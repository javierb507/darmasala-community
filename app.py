from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os
from utils.calendar_utils import (
    CalendarioAcademico,
    PeriodoPago,
    HorarioSemanalHelper,
    crear_contexto_calendario
)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Modelo de Alumno
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.Text)
    condiciones_medicas = db.Column(db.Text)
    tipo_cuota = db.Column(db.String(30), nullable=False, default='1_clase_semanal')  # 1_clase_semanal, 2_clases_semanal, 3_clases_semanal, plana, 1_clase_bimensual, 2_clases_bimensual
    matricula_pagada = db.Column(db.Boolean, default=False)
    fecha_matricula = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    pagos = db.relationship('Pago', backref='alumno', lazy=True)
    cliente = db.relationship('Cliente', backref='alumno', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<Alumno {self.nombre} {self.apellido}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'dni': self.dni,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'direccion': self.direccion,
            'condiciones_medicas': self.condiciones_medicas,
            'tipo_cuota': self.tipo_cuota,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def get_tipo_cuota_display(self):
        tipos = {
            'clase_suelta': 'Clase suelta',
            '1_clase_semanal': '1 clase por semana',
            '2_clases_semanal': '2 clases por semana', 
            'plana': 'Tarifa plana',
            '1_clase_bimensual': '1 clase bimensual',
            '2_clases_bimensual': '2 clases bimensual'
        }
        return tipos.get(self.tipo_cuota, self.tipo_cuota)
    
    def get_precio_cuota(self):
        """Obtiene el precio de la cuota según el tipo"""
        precios = {
            'clase_suelta': 15.00,
            '1_clase_semanal': 40.00,
            '2_clases_semanal': 70.00,
            'plana': 90.00,
            '1_clase_bimensual': 75.00,
            '2_clases_bimensual': 135.00
        }
        return precios.get(self.tipo_cuota, 40.00)

# Modelo de Pago
class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    mes = db.Column(db.String(7), nullable=True)  # Formato: YYYY-MM (null para matrícula)
    año = db.Column(db.Integer, nullable=True)  # Año para matrícula
    monto = db.Column(db.Float, nullable=False)
    tipo_pago = db.Column(db.String(20), default='cuota')  # cuota, matricula, clase_suelta
    descripcion = db.Column(db.String(100))  # Descripción del pago
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago {self.mes} - {self.monto}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'alumno_id': self.alumno_id,
            'mes': self.mes,
            'año': self.año,
            'monto': self.monto,
            'tipo_pago': self.tipo_pago,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

# Modelo de Clase
class Clase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7), default='#4ECDC4')  # Color hexadecimal para el calendario
    activa = db.Column(db.Boolean, default=True)
    duracion_minutos = db.Column(db.Integer, default=75)  # Duración por defecto de la clase
    periodicidad = db.Column(db.String(50), default='semanal')  # semanal, quincenal, mensual

    def __repr__(self):
        return f'<Clase {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color,
            'activa': self.activa,
            'duracion_minutos': self.duracion_minutos,
            'periodicidad': self.periodicidad
        }

# Modelo de Horario Semanal
class HorarioSemanal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    instructor = db.Column(db.String(50), default='Minouche')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con clase
    clase = db.relationship('Clase', backref='horarios')
    
    def __repr__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f'<Horario {dias[self.dia_semana]} {self.hora_inicio} - {self.hora_fin}>'
    
    def get_dia_display(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[self.dia_semana]
    
    def to_dict(self):
        return {
            'id': self.id,
            'clase_id': self.clase_id,
            'clase_nombre': self.clase.nombre,
            'dia_semana': self.dia_semana,
            'dia_display': self.get_dia_display(),
            'hora_inicio': self.hora_inicio.strftime('%H:%M'),
            'hora_fin': self.hora_fin.strftime('%H:%M'),
            'instructor': self.instructor,
            'activo': self.activo
        }

# Modelo de Asistencia
class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario_semanal.id'), nullable=True)  # Nullable para clases individuales
    evento_id = db.Column(db.Integer, db.ForeignKey('evento_calendario.id'), nullable=True)  # Para eventos individuales
    fecha_clase = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    alumno = db.relationship('Alumno', backref='asistencias')
    horario = db.relationship('HorarioSemanal', backref='asistencias')

    def __repr__(self):
        return f'<Asistencia {self.alumno.nombre} - {self.fecha_clase}>'

    def to_dict(self):
        return {
            'id': self.id,
            'alumno_id': self.alumno_id,
            'alumno_nombre': f"{self.alumno.nombre} {self.alumno.apellido}",
            'horario_id': self.horario_id,
            'clase_nombre': self.horario.clase.nombre if self.horario else 'Clase Individual',
            'dia_display': self.horario.get_dia_display() if self.horario else '',
            'fecha_clase': self.fecha_clase.isoformat(),
            'presente': self.presente,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat()
        }

# Modelo de Evento de Calendario (para clases individuales y eventos especiales)
class EventoCalendario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=True)  # Para clases individuales
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(50), default='individual')  # individual, evento_especial, taller, etc
    color = db.Column(db.String(7), default='#8B5FBF')  # Color en formato hex
    instructor = db.Column(db.String(50), default='Minouche')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    clase = db.relationship('Clase', backref='eventos')
    alumno = db.relationship('Alumno', backref='eventos_individuales')
    asistencias = db.relationship('Asistencia', backref='evento', lazy=True)

    def __repr__(self):
        return f'<EventoCalendario {self.titulo} - {self.fecha_inicio}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.titulo,
            'description': self.descripcion,
            'start': self.fecha_inicio.isoformat(),
            'end': self.fecha_fin.isoformat(),
            'className': self.clase.nombre if self.clase else 'Individual',
            'alumno': f"{self.alumno.nombre} {self.alumno.apellido}" if self.alumno else None,
            'tipo': self.tipo,
            'color': self.color,
            'instructor': self.instructor
        }

# Modelo de Configuración
class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracion {self.clave}: {self.valor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat()
        }

# Modelo de Tarifa Personalizada
class Tarifa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tarifa {self.nombre}: €{self.precio}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'activa': self.activa
        }

# MODELOS PARA FACTURACIÓN (Facturas emitidas a clientes)

# Modelo de Cliente (para facturas emitidas)
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    nif_cif = db.Column(db.String(20), nullable=False, unique=True)
    direccion = db.Column(db.Text, nullable=False)
    codigo_postal = db.Column(db.String(10))
    ciudad = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    pais = db.Column(db.String(100), default='España')
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    tipo_cliente = db.Column(db.String(20), default='particular')  # particular, empresa, autonomo
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)

    # Relación con alumno (opcional)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'))

    # Relaciones
    facturas = db.relationship('FacturaEmitida', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nombre} - {self.nif_cif}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nif_cif': self.nif_cif,
            'direccion': self.direccion,
            'codigo_postal': self.codigo_postal,
            'ciudad': self.ciudad,
            'provincia': self.provincia,
            'email': self.email,
            'telefono': self.telefono,
            'tipo_cliente': self.tipo_cliente
        }

# Modelo de Configuración Fiscal del Negocio
class ConfiguracionFiscal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(200), nullable=False)
    nif = db.Column(db.String(20), nullable=False)
    direccion_fiscal = db.Column(db.Text, nullable=False)
    codigo_postal = db.Column(db.String(10))
    ciudad = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    epigrafe_iae = db.Column(db.String(10))  # Epígrafe IAE
    regimen_iva = db.Column(db.String(50), default='general')  # general, recargo_equivalencia, exento
    tipo_retencion_default = db.Column(db.Float, default=7.0)  # 7% o 15% según actividad
    exento_iva = db.Column(db.Boolean, default=True)  # Exención art. 20 Ley 37/1992
    texto_exencion_iva = db.Column(db.Text, default='Exento de IVA según art. 20.Uno.9º de la Ley 37/1992')
    logo_factura = db.Column(db.String(200))  # Ruta al logo
    pie_factura = db.Column(db.Text)  # Texto legal adicional
    serie_factura_default = db.Column(db.String(10), default='A')
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ConfiguracionFiscal {self.nombre_empresa}>'

# Modelo de Factura Emitida
class FacturaEmitida(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Numeración
    serie = db.Column(db.String(10), nullable=False, default='A')
    numero = db.Column(db.Integer, nullable=False)
    numero_completo = db.Column(db.String(50), nullable=False, unique=True)  # Ej: A/2025/001

    # Fechas
    fecha_emision = db.Column(db.Date, nullable=False, default=date.today)
    fecha_prestacion = db.Column(db.Date, nullable=False, default=date.today)
    fecha_vencimiento = db.Column(db.Date)

    # Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    # Importes
    base_imponible = db.Column(db.Float, nullable=False)
    tipo_iva = db.Column(db.Float, default=0.0)  # 0% si exento, 21% si no
    cuota_iva = db.Column(db.Float, default=0.0)
    tipo_retencion = db.Column(db.Float, default=0.0)  # 0%, 7% o 15%
    cuota_retencion = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)

    # Exenciones
    exenta_iva = db.Column(db.Boolean, default=True)
    motivo_exencion = db.Column(db.Text)

    # Estado y pago
    estado = db.Column(db.String(20), default='emitida')  # emitida, pagada, parcialmente_pagada, vencida, anulada
    fecha_pago = db.Column(db.Date)
    metodo_pago = db.Column(db.String(50))  # transferencia, efectivo, tarjeta, domiciliacion

    # Información adicional
    observaciones = db.Column(db.Text)
    notas_internas = db.Column(db.Text)
    archivo_pdf = db.Column(db.String(200))  # Ruta al PDF generado

    # Control
    enviada_cliente = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.DateTime)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Factura rectificativa
    es_rectificativa = db.Column(db.Boolean, default=False)
    factura_origen_id = db.Column(db.Integer, db.ForeignKey('factura_emitida.id'))
    motivo_rectificacion = db.Column(db.Text)

    # Relaciones
    lineas = db.relationship('LineaFactura', backref='factura', lazy=True, cascade='all, delete-orphan')
    facturas_rectificativas = db.relationship('FacturaEmitida',
                                              backref=db.backref('factura_origen', remote_side=[id]),
                                              lazy=True)

    def __repr__(self):
        return f'<FacturaEmitida {self.numero_completo}>'

    def calcular_totales(self):
        """Calcula los totales de la factura basándose en sus líneas"""
        self.base_imponible = sum(linea.subtotal for linea in self.lineas)

        if self.exenta_iva:
            self.tipo_iva = 0.0
            self.cuota_iva = 0.0
        else:
            self.cuota_iva = self.base_imponible * (self.tipo_iva / 100)

        if self.tipo_retencion > 0:
            self.cuota_retencion = self.base_imponible * (self.tipo_retencion / 100)
        else:
            self.cuota_retencion = 0.0

        self.total = self.base_imponible + self.cuota_iva - self.cuota_retencion

    def generar_numero_factura(self):
        """Genera el número de factura correlativo según la serie"""
        año_factura = self.fecha_emision.year if self.fecha_emision else date.today().year

        # Buscar el último número de la serie en el año de la factura
        ultima_factura = FacturaEmitida.query.filter(
            FacturaEmitida.serie == self.serie,
            db.extract('year', FacturaEmitida.fecha_emision) == año_factura,
            FacturaEmitida.es_rectificativa == False
        ).order_by(FacturaEmitida.numero.desc()).first()

        if ultima_factura:
            self.numero = ultima_factura.numero + 1
        else:
            self.numero = 1

        self.numero_completo = f"{self.serie}/{año_factura}/{self.numero:04d}"

    def to_dict(self):
        return {
            'id': self.id,
            'numero_completo': self.numero_completo,
            'fecha_emision': self.fecha_emision.isoformat(),
            'cliente': self.cliente.to_dict() if self.cliente else None,
            'base_imponible': self.base_imponible,
            'cuota_iva': self.cuota_iva,
            'cuota_retencion': self.cuota_retencion,
            'total': self.total,
            'estado': self.estado
        }

# Modelo de Línea de Factura
class LineaFactura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('factura_emitida.id'), nullable=False)
    orden = db.Column(db.Integer, default=0)  # Para mantener el orden de las líneas

    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Float, default=1.0)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    # Referencias opcionales
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'))
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'))
    tarifa_id = db.Column(db.Integer, db.ForeignKey('tarifa.id'))

    def __repr__(self):
        return f'<LineaFactura {self.descripcion} - €{self.subtotal}>'

    def calcular_subtotal(self):
        """Calcula el subtotal de la línea"""
        self.subtotal = self.cantidad * self.precio_unitario

# MODELOS PARA GESTIÓN ECONÓMICA

# Modelo de Proveedor
class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cif_nif = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    contacto_principal = db.Column(db.String(100))
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    facturas = db.relationship('FacturaProveedor', backref='proveedor', lazy=True)
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

# Modelo de Categoría de Gastos
class CategoriaGasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#6c757d')  # Color hex para visualización
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    facturas = db.relationship('FacturaProveedor', backref='categoria', lazy=True)
    gastos_fijos = db.relationship('GastoFijo', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<CategoriaGasto {self.nombre}>'

# Modelo de Factura de Proveedor
class FacturaProveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_gasto.id'), nullable=False)
    fecha_factura = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    importe_sin_iva = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=21.0)  # Porcentaje de IVA
    importe_total = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, vencida
    fecha_pago = db.Column(db.Date)
    metodo_pago = db.Column(db.String(50))  # transferencia, efectivo, tarjeta, etc.
    notas = db.Column(db.Text)
    archivo_factura = db.Column(db.String(200))  # Ruta al archivo PDF/imagen
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calcular_total(self):
        """Calcula el importe total con IVA"""
        return self.importe_sin_iva * (1 + self.iva / 100)
    
    def esta_vencida(self):
        """Verifica si la factura está vencida"""
        if self.fecha_vencimiento and self.estado == 'pendiente':
            return date.today() > self.fecha_vencimiento
        return False
    
    def __repr__(self):
        return f'<FacturaProveedor {self.numero_factura} - {self.proveedor.nombre}>'

# Modelo de Gasto Fijo (Recurrente)
class GastoFijo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))  # Proveedor asociado
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_gasto.id'), nullable=False)
    importe = db.Column(db.Float, nullable=False)
    frecuencia = db.Column(db.String(20), default='mensual')  # mensual, trimestral, anual
    dia_cargo = db.Column(db.Integer, default=1)  # Día del mes para el cargo
    activo = db.Column(db.Boolean, default=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)  # Opcional, para gastos temporales
    notas = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def get_importe_anual(self):
        """Calcula el importe anual según la frecuencia"""
        if self.frecuencia == 'mensual':
            return self.importe * 12
        elif self.frecuencia == 'trimestral':
            return self.importe * 4
        elif self.frecuencia == 'anual':
            return self.importe
        return 0

    def __repr__(self):
        return f'<GastoFijo {self.nombre} - {self.importe}€/{self.frecuencia}>'

# Modelo de Ingreso
class Ingreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concepto = db.Column(db.String(200), nullable=False)
    importe = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), default='cuota')  # cuota, matricula, clase_suelta, otros
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'))  # Opcional, para vincular con alumnos
    pago_id = db.Column(db.Integer, db.ForeignKey('pago.id'))  # Opcional, para vincular con pagos
    metodo_pago = db.Column(db.String(50))  # efectivo, transferencia, tarjeta
    notas = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Ingreso {self.concepto} - {self.importe}€>'

# Context Processor para hacer disponibles las utilidades de calendario en todos los templates
@app.context_processor
def inject_calendar_utils():
    """Inyecta utilidades de calendario en todos los templates."""
    return crear_contexto_calendario()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    # Mostrar solo alumnos activos
    alumnos_activos = Alumno.query.filter_by(activo=True).all()
    return render_template('alumnos.html', alumnos=alumnos_activos)

@app.route('/alumnos/desactivados')
def alumnos_desactivados():
    # Mostrar solo alumnos desactivados
    alumnos_inactivos = Alumno.query.filter_by(activo=False).all()
    current_year = date.today().year
    return render_template('alumnos_desactivados.html', 
                         alumnos=alumnos_inactivos,
                         current_year=current_year)

@app.route('/alumnos/nuevo', methods=['GET', 'POST'])
def nuevo_alumno():
    if request.method == 'POST':
                try:
                    matricula_pagada = 'matricula_pagada' in request.form
                    fecha_matricula = date.today() if matricula_pagada else None
                    
                    alumno = Alumno(
                        nombre=request.form['nombre'],
                        apellido=request.form['apellido'],
                        dni=request.form.get('dni'),
                        email=request.form['email'],
                        telefono=request.form.get('telefono'),
                        fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None,
                        direccion=request.form.get('direccion'),
                        condiciones_medicas=request.form.get('condiciones_medicas'),
                        tipo_cuota=request.form.get('tipo_cuota', '1_clase_semanal'),
                        matricula_pagada=matricula_pagada,
                        fecha_matricula=fecha_matricula
                    )
                    db.session.add(alumno)
                    db.session.commit()
                    flash('¡Alumno registrado exitosamente!', 'success')
                    return redirect(url_for('alumnos'))
                except Exception as e:
                    flash(f'Error al registrar alumno: {str(e)}', 'error')
                    db.session.rollback()
    
    return render_template('nuevo_alumno.html')

@app.route('/alumnos/<int:alumno_id>')
def ver_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    pagos = Pago.query.filter_by(alumno_id=alumno_id).order_by(Pago.mes.desc()).all()

    # Obtener asistencias del alumno (últimos 90 días)
    from datetime import timedelta
    fecha_inicio = date.today() - timedelta(days=90)
    asistencias = Asistencia.query.filter(
        Asistencia.alumno_id == alumno_id,
        Asistencia.fecha_clase >= fecha_inicio
    ).order_by(Asistencia.fecha_clase.desc()).all()

    # Calcular estadísticas de asistencia
    total_asistencias = len(asistencias)
    asistencias_presente = sum(1 for a in asistencias if a.presente)
    asistencias_ausente = total_asistencias - asistencias_presente
    porcentaje_asistencia = (asistencias_presente / total_asistencias * 100) if total_asistencias > 0 else 0

    # Asistencias por mes (últimos 3 meses)
    asistencias_por_mes = {}
    for asistencia in asistencias:
        mes_key = asistencia.fecha_clase.strftime('%Y-%m')
        if mes_key not in asistencias_por_mes:
            asistencias_por_mes[mes_key] = {'total': 0, 'presente': 0}
        asistencias_por_mes[mes_key]['total'] += 1
        if asistencia.presente:
            asistencias_por_mes[mes_key]['presente'] += 1

    return render_template('ver_alumno.html',
                         alumno=alumno,
                         pagos=pagos,
                         asistencias=asistencias,
                         total_asistencias=total_asistencias,
                         asistencias_presente=asistencias_presente,
                         asistencias_ausente=asistencias_ausente,
                         porcentaje_asistencia=porcentaje_asistencia,
                         asistencias_por_mes=asistencias_por_mes)

@app.route('/alumnos/<int:alumno_id>/editar', methods=['GET', 'POST'])
def editar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
            alumno.dni = request.form.get('dni')
            alumno.email = request.form['email']
            alumno.telefono = request.form.get('telefono')
            alumno.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None
            alumno.direccion = request.form.get('direccion')
            alumno.condiciones_medicas = request.form.get('condiciones_medicas')
            alumno.tipo_cuota = request.form.get('tipo_cuota', '1_clase')
            
            db.session.commit()
            flash('¡Alumno actualizado exitosamente!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno.id))
        except Exception as e:
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_alumno.html', alumno=alumno)

@app.route('/alumnos/<int:alumno_id>/eliminar', methods=['GET', 'POST'])
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if request.method == 'POST':
        alumno.activo = False
        db.session.commit()
        flash('¡Alumno desactivado exitosamente!', 'success')
        return redirect(url_for('alumnos'))
    else:
        # Confirmación GET - mostrar página de confirmación o redirigir
        if request.args.get('confirm') == '1':
            alumno.activo = False
            db.session.commit()
            flash('¡Alumno desactivado exitosamente!', 'success')
            return redirect(url_for('alumnos'))
        else:
            # Redirigir a la lista con confirmación JavaScript
            flash('Confirma la desactivación del alumno.', 'warning')
            return redirect(url_for('alumnos'))

@app.route('/alumnos/<int:alumno_id>/reactivar', methods=['POST'])
def reactivar_alumno(alumno_id):
    try:
        alumno = Alumno.query.get_or_404(alumno_id)
        alumno.activo = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alumno reactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Rutas para Pagos
@app.route('/alumnos/<int:alumno_id>/pago', methods=['GET', 'POST'])
def agregar_pago(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)

    if request.method == 'POST':
        try:
            tipo_pago = request.form['tipo_pago']
            monto = float(request.form['monto'])
            
            # Manejar mes y año según el tipo de pago
            mes = request.form.get('mes') if tipo_pago != 'matricula' else None
            año = request.form.get('año') if tipo_pago == 'matricula' else None
            
            # Crear descripción según el tipo de pago
            descripciones = {
                'cuota': f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                'matricula': f'Matrícula anual {año}',
                'clase_suelta': 'Clase suelta'
            }
            
            pago = Pago(
                alumno_id=alumno_id,
                mes=mes,
                año=int(año) if año else None,
                monto=monto,
                tipo_pago=tipo_pago,
                descripcion=descripciones.get(tipo_pago, 'Pago')
            )
            db.session.add(pago)
            
            # Si es matrícula, marcar al alumno como que pagó la matrícula
            if tipo_pago == 'matricula':
                alumno.matricula_pagada = True
                alumno.fecha_matricula = date.today()
            
            db.session.commit()
            flash('¡Pago registrado exitosamente!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno_id))
        except Exception as e:
            flash(f'Error al registrar pago: {str(e)}', 'error')
            db.session.rollback()

    return render_template('agregar_pago.html', alumno=alumno)

# Rutas para Clases
@app.route('/clases')
def clases():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases.html', clases=clases)

@app.route('/horarios')
def horarios():
    # Obtener todos los horarios activos
    horarios_list = HorarioSemanal.query.filter_by(activo=True).order_by(
        HorarioSemanal.dia_semana,
        HorarioSemanal.hora_inicio
    ).all()

    # Obtener todas las clases
    clases = Clase.query.filter_by(activa=True).all()

    # Calcular estadísticas de periodicidad
    clases_periodicidad = {
        'semanal': Clase.query.filter_by(activa=True, periodicidad='semanal').count(),
        'quincenal': Clase.query.filter_by(activa=True, periodicidad='quincenal').count(),
        'mensual': Clase.query.filter_by(activa=True, periodicidad='mensual').count()
    }

    # Calcular total de horas semanales
    total_horas_semanales = 0
    for horario in horarios_list:
        duracion_horas = horario.clase.duracion_minutos / 60.0
        total_horas_semanales += duracion_horas
    total_horas_semanales = round(total_horas_semanales, 1)

    return render_template('horarios.html',
                         horarios=horarios_list,
                         clases=clases,
                         clases_periodicidad=clases_periodicidad,
                         total_horas_semanales=total_horas_semanales)

@app.route('/horarios/nuevo', methods=['GET', 'POST'])
def nuevo_horario():
    if request.method == 'POST':
        try:
            clase_id = int(request.form['clase_id'])
            dia_semana = int(request.form['dia_semana'])
            hora_inicio_str = request.form['hora_inicio']
            hora_fin_str = request.form['hora_fin']
            instructor = request.form.get('instructor', 'Minouche')

            # Convertir horas de string a time
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

            # Crear el horario
            horario = HorarioSemanal(
                clase_id=clase_id,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                instructor=instructor
            )

            db.session.add(horario)
            db.session.commit()

            flash('Horario creado exitosamente!', 'success')
            return redirect(url_for('horarios'))

        except Exception as e:
            flash(f'Error al crear el horario: {str(e)}', 'danger')
            db.session.rollback()
            return redirect(url_for('horarios'))

    # Para GET, simplemente redirigir a horarios (el modal está en esa página)
    return redirect(url_for('horarios'))

@app.route('/horarios/<int:horario_id>/eliminar', methods=['POST'])
def eliminar_horario(horario_id):
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        horario.activo = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/asistencias')
def asistencias():
    # Redirigir a la vista de calendario centralizado
    return redirect(url_for('calendario'))

@app.route('/asistencias/registrar', methods=['GET', 'POST'])
def registrar_asistencia():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            alumno_id = int(request.form['alumno_id'])
            horario_id = int(request.form['horario_id'])
            fecha_clase = CalendarioAcademico.parsear_fecha(request.form['fecha_clase'], 'iso')
            presente = 'presente' in request.form
            observaciones = request.form.get('observaciones', '')
            
            # Verificar si ya existe una asistencia para este alumno en esta clase y fecha
            asistencia_existente = Asistencia.query.filter_by(
                alumno_id=alumno_id,
                horario_id=horario_id,
                fecha_clase=fecha_clase
            ).first()
            
            if asistencia_existente:
                # Actualizar asistencia existente
                asistencia_existente.presente = presente
                asistencia_existente.observaciones = observaciones
            else:
                # Crear nueva asistencia
                asistencia = Asistencia(
                    alumno_id=alumno_id,
                    horario_id=horario_id,
                    fecha_clase=fecha_clase,
                    presente=presente,
                    observaciones=observaciones
                )
                db.session.add(asistencia)
            
            db.session.commit()
            flash('¡Asistencia registrada exitosamente!', 'success')
            return redirect(url_for('calendario'))
        except Exception as e:
            flash(f'Error al registrar asistencia: {str(e)}', 'error')
            db.session.rollback()
    
    # Obtener datos para el formulario
    alumnos = Alumno.query.filter_by(activo=True).all()
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    
    return render_template('registrar_asistencia.html', alumnos=alumnos, horarios=horarios)

@app.route('/reportes/asistencia')
def reporte_asistencia():
    # Obtener parámetros de filtro
    alumno_id = request.args.get('alumno_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    # Construir consulta
    query = Asistencia.query
    
    if alumno_id:
        query = query.filter_by(alumno_id=alumno_id)
    
    if fecha_desde:
        query = query.filter(Asistencia.fecha_clase >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())
    
    if fecha_hasta:
        query = query.filter(Asistencia.fecha_clase <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())
    
    asistencias = query.order_by(Asistencia.fecha_clase.desc()).all()
    alumnos = Alumno.query.filter_by(activo=True).all()
    
    return render_template('reporte_asistencia.html', asistencias=asistencias, alumnos=alumnos,
                         alumno_id=alumno_id, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)

# Función para inicializar las clases básicas
def inicializar_clases():
    clases_basicas = [
        {'nombre': 'Yoga menopausia', 'descripcion': 'Clase especializada para mujeres en etapa de menopausia'},
        {'nombre': 'Yoga integral', 'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación'},
        {'nombre': 'Yoga embarazadas', 'descripcion': 'Yoga adaptado para mujeres embarazadas'},
        {'nombre': 'Meditación', 'descripcion': 'Práctica de meditación y mindfulness'}
    ]
    
    for clase_data in clases_basicas:
        clase_existente = Clase.query.filter_by(nombre=clase_data['nombre']).first()
        if not clase_existente:
            clase = Clase(
                nombre=clase_data['nombre'],
                descripcion=clase_data['descripcion']
            )
            db.session.add(clase)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar clases: {e}")

# Función para crear datos de prueba
def inicializar_categorias_gastos():
    """Inicializar categorías de gastos predeterminadas"""
    categorias_default = [
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'color': '#dc3545'},
        {'nombre': 'Suministros', 'descripcion': 'Luz, agua, gas, internet', 'color': '#ffc107'},
        {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, material de yoga', 'color': '#28a745'},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción', 'color': '#007bff'},
        {'nombre': 'Formación', 'descripcion': 'Cursos y certificaciones', 'color': '#6f42c1'},
        {'nombre': 'Seguros', 'descripcion': 'Seguros de responsabilidad civil', 'color': '#fd7e14'},
        {'nombre': 'Mantenimiento', 'descripcion': 'Limpieza y mantenimiento', 'color': '#20c997'},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'color': '#6c757d'}
    ]
    
    try:
        for cat_data in categorias_default:
            categoria_existente = CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria_existente:
                categoria = CategoriaGasto(**cat_data)
                db.session.add(categoria)
        
        db.session.commit()
        print("✅ Categorías de gastos inicializadas")
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar categorías: {e}")

def crear_datos_prueba():
    import random
    from datetime import date, timedelta, datetime
    
    # Verificar si ya existen datos
    if Alumno.query.count() > 0:
        return
    
    # Crear 10 alumnos de prueba
    nombres = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Sofia', 'Patricia', 'Rosa', 'Mónica']
    apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín']
    current_year = date.today().year
    
    for i in range(10):
        # Crear alumno
        matricula_pagada = random.choice([True, False])
        alumno = Alumno(
            nombre=random.choice(nombres),
            apellido=random.choice(apellidos),
            email=f"alumno{i+1}@test.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1960 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja'])} {random.randint(1, 100)}",
            condiciones_medicas=random.choice(['Ninguna', 'Hipertensión', 'Diabetes', 'Problemas de espalda', '']),
            tipo_cuota=random.choice(['1_clase_semanal', '2_clases_semanal', '3_clases_semanal', '1_clase_bimensual', '2_clases_bimensual']),
            matricula_pagada=matricula_pagada,
            fecha_matricula=date.today() - timedelta(days=random.randint(1, 365)) if matricula_pagada else None
        )
        db.session.add(alumno)
        db.session.flush()  # Para obtener el ID del alumno
        
        # Crear pagos de meses pasados (algunos pagados, otros no)
        meses_pagados = random.sample(range(1, 13), random.randint(3, 8))  # Entre 3 y 8 meses pagados
        
        for mes in range(1, 13):
            if mes in meses_pagados:
                # Crear pago de cuota mensual
                pago = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                    fecha_creacion=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(pago)
        
        # Crear pago de matrícula si está pagada
        if matricula_pagada:
            pago_matricula = Pago(
                alumno_id=alumno.id,
                año=current_year,
                monto=25.00,
                tipo_pago='matricula',
                descripcion=f'Matrícula anual {current_year}',
                fecha_creacion=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            db.session.add(pago_matricula)
    
    try:
        db.session.commit()
        print("✅ Datos de prueba creados exitosamente con pagos históricos")
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear datos de prueba: {e}")

# Rutas para Configuración
@app.route('/configuracion')
def configuracion():
    configuraciones = Configuracion.query.all()
    config_dict = {config.clave: config.valor for config in configuraciones}
    clases = Clase.query.all()
    tarifas = Tarifa.query.all()
    return render_template('configuracion.html', config=config_dict, clases=clases, tarifas=tarifas)

@app.route('/configuracion/guardar', methods=['POST'])
def guardar_configuracion():
    try:
        configuraciones = [
            # Tarifas
            ('precio_clase_suelta', request.form.get('precio_clase_suelta', '15.00'), 'Precio por clase suelta'),
            ('precio_1_clase_semanal', request.form.get('precio_1_clase_semanal', '40.00'), 'Precio 1 clase por semana'),
            ('precio_2_clases_semanal', request.form.get('precio_2_clases_semanal', '70.00'), 'Precio 2 clases por semana'),
            ('precio_tarifa_plana', request.form.get('precio_tarifa_plana', '90.00'), 'Precio tarifa plana'),
            ('precio_1_clase_bimensual', request.form.get('precio_1_clase_bimensual', '75.00'), 'Precio 1 clase bimensual'),
            ('precio_2_clases_bimensual', request.form.get('precio_2_clases_bimensual', '135.00'), 'Precio 2 clases bimensual'),
            ('precio_matricula', request.form.get('precio_matricula', '25.00'), 'Precio de matrícula anual'),
            
            # Información de la escuela
            ('direccion_escuela', request.form.get('direccion_escuela', ''), 'Dirección de la escuela'),
            ('numero_cuenta', request.form.get('numero_cuenta', ''), 'Número de cuenta bancaria'),
            ('nombre_instructora', request.form.get('nombre_instructora', 'Minouche'), 'Nombre de la instructora'),
            ('telefono_escuela', request.form.get('telefono_escuela', ''), 'Teléfono de contacto'),
            ('email_escuela', request.form.get('email_escuela', ''), 'Email de contacto')
        ]
        
        for clave, valor, descripcion in configuraciones:
            config_existente = Configuracion.query.filter_by(clave=clave).first()
            if config_existente:
                config_existente.valor = valor
                config_existente.descripcion = descripcion
                config_existente.fecha_actualizacion = datetime.utcnow()
            else:
                nueva_config = Configuracion(
                    clave=clave,
                    valor=valor,
                    descripcion=descripcion
                )
                db.session.add(nueva_config)
        
        db.session.commit()
        flash('¡Configuración guardada exitosamente!', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al guardar configuración: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

# Rutas para gestión de tipos de clases
@app.route('/configuracion/clases/nueva', methods=['POST'])
def nueva_clase():
    try:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        color = request.form.get('color', '#6c757d')

        if not nombre:
            flash('El nombre de la clase es obligatorio', 'error')
            return redirect(url_for('configuracion'))

        # Verificar si ya existe una clase con ese nombre
        clase_existente = Clase.query.filter_by(nombre=nombre).first()
        if clase_existente:
            flash(f'Ya existe una clase con el nombre "{nombre}"', 'error')
            return redirect(url_for('configuracion'))

        duracion_minutos = request.form.get('duracion_minutos', 75, type=int)
        periodicidad = request.form.get('periodicidad', 'semanal')

        nueva_clase = Clase(
            nombre=nombre,
            descripcion=descripcion,
            color=color,
            duracion_minutos=duracion_minutos,
            periodicidad=periodicidad,
            activa=True
        )
        db.session.add(nueva_clase)
        db.session.commit()

        flash(f'Clase "{nombre}" creada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al crear la clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/clases/<int:clase_id>/editar', methods=['POST'])
def editar_clase(clase_id):
    try:
        clase = Clase.query.get_or_404(clase_id)

        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')

        if not nombre:
            flash('El nombre de la clase es obligatorio', 'error')
            return redirect(url_for('configuracion'))

        # Verificar si ya existe otra clase con ese nombre
        clase_existente = Clase.query.filter(
            Clase.nombre == nombre,
            Clase.id != clase_id
        ).first()
        if clase_existente:
            flash(f'Ya existe otra clase con el nombre "{nombre}"', 'error')
            return redirect(url_for('configuracion'))

        clase.nombre = nombre
        clase.descripcion = descripcion
        clase.color = request.form.get('color', '#4ECDC4')
        clase.duracion_minutos = request.form.get('duracion_minutos', 75, type=int)
        clase.periodicidad = request.form.get('periodicidad', 'semanal')
        db.session.commit()

        flash(f'Clase "{nombre}" actualizada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al actualizar la clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/clases/<int:clase_id>/toggle', methods=['POST'])
def toggle_clase(clase_id):
    try:
        clase = Clase.query.get_or_404(clase_id)
        clase.activa = not clase.activa
        db.session.commit()

        estado = 'activada' if clase.activa else 'desactivada'
        flash(f'Clase "{clase.nombre}" {estado} exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al cambiar el estado de la clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/clases/<int:clase_id>/eliminar', methods=['POST'])
def eliminar_clase(clase_id):
    try:
        clase = Clase.query.get_or_404(clase_id)

        # Verificar si tiene horarios asociados
        if clase.horarios:
            flash(f'No se puede eliminar la clase "{clase.nombre}" porque tiene horarios asociados', 'error')
            return redirect(url_for('configuracion'))

        nombre = clase.nombre
        db.session.delete(clase)
        db.session.commit()

        flash(f'Clase "{nombre}" eliminada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al eliminar la clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

# Rutas para Tarifas Personalizadas
@app.route('/configuracion/tarifas/nueva', methods=['POST'])
def nueva_tarifa():
    try:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = request.form.get('precio')

        if not nombre or not precio:
            flash('El nombre y el precio son obligatorios', 'error')
            return redirect(url_for('configuracion'))

        # Verificar si ya existe una tarifa con ese nombre
        tarifa_existente = Tarifa.query.filter_by(nombre=nombre).first()
        if tarifa_existente:
            flash(f'Ya existe una tarifa con el nombre "{nombre}"', 'error')
            return redirect(url_for('configuracion'))

        nueva_tarifa = Tarifa(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            activa=True
        )
        db.session.add(nueva_tarifa)
        db.session.commit()

        flash(f'Tarifa "{nombre}" creada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al crear la tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/tarifas/<int:tarifa_id>/editar', methods=['POST'])
def editar_tarifa(tarifa_id):
    try:
        tarifa = Tarifa.query.get_or_404(tarifa_id)

        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = request.form.get('precio')

        if not nombre or not precio:
            flash('El nombre y el precio son obligatorios', 'error')
            return redirect(url_for('configuracion'))

        # Verificar si ya existe otra tarifa con ese nombre
        tarifa_existente = Tarifa.query.filter(
            Tarifa.nombre == nombre,
            Tarifa.id != tarifa_id
        ).first()
        if tarifa_existente:
            flash(f'Ya existe otra tarifa con el nombre "{nombre}"', 'error')
            return redirect(url_for('configuracion'))

        tarifa.nombre = nombre
        tarifa.descripcion = descripcion
        tarifa.precio = float(precio)
        db.session.commit()

        flash(f'Tarifa "{nombre}" actualizada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al actualizar la tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/tarifas/<int:tarifa_id>/toggle', methods=['POST'])
def toggle_tarifa(tarifa_id):
    try:
        tarifa = Tarifa.query.get_or_404(tarifa_id)
        tarifa.activa = not tarifa.activa
        db.session.commit()

        estado = 'activada' if tarifa.activa else 'desactivada'
        flash(f'Tarifa "{tarifa.nombre}" {estado} exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al cambiar el estado de la tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

@app.route('/configuracion/tarifas/<int:tarifa_id>/eliminar', methods=['POST'])
def eliminar_tarifa(tarifa_id):
    try:
        tarifa = Tarifa.query.get_or_404(tarifa_id)

        nombre = tarifa.nombre
        db.session.delete(tarifa)
        db.session.commit()

        flash(f'Tarifa "{nombre}" eliminada exitosamente', 'success')
        return redirect(url_for('configuracion'))
    except Exception as e:
        flash(f'Error al eliminar la tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('configuracion'))

# RUTAS PARA MODO DE PRUEBAS (ADMINISTRADOR)

@app.route('/modo-pruebas')
def modo_pruebas():
    """Página de gestión de datos de prueba"""
    stats = {
        'alumnos': Alumno.query.count(),
        'horarios': HorarioSemanal.query.count(),
        'asistencias': Asistencia.query.count(),
        'facturas_emitidas': FacturaEmitida.query.count(),
        'facturas_proveedores': FacturaProveedor.query.count(),
        'clientes': Cliente.query.count(),
        'proveedores': Proveedor.query.count(),
        'gastos_fijos': GastoFijo.query.count()
    }
    return render_template('modo_pruebas.html', stats=stats)

@app.route('/cargar-datos-prueba', methods=['POST'])
def cargar_datos_prueba():
    """Carga datos de prueba completos en el sistema"""
    try:
        from cargar_datos_prueba_completos import cargar_datos_completos

        # Cargar todos los datos de prueba
        cargar_datos_completos(modo_web=True)

        flash('¡Datos de prueba cargados exitosamente!', 'success')
    except Exception as e:
        flash(f'Error al cargar datos de prueba: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('modo_pruebas'))

@app.route('/resetear-sistema', methods=['POST'])
def resetear_sistema():
    """Resetea todos los datos del sistema (excepto configuración base)"""
    try:
        # Eliminar en orden para respetar foreign keys
        print("Eliminando datos del sistema...")

        # Asistencias
        Asistencia.query.delete()
        print("- Asistencias eliminadas")

        # Líneas de facturas
        LineaFactura.query.delete()
        print("- Líneas de factura eliminadas")

        # Facturas emitidas
        FacturaEmitida.query.delete()
        print("- Facturas emitidas eliminadas")

        # Clientes
        Cliente.query.delete()
        print("- Clientes eliminados")

        # Facturas de proveedores
        FacturaProveedor.query.delete()
        print("- Facturas de proveedores eliminadas")

        # Gastos fijos
        GastoFijo.query.delete()
        print("- Gastos fijos eliminados")

        # Proveedores
        Proveedor.query.delete()
        print("- Proveedores eliminados")

        # Pagos
        Pago.query.delete()
        print("- Pagos eliminados")

        # Alumnos
        Alumno.query.delete()
        print("- Alumnos eliminados")

        # Horarios
        HorarioSemanal.query.delete()
        print("- Horarios eliminados")

        # Eventos de calendario
        EventoCalendario.query.delete()
        print("- Eventos de calendario eliminados")

        # Ingresos
        Ingreso.query.delete()
        print("- Ingresos eliminados")

        db.session.commit()

        flash('Sistema reseteado exitosamente. Todos los datos han sido eliminados.', 'success')
    except Exception as e:
        flash(f'Error al resetear el sistema: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('modo_pruebas'))

# RUTAS PARA FACTURACIÓN

@app.route('/facturacion')
def facturacion():
    """Dashboard principal de facturación"""
    # Obtener resumen de facturas
    facturas_emitidas = FacturaEmitida.query.order_by(FacturaEmitida.fecha_emision.desc()).limit(10).all()

    # Estadísticas del año actual
    año_actual = date.today().year
    total_facturado = db.session.query(db.func.sum(FacturaEmitida.base_imponible)).filter(
        db.extract('year', FacturaEmitida.fecha_emision) == año_actual,
        FacturaEmitida.estado != 'anulada'
    ).scalar() or 0

    facturas_pendientes = FacturaEmitida.query.filter_by(estado='emitida').count()
    facturas_pagadas = FacturaEmitida.query.filter_by(estado='pagada').count()

    # Configuración fiscal
    config_fiscal = ConfiguracionFiscal.query.first()

    return render_template('facturacion.html',
                         facturas=facturas_emitidas,
                         total_facturado=total_facturado,
                         facturas_pendientes=facturas_pendientes,
                         facturas_pagadas=facturas_pagadas,
                         config_fiscal=config_fiscal,
                         current_year=año_actual)

@app.route('/facturacion/clientes')
def clientes_facturacion():
    """Listado de clientes para facturación"""
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return render_template('clientes_facturacion.html', clientes=clientes)

@app.route('/facturacion/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        try:
            # Verificar si ya existe un cliente con ese NIF
            nif_cif = request.form.get('nif_cif', '').strip()
            if Cliente.query.filter_by(nif_cif=nif_cif).first():
                flash(f'Ya existe un cliente con el NIF/CIF {nif_cif}', 'error')
                return redirect(url_for('nuevo_cliente'))

            cliente = Cliente(
                nombre=request.form.get('nombre'),
                nif_cif=nif_cif,
                direccion=request.form.get('direccion'),
                codigo_postal=request.form.get('codigo_postal'),
                ciudad=request.form.get('ciudad'),
                provincia=request.form.get('provincia'),
                pais=request.form.get('pais', 'España'),
                email=request.form.get('email'),
                telefono=request.form.get('telefono'),
                tipo_cliente=request.form.get('tipo_cliente', 'particular'),
                notas=request.form.get('notas'),
                alumno_id=request.form.get('alumno_id') if request.form.get('alumno_id') else None
            )

            db.session.add(cliente)
            db.session.commit()

            flash(f'Cliente "{cliente.nombre}" creado exitosamente', 'success')
            return redirect(url_for('clientes_facturacion'))
        except Exception as e:
            flash(f'Error al crear el cliente: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('nuevo_cliente'))

    # GET request
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre).all()
    return render_template('nuevo_cliente.html', alumnos=alumnos)

@app.route('/facturacion/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    """Editar cliente existente"""
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        try:
            # Verificar NIF único (excepto el actual)
            nif_cif = request.form.get('nif_cif', '').strip()
            cliente_existente = Cliente.query.filter_by(nif_cif=nif_cif).first()
            if cliente_existente and cliente_existente.id != cliente_id:
                flash(f'Ya existe otro cliente con el NIF/CIF {nif_cif}', 'error')
                return redirect(url_for('editar_cliente', cliente_id=cliente_id))

            cliente.nombre = request.form.get('nombre')
            cliente.nif_cif = nif_cif
            cliente.direccion = request.form.get('direccion')
            cliente.codigo_postal = request.form.get('codigo_postal')
            cliente.ciudad = request.form.get('ciudad')
            cliente.provincia = request.form.get('provincia')
            cliente.pais = request.form.get('pais', 'España')
            cliente.email = request.form.get('email')
            cliente.telefono = request.form.get('telefono')
            cliente.tipo_cliente = request.form.get('tipo_cliente', 'particular')
            cliente.notas = request.form.get('notas')
            cliente.alumno_id = request.form.get('alumno_id') if request.form.get('alumno_id') else None

            db.session.commit()

            flash(f'Cliente "{cliente.nombre}" actualizado exitosamente', 'success')
            return redirect(url_for('clientes_facturacion'))
        except Exception as e:
            flash(f'Error al actualizar el cliente: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('editar_cliente', cliente_id=cliente_id))

    # GET request
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre).all()
    return render_template('editar_cliente.html', cliente=cliente, alumnos=alumnos)

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura_emitida():
    """Crear nueva factura"""
    if request.method == 'POST':
        try:
            # Obtener configuración fiscal
            config_fiscal = ConfiguracionFiscal.query.first()
            if not config_fiscal:
                flash('Debe configurar los datos fiscales antes de emitir facturas', 'error')
                return redirect(url_for('configuracion'))

            # Crear factura
            factura = FacturaEmitida(
                serie=request.form.get('serie', config_fiscal.serie_factura_default),
                fecha_emision=datetime.strptime(request.form.get('fecha_emision'), '%Y-%m-%d').date(),
                fecha_prestacion=datetime.strptime(request.form.get('fecha_prestacion'), '%Y-%m-%d').date(),
                cliente_id=request.form.get('cliente_id'),
                exenta_iva=request.form.get('exenta_iva') == 'on',
                tipo_iva=float(request.form.get('tipo_iva', 0)),
                tipo_retencion=float(request.form.get('tipo_retencion', 0)),
                observaciones=request.form.get('observaciones'),
                base_imponible=0,  # Se calculará después
                total=0  # Se calculará después
            )

            # Asignar motivo de exención si aplica
            if factura.exenta_iva:
                factura.motivo_exencion = config_fiscal.texto_exencion_iva

            # Generar número de factura
            factura.generar_numero_factura()

            db.session.add(factura)
            db.session.flush()  # Para obtener el ID de la factura

            # Procesar líneas de factura
            lineas_count = int(request.form.get('lineas_count', 0))
            for i in range(lineas_count):
                descripcion = request.form.get(f'linea_{i}_descripcion')
                if descripcion:  # Solo agregar líneas con descripción
                    linea = LineaFactura(
                        factura_id=factura.id,
                        orden=i,
                        descripcion=descripcion,
                        cantidad=float(request.form.get(f'linea_{i}_cantidad', 1)),
                        precio_unitario=float(request.form.get(f'linea_{i}_precio', 0))
                    )
                    linea.calcular_subtotal()
                    db.session.add(linea)

            # Calcular totales de la factura
            factura.calcular_totales()

            db.session.commit()

            flash(f'Factura {factura.numero_completo} creada exitosamente', 'success')
            return redirect(url_for('ver_factura_emitida', factura_id=factura.id))
        except Exception as e:
            flash(f'Error al crear la factura: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('nueva_factura_emitida'))

    # GET request
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    config_fiscal = ConfiguracionFiscal.query.first()
    tarifas = Tarifa.query.filter_by(activa=True).all()

    return render_template('nueva_factura.html',
                         clientes=clientes,
                         config_fiscal=config_fiscal,
                         tarifas=tarifas,
                         fecha_hoy=date.today())

@app.route('/facturacion/<int:factura_id>')
def ver_factura_emitida(factura_id):
    """Ver detalle de factura"""
    factura = FacturaEmitida.query.get_or_404(factura_id)
    config_fiscal = ConfiguracionFiscal.query.first()
    return render_template('ver_factura.html', factura=factura, config_fiscal=config_fiscal, fecha_hoy=date.today())

@app.route('/facturacion/<int:factura_id>/anular', methods=['POST'])
def anular_factura_emitida(factura_id):
    """Anular una factura"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)

        if factura.estado == 'anulada':
            flash('La factura ya está anulada', 'warning')
            return redirect(url_for('ver_factura_emitida', factura_id=factura_id))

        factura.estado = 'anulada'
        db.session.commit()

        flash(f'Factura {factura.numero_completo} anulada exitosamente', 'success')
        return redirect(url_for('ver_factura_emitida', factura_id=factura_id))
    except Exception as e:
        flash(f'Error al anular la factura: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('ver_factura_emitida', factura_id=factura_id))

@app.route('/facturacion/<int:factura_id>/marcar_pagada', methods=['POST'])
def marcar_factura_emitida_pagada(factura_id):
    """Marcar factura como pagada"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)

        factura.estado = 'pagada'
        factura.fecha_pago = datetime.strptime(request.form.get('fecha_pago'), '%Y-%m-%d').date()
        factura.metodo_pago = request.form.get('metodo_pago')

        db.session.commit()

        flash(f'Factura {factura.numero_completo} marcada como pagada', 'success')
        return redirect(url_for('ver_factura_emitida', factura_id=factura_id))
    except Exception as e:
        flash(f'Error al marcar la factura como pagada: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('ver_factura_emitida', factura_id=factura_id))

@app.route('/facturacion/<int:factura_id>/pdf')
def descargar_factura_pdf(factura_id):
    """Generar y descargar PDF de factura"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)
        config_fiscal = ConfiguracionFiscal.query.first()

        if not config_fiscal:
            flash('Debe configurar los datos fiscales antes de generar facturas en PDF', 'error')
            return redirect(url_for('ver_factura_emitida', factura_id=factura_id))

        from utils.pdf_generator import generar_pdf_factura
        pdf_buffer = generar_pdf_factura(factura, config_fiscal)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Factura_{factura.serie}_{factura.numero:04d}.pdf'
        )
    except Exception as e:
        flash(f'Error al generar PDF: {str(e)}', 'error')
        return redirect(url_for('ver_factura_emitida', factura_id=factura_id))

@app.route('/facturacion/configuracion-fiscal', methods=['GET', 'POST'])
def configuracion_fiscal():
    """Configurar datos fiscales del negocio"""
    config = ConfiguracionFiscal.query.first()

    if request.method == 'POST':
        try:
            if not config:
                config = ConfiguracionFiscal()
                db.session.add(config)

            config.nombre_empresa = request.form.get('nombre_empresa')
            config.nif = request.form.get('nif')
            config.direccion_fiscal = request.form.get('direccion_fiscal')
            config.codigo_postal = request.form.get('codigo_postal')
            config.ciudad = request.form.get('ciudad')
            config.provincia = request.form.get('provincia')
            config.telefono = request.form.get('telefono')
            config.email = request.form.get('email')
            config.epigrafe_iae = request.form.get('epigrafe_iae')
            config.regimen_iva = request.form.get('regimen_iva', 'general')
            config.tipo_retencion_default = float(request.form.get('tipo_retencion_default', 7.0))
            config.exento_iva = request.form.get('exento_iva') == 'on'
            config.texto_exencion_iva = request.form.get('texto_exencion_iva')
            config.serie_factura_default = request.form.get('serie_factura_default', 'A')
            config.pie_factura = request.form.get('pie_factura')

            db.session.commit()

            flash('Configuración fiscal actualizada exitosamente', 'success')
            return redirect(url_for('facturacion'))
        except Exception as e:
            flash(f'Error al actualizar la configuración fiscal: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('configuracion_fiscal'))

    # GET request
    return render_template('configuracion_fiscal.html', config=config)

# Rutas API
@app.route('/api/alumnos')
def api_alumnos():
    alumnos = Alumno.query.filter_by(activo=True).all()
    return jsonify([alumno.to_dict() for alumno in alumnos])

# RUTAS PARA GESTIÓN ECONÓMICA

@app.route('/economia')
def economia():
    """Dashboard principal de gestión económica unificado"""
    # Resumen financiero del mes y año actual
    current_month = date.today().month
    current_year = date.today().year

    # INGRESOS - Facturas emitidas a clientes
    facturas_emitidas_año = FacturaEmitida.query.filter(
        db.extract('year', FacturaEmitida.fecha_emision) == current_year,
        FacturaEmitida.estado != 'anulada'
    ).all()

    total_facturado_año = sum(f.base_imponible for f in facturas_emitidas_año)
    facturas_emitidas_pendientes = FacturaEmitida.query.filter_by(estado='emitida').count()
    facturas_emitidas_pagadas = FacturaEmitida.query.filter_by(estado='pagada').count()

    # Últimas facturas emitidas
    ultimas_facturas_emitidas = FacturaEmitida.query.order_by(FacturaEmitida.fecha_emision.desc()).limit(5).all()

    # GASTOS FIJOS
    gastos_fijos_activos = GastoFijo.query.filter_by(activo=True).count()
    gastos_fijos = GastoFijo.query.filter_by(activo=True).all()

    # Calcular total mensual de gastos fijos
    gastos_fijos_mensuales = 0
    for gasto in gastos_fijos:
        if gasto.frecuencia == 'mensual':
            gastos_fijos_mensuales += gasto.importe
        elif gasto.frecuencia == 'trimestral':
            gastos_fijos_mensuales += gasto.importe / 3
        elif gasto.frecuencia == 'anual':
            gastos_fijos_mensuales += gasto.importe / 12

    # GASTOS VARIABLES - Facturas de proveedores
    gastos_mes = db.session.query(db.func.sum(FacturaProveedor.importe_total)).filter(
        FacturaProveedor.estado == 'pagada',
        db.extract('month', FacturaProveedor.fecha_pago) == current_month,
        db.extract('year', FacturaProveedor.fecha_pago) == current_year
    ).scalar() or 0

    facturas_proveedores_pendientes = FacturaProveedor.query.filter_by(estado='pendiente').count()

    facturas_proveedores_vencidas = FacturaProveedor.query.filter(
        FacturaProveedor.estado == 'pendiente',
        FacturaProveedor.fecha_vencimiento < date.today()
    ).count()

    # Configuración fiscal
    config_fiscal = ConfiguracionFiscal.query.first()

    return render_template('economia/dashboard.html',
                         # Facturas emitidas
                         total_facturado_año=total_facturado_año,
                         facturas_emitidas_pendientes=facturas_emitidas_pendientes,
                         facturas_emitidas_pagadas=facturas_emitidas_pagadas,
                         ultimas_facturas_emitidas=ultimas_facturas_emitidas,
                         # Gastos fijos
                         gastos_fijos_activos=gastos_fijos_activos,
                         gastos_fijos_mensuales=gastos_fijos_mensuales,
                         # Gastos variables (facturas proveedores)
                         gastos_mes=gastos_mes,
                         facturas_proveedores_pendientes=facturas_proveedores_pendientes,
                         facturas_proveedores_vencidas=facturas_proveedores_vencidas,
                         # General
                         current_year=current_year,
                         config_fiscal=config_fiscal)

@app.route('/economia/proveedores')
def proveedores():
    """Lista de proveedores"""
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/proveedores.html', proveedores=proveedores)

@app.route('/economia/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form['nombre'],
                cif_nif=request.form.get('cif_nif'),
                direccion=request.form.get('direccion'),
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                contacto_principal=request.form.get('contacto_principal'),
                notas=request.form.get('notas')
            )
            db.session.add(proveedor)
            db.session.commit()
            flash('¡Proveedor creado exitosamente!', 'success')
            return redirect(url_for('proveedores'))
        except Exception as e:
            flash(f'Error al crear proveedor: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('economia/nuevo_proveedor.html')

@app.route('/economia/facturas')
def facturas():
    """Lista de facturas"""
    facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
    return render_template('economia/facturas.html', facturas=facturas)

@app.route('/economia/facturas/nueva', methods=['GET', 'POST'])
def nueva_factura():
    """Crear nueva factura"""
    if request.method == 'POST':
        try:
            importe_sin_iva = float(request.form['importe_sin_iva'])
            iva = float(request.form.get('iva', 21))
            importe_total = importe_sin_iva * (1 + iva / 100)
            
            factura = FacturaProveedor(
                numero_factura=request.form['numero_factura'],
                proveedor_id=int(request.form['proveedor_id']),
                categoria_id=int(request.form['categoria_id']),
                fecha_factura=datetime.strptime(request.form['fecha_factura'], '%Y-%m-%d').date(),
                fecha_vencimiento=datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date() if request.form.get('fecha_vencimiento') else None,
                importe_sin_iva=importe_sin_iva,
                iva=iva,
                importe_total=importe_total,
                descripcion=request.form.get('descripcion'),
                notas=request.form.get('notas')
            )
            db.session.add(factura)
            db.session.commit()
            flash('¡Factura registrada exitosamente!', 'success')
            return redirect(url_for('facturas'))
        except Exception as e:
            flash(f'Error al registrar factura: {str(e)}', 'error')
            db.session.rollback()
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    return render_template('economia/nueva_factura.html', proveedores=proveedores, categorias=categorias)

@app.route('/economia/gastos-fijos')
def gastos_fijos():
    """Lista de gastos fijos"""
    gastos = GastoFijo.query.filter_by(activo=True).all()
    return render_template('economia/gastos_fijos.html', gastos=gastos)

@app.route('/economia/gastos-fijos/nuevo', methods=['GET', 'POST'])
def nuevo_gasto_fijo():
    """Crear nuevo gasto fijo"""
    if request.method == 'POST':
        try:
            gasto = GastoFijo(
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion'),
                proveedor_id=int(request.form['proveedor_id']) if request.form.get('proveedor_id') else None,
                categoria_id=int(request.form['categoria_id']),
                importe=float(request.form['importe']),
                frecuencia=request.form['frecuencia'],
                dia_cargo=int(request.form.get('dia_cargo', 1)),
                fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
                fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
                notas=request.form.get('notas')
            )
            db.session.add(gasto)
            db.session.commit()
            flash('¡Gasto fijo creado exitosamente!', 'success')
            return redirect(url_for('gastos_fijos'))
        except Exception as e:
            flash(f'Error al crear gasto fijo: {str(e)}', 'error')
            db.session.rollback()

    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/nuevo_gasto_fijo.html', categorias=categorias, proveedores=proveedores, fecha_hoy=date.today())

@app.route('/economia/export/<tipo>')
def export_data(tipo):
    """Exportar datos económicos a CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    output = StringIO()
    
    if tipo == 'facturas':
        facturas = FacturaProveedor.query.all()
        writer = csv.writer(output)
        writer.writerow(['Número', 'Proveedor', 'Categoría', 'Fecha', 'Importe Sin IVA', 'IVA', 'Total', 'Estado', 'Descripción'])
        
        for factura in facturas:
            writer.writerow([
                factura.numero_factura,
                factura.proveedor.nombre,
                factura.categoria.nombre,
                factura.fecha_factura.strftime('%Y-%m-%d'),
                factura.importe_sin_iva,
                factura.iva,
                factura.importe_total,
                factura.estado,
                factura.descripcion or ''
            ])
    
    elif tipo == 'gastos-fijos':
        gastos = GastoFijo.query.all()
        writer = csv.writer(output)
        writer.writerow(['Nombre', 'Categoría', 'Importe', 'Frecuencia', 'Día Cargo', 'Fecha Inicio', 'Fecha Fin', 'Activo'])
        
        for gasto in gastos:
            writer.writerow([
                gasto.nombre,
                gasto.categoria.nombre,
                gasto.importe,
                gasto.frecuencia,
                gasto.dia_cargo,
                gasto.fecha_inicio.strftime('%Y-%m-%d'),
                gasto.fecha_fin.strftime('%Y-%m-%d') if gasto.fecha_fin else '',
                'Sí' if gasto.activo else 'No'
            ])
    
    elif tipo == 'ingresos':
        ingresos = Ingreso.query.all()
        writer = csv.writer(output)
        writer.writerow(['Concepto', 'Importe', 'Fecha', 'Tipo', 'Método Pago', 'Alumno', 'Notas'])
        
        for ingreso in ingresos:
            alumno_nombre = ''
            if ingreso.alumno_id:
                alumno = Alumno.query.get(ingreso.alumno_id)
                if alumno:
                    alumno_nombre = f"{alumno.nombre} {alumno.apellido}"
            
            writer.writerow([
                ingreso.concepto,
                ingreso.importe,
                ingreso.fecha.strftime('%Y-%m-%d'),
                ingreso.tipo,
                ingreso.metodo_pago or '',
                alumno_nombre,
                ingreso.notas or ''
            ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={tipo}_atma_suddhi.csv'
    
    return response

# Rutas del Calendario Interactivo
@app.route('/calendario')
def calendario():
    clases = Clase.query.filter_by(activa=True).all()
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.apellido, Alumno.nombre).all()
    return render_template('calendario.html', clases=clases, alumnos=alumnos)

@app.route('/debug-calendario')
def debug_calendario():
    """Página de debug para verificar el calendario"""
    return render_template('debug_calendario.html')

@app.route('/calendario-simple')
def calendario_simple():
    """Versión simplificada del calendario para debugging"""
    return render_template('calendario_simple.html')

@app.route('/api/horarios')
def get_horarios_api():
    """API para obtener todos los horarios semanales"""
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return jsonify([{
        'id': h.id,
        'clase_id': h.clase_id,
        'clase_nombre': h.clase.nombre,
        'dia_semana': h.dia_semana,
        'hora_inicio': h.hora_inicio.strftime('%H:%M'),
        'hora_fin': h.hora_fin.strftime('%H:%M'),
        'instructor': h.instructor,
        'activo': h.activo
    } for h in horarios])

@app.route('/api/calendario/eventos')
def get_eventos_calendario():
    """Obtiene todos los eventos para el calendario (horarios recurrentes + eventos individuales + asistencias)"""
    eventos = []

    # Obtener rango de fechas del request
    start = request.args.get('start')
    end = request.args.get('end')

    if start and end:
        # IMPORTANTE: En URLs, el '+' se convierte en espacio por request.args.get()
        # Ejemplo: "2025-12-29T00:00:00+01:00" llega como "2025-12-29T00:00:00 01:00"
        # También soporta: 2025-12-29T00:00:00Z, 2025-12-29T00:00:00

        # Quitar zona horaria (puede venir como ' 01:00', '+01:00', 'Z' o nada)
        # Buscamos el último 'T' y tomamos todo hasta el último ':'
        # Ejemplo: "2025-12-29T00:00:00 01:00" -> tomar hasta "2025-12-29T00:00:00"

        # Split por espacio, +, o Z y tomar solo la parte de fecha/hora
        import re
        start_clean = re.split(r'[\s+Z]', start)[0]
        end_clean = re.split(r'[\s+Z]', end)[0]

        start_date = datetime.fromisoformat(start_clean)
        end_date = datetime.fromisoformat(end_clean)
    else:
        # Default: próximas 2 semanas
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() + timedelta(days=14)

    # 1. Generar eventos desde horarios recurrentes
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    current_date = start_date.date()

    while current_date <= end_date.date():
        dia_semana = current_date.weekday()

        for horario in horarios:
            if horario.dia_semana == dia_semana:
                # Crear evento para este día
                fecha_inicio = datetime.combine(current_date, horario.hora_inicio)
                fecha_fin = datetime.combine(current_date, horario.hora_fin)

                # Contar asistencias para esta clase
                asistencias_clase = Asistencia.query.filter_by(
                    horario_id=horario.id,
                    fecha_clase=current_date
                ).all()

                total_asistencias = len(asistencias_clase)
                presentes = sum(1 for a in asistencias_clase if a.presente)

                # Obtener nombres de alumnos presentes y ausentes
                alumnos_presentes = []
                alumnos_ausentes = []
                for asistencia in asistencias_clase:
                    nombre_completo = f"{asistencia.alumno.nombre} {asistencia.alumno.apellido}"
                    if asistencia.presente:
                        alumnos_presentes.append(nombre_completo)
                    else:
                        alumnos_ausentes.append(nombre_completo)

                # Construir título con información de asistencia
                titulo = horario.clase.nombre
                if total_asistencias > 0:
                    titulo += f" ({presentes}/{total_asistencias})"

                eventos.append({
                    'id': f'h_{horario.id}_{current_date.isoformat()}',
                    'title': titulo,
                    'start': fecha_inicio.isoformat(),
                    'end': fecha_fin.isoformat(),
                    'className': horario.clase.nombre,
                    'color': horario.clase.color or '#4ECDC4',
                    'instructor': horario.instructor,
                    'tipo': 'recurrente',
                    'horario_id': horario.id,
                    'total_asistencias': total_asistencias,
                    'presentes': presentes,
                    'alumnos_presentes': alumnos_presentes,
                    'alumnos_ausentes': alumnos_ausentes,
                    'fecha': current_date.isoformat(),
                    'editable': False
                })

        current_date += timedelta(days=1)

    # 2. Añadir eventos individuales
    eventos_individuales = EventoCalendario.query.filter(
        EventoCalendario.activo == True,
        EventoCalendario.fecha_inicio >= start_date,
        EventoCalendario.fecha_inicio <= end_date
    ).all()

    for evento in eventos_individuales:
        eventos.append({
            'id': f'e_{evento.id}',
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat(),
            'description': evento.descripcion,
            'className': evento.clase.nombre if evento.clase else 'Individual',
            'alumno': f"{evento.alumno.nombre} {evento.alumno.apellido}" if evento.alumno else None,
            'tipo': evento.tipo,
            'color': evento.color,
            'instructor': evento.instructor,
            'evento_id': evento.id,
            'editable': True
        })

    return jsonify(eventos)

@app.route('/api/calendario/eventos/<int:evento_id>')
def get_evento_calendario(evento_id):
    """Obtiene detalles de un evento individual"""
    evento = EventoCalendario.query.get_or_404(evento_id)

    return jsonify({
        'id': evento.id,
        'titulo': evento.titulo,
        'descripcion': evento.descripcion,
        'clase_id': evento.clase_id,
        'alumno_id': evento.alumno_id,
        'fecha_inicio': evento.fecha_inicio.isoformat(),
        'fecha_fin': evento.fecha_fin.isoformat(),
        'tipo': evento.tipo,
        'color': evento.color,
        'instructor': evento.instructor
    })

@app.route('/api/calendario/eventos', methods=['POST'])
def crear_evento_calendario():
    """Crea un nuevo evento individual"""
    try:
        data = request.get_json()

        # Generar título automático si no se proporciona
        titulo = data.get('titulo')
        if not titulo:
            if data.get('alumno_id'):
                alumno = Alumno.query.get(data['alumno_id'])
                titulo = f"Clase Individual - {alumno.nombre} {alumno.apellido}"
            else:
                titulo = "Evento Especial"

        evento = EventoCalendario(
            titulo=titulo,
            descripcion=data.get('descripcion'),
            clase_id=data.get('clase_id') if data.get('clase_id') else None,
            alumno_id=data.get('alumno_id') if data.get('alumno_id') else None,
            fecha_inicio=datetime.fromisoformat(data['fecha_inicio']),
            fecha_fin=datetime.fromisoformat(data['fecha_fin']),
            tipo=data.get('tipo', 'individual'),
            color=data.get('color', '#8B5FBF'),
            instructor=data.get('instructor', 'Minouche')
        )

        db.session.add(evento)
        db.session.commit()

        return jsonify({'success': True, 'id': evento.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calendario/eventos/<int:evento_id>', methods=['PUT'])
def actualizar_evento_calendario(evento_id):
    """Actualiza un evento individual"""
    try:
        evento = EventoCalendario.query.get_or_404(evento_id)
        data = request.get_json()

        if 'titulo' in data:
            evento.titulo = data['titulo']
        if 'descripcion' in data:
            evento.descripcion = data['descripcion']
        if 'clase_id' in data:
            evento.clase_id = data['clase_id'] if data['clase_id'] else None
        if 'alumno_id' in data:
            evento.alumno_id = data['alumno_id'] if data['alumno_id'] else None
        if 'fecha_inicio' in data:
            evento.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        if 'fecha_fin' in data:
            evento.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
        if 'tipo' in data:
            evento.tipo = data['tipo']
        if 'color' in data:
            evento.color = data['color']
        if 'instructor' in data:
            evento.instructor = data['instructor']

        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calendario/eventos/<int:evento_id>', methods=['DELETE'])
def eliminar_evento_calendario(evento_id):
    """Elimina un evento individual"""
    try:
        evento = EventoCalendario.query.get_or_404(evento_id)
        evento.activo = False  # Soft delete
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        inicializar_categorias_gastos()
        crear_datos_prueba()
    app.run(debug=True, host='0.0.0.0', port=5000)
