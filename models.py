from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# MODELOS DE BASE DE DATOS

# Modelo de Usuario del Sistema
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='instructor')  # admin, instructor, recepcionista
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def get_rol_display(self):
        roles = {
            'admin': 'Administrador',
            'instructor': 'Instructor',
            'recepcionista': 'Recepcionista'
        }
        return roles.get(self.rol, self.rol)
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def is_instructor(self):
        return self.rol in ['admin', 'instructor']
    
    def can_manage_users(self):
        return self.rol == 'admin'
    
    def can_manage_payments(self):
        return self.rol in ['admin', 'recepcionista']
    
    def can_manage_yogaterapia(self):
        return self.rol in ['admin', 'instructor']

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
    tipo_cuota = db.Column(db.String(30), nullable=False, default='1_clase_semanal')
    matricula_pagada = db.Column(db.Boolean, default=False)
    fecha_matricula = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    pagos = db.relationship('Pago', backref='alumno', lazy=True)
    cliente = db.relationship('Cliente', backref='alumno', lazy=True, uselist=False)
    horarios = db.relationship('HorarioSemanal', secondary='inscripciones_horarios', backref='alumnos_inscritos', lazy=True)
    
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
            '2_clases_bimensual': '2 clases bimensual',
            'yogaterapia_individual': 'Yogaterapia individual',
            'yogaterapia_pareja': 'Yogaterapia en pareja'
        }
        return tipos.get(self.tipo_cuota, self.tipo_cuota)
    
    def get_precio_cuota(self):
        """Obtiene el precio de la cuota según el tipo"""
        # Buscar en la configuración de tipos de clase
        tipo_clase = TipoClase.query.filter_by(codigo=self.tipo_cuota, activo=True).first()
        if tipo_clase:
            return tipo_clase.precio
        
        # Fallback a precios por defecto si no está configurado
        precios = {
            'clase_suelta': 15.00,
            '1_clase_semanal': 40.00,
            '2_clases_semanal': 70.00,
            'plana': 90.00,
            '1_clase_bimensual': 75.00,
            '2_clases_bimensual': 135.00,
            'yogaterapia_individual': 50.00,
            'yogaterapia_pareja': 70.00
        }
        return precios.get(self.tipo_cuota, 40.00)

# Modelo de Pago
class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    mes = db.Column(db.String(7), nullable=True)  # Formato: YYYY-MM
    año = db.Column(db.Integer, nullable=True)  # Año para matrícula
    fecha_clase = db.Column(db.Date, nullable=True)  # Para clases sueltas
    monto = db.Column(db.Float, nullable=False)
    tipo_pago = db.Column(db.String(20), default='cuota')  # cuota, matricula, clase_suelta, yogaterapia
    descripcion = db.Column(db.String(100))
    metodo_pago = db.Column(db.String(50))  # efectivo, transferencia, tarjeta
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago {self.mes} - {self.monto}>'

# Modelo de Clase
class Clase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7), default='#4ECDC4')  # Color hexadecimal para el calendario
    activa = db.Column(db.Boolean, default=True)
    duracion_minutos = db.Column(db.Integer, default=75)  # Duración por defecto de la clase
    periodicidad = db.Column(db.String(50), default='semanal')  # semanal, quincenal, mensual
    precio = db.Column(db.Float, default=15.00)
    nivel = db.Column(db.String(50), default='todos')
    capacidad_maxima = db.Column(db.Integer, default=15)
    instructor = db.Column(db.String(100), default='Minouche')

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
            'periodicidad': self.periodicidad,
            'instructor': self.instructor
        }

# Modelo de Horario Semanal
# Tabla de asociación para inscripciones de alumnos en clases semanales
inscripciones_horarios = db.Table('inscripciones_horarios',
    db.Column('alumno_id', db.Integer, db.ForeignKey('alumno.id'), primary_key=True),
    db.Column('horario_id', db.Integer, db.ForeignKey('horario_semanal.id'), primary_key=True)
)

class HorarioSemanal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    instructor = db.Column(db.String(50), default='Minouche')
    capacidad_maxima = db.Column(db.Integer, default=15)
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    asistencias = db.relationship('Asistencia', backref='horario', lazy=True)
    clase = db.relationship('Clase', backref='horarios', lazy=True)
    
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
            'clase': self.clase.to_dict() if self.clase else None,
            'dia_semana': self.dia_semana,
            'dias_semana_texto': self.get_dia_display(),
            'hora_inicio': self.hora_inicio.strftime('%H:%M'),
            'hora_fin': self.hora_fin.strftime('%H:%M'),
            'instructor': self.instructor,
            'capacidad_maxima': self.capacidad_maxima,
            'observaciones': self.observaciones or '',
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


    def __repr__(self):
        return f'<Asistencia {self.alumno.nombre} - {self.fecha_clase}>'

    def to_dict(self):
        # Generar objeto evento compatible con lo que espera el frontend
        evento_info = {
            'titulo': 'Clase',
            'color': '#4ECDC4',
            'hora_inicio': '00:00',
            'hora_fin': '00:00',
            'instructor': 'Minouche'
        }
        
        if self.horario:
            evento_info['titulo'] = self.horario.clase.nombre
            evento_info['color'] = self.horario.clase.color
            evento_info['hora_inicio'] = self.horario.hora_inicio.strftime('%H:%M')
            evento_info['hora_fin'] = self.horario.hora_fin.strftime('%H:%M')
            evento_info['instructor'] = self.horario.instructor
        elif self.evento:
            evento_info['titulo'] = self.evento.titulo
            evento_info['color'] = self.evento.color
            evento_info['hora_inicio'] = self.evento.fecha_inicio.strftime('%H:%M')
            evento_info['hora_fin'] = self.evento.fecha_fin.strftime('%H:%M')
            evento_info['instructor'] = self.evento.instructor

        return {
            'id': self.id,
            'fecha': self.fecha_clase.isoformat(),
            'asistio': self.presente,
            'observaciones': self.observaciones,
            'evento': evento_info
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

# Modelo de Instructor
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    especialidad = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Instructor {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'especialidad': self.especialidad,
            'activo': self.activo
        }

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
    fecha_pago = db.Date
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
    fecha = db.Column(db.Date, nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    importe = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), default='Varios')
    metodo_pago = db.Column(db.String(50))
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=True)
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    alumno = db.relationship('Alumno', backref='ingresos')
    
    def __repr__(self):
        return f'<Ingreso {self.concepto} - {self.importe}€>'

# Modelo de Gasto Mensual (Simplificado)
class GastoMensual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # Alquiler, Suministros, Material, etc.
    importe = db.Column(db.Float, nullable=False)
    pagado = db.Column(db.Boolean, default=False)
    metodo_pago = db.Column(db.String(50))  # efectivo, transferencia, tarjeta, domiciliacion
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GastoMensual {self.concepto} - {self.importe}€>'
    
    @property
    def categoria_color(self):
        colores = {
            'Alquiler': '#dc3545',
            'Suministros': '#ffc107', 
            'Material': '#28a745',
            'Marketing': '#007bff',
            'Formación': '#6f42c1',
            'Seguros': '#fd7e14',
            'Mantenimiento': '#20c997',
            'Otros': '#6c757d'
        }
        return colores.get(self.categoria, '#6c757d')

# Modelo de Tipo de Clase Configurable
class TipoClase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  # ej: 'clase_suelta', '1_clase_semanal'
    nombre = db.Column(db.String(100), nullable=False)  # ej: 'Clase Suelta', '1 Clase Semanal'
    descripcion = db.Column(db.Text)  # Descripción detallada
    precio = db.Column(db.Float, nullable=False)
    frecuencia = db.Column(db.String(20), default='mensual')  # mensual, bimensual, anual, por_clase
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)  # Para ordenar en la lista
    color = db.Column(db.String(7), default='#007bff')  # Color para visualización
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TipoClase {self.nombre}: {self.precio}€>'
    
    def get_precio_display(self):
        """Obtiene el precio con la unidad correspondiente"""
        unidades = {
            'por_clase': '€/clase',
            'mensual': '€/mes',
            'bimensual': '€/bimestre',
            'anual': '€/año'
        }
        return f"{self.precio} {unidades.get(self.frecuencia, '€')}"

# MODELOS DE YOGATERAPIA

# Modelo de Yogaterapia (Sesiones Individuales)
class SesionYogaterapia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)  # Referencia al alumno
    fecha_sesion = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)  # Hora de inicio de la sesión
    hora_fin = db.Column(db.Time)  # Hora de fin de la sesión
    duracion_minutos = db.Column(db.Integer, default=60)
    tipo_sesion = db.Column(db.String(50), default='individual')  # individual, pareja
    
    # Información terapéutica
    motivo_consulta = db.Column(db.Text)  # Por qué viene la persona
    objetivos_terapeuticos = db.Column(db.Text)  # Objetivos específicos
    tecnicas_aplicadas = db.Column(db.Text)  # Técnicas de yoga utilizadas
    posturas_trabajadas = db.Column(db.Text)  # Asanas específicas
    respiracion_pranayama = db.Column(db.Text)  # Ejercicios de respiración
    meditacion_relajacion = db.Column(db.Text)  # Técnicas de meditación
    
    # Evaluación y seguimiento
    estado_inicial = db.Column(db.Text)  # Cómo llegó la persona
    respuesta_sesion = db.Column(db.Text)  # Cómo respondió durante la sesión
    estado_final = db.Column(db.Text)  # Cómo se fue la persona
    observaciones_terapeuta = db.Column(db.Text)  # Observaciones profesionales
    recomendaciones_casa = db.Column(db.Text)  # Práctica para casa
    proxima_sesion = db.Column(db.Text)  # Plan para próxima sesión
    
    # Información administrativa
    instructor = db.Column(db.String(50), default='Minouche')
    precio = db.Column(db.Float, default=45.00)
    pagado = db.Column(db.Boolean, default=False)
    metodo_pago = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    alumno = db.relationship('Alumno', backref='sesiones_yogaterapia', lazy=True)
    archivos = db.relationship('ArchivoYogaterapia', backref='sesion_yogaterapia', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SesionYogaterapia {self.alumno.nombre if self.alumno else "Sin alumno"} - {self.fecha_sesion}>'

# Modelo de Archivo de Yogaterapia
class ArchivoYogaterapia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sesion_yogaterapia_id = db.Column(db.Integer, db.ForeignKey('sesion_yogaterapia.id'), nullable=False)
    nombre_archivo = db.Column(db.String(200), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tipo_archivo = db.Column(db.String(50))  # pdf, imagen, video, audio
    descripcion = db.Column(db.String(200))
    tamaño_bytes = db.Column(db.Integer)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ArchivoYogaterapia {self.nombre_archivo}>'

# Modelo de Clase Personal (Simplificado)
class ClasePersonal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    fecha_clase = db.Column(db.Date, nullable=False)
    duracion_minutos = db.Column(db.Integer, default=60)
    tipo_sesion = db.Column(db.String(50), default='individual')  # individual, pareja
    objetivos = db.Column(db.Text)
    desarrollo = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    instructor = db.Column(db.String(50), default='Minouche')
    precio = db.Column(db.Float, default=50.00)
    pagado = db.Column(db.Boolean, default=False)
    metodo_pago = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClasePersonal {self.alumno.nombre} - {self.fecha_clase}>'

# Modelo de Sutra
class Sutra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)  # I.1, I.2, etc.
    sanscrito = db.Column(db.Text, nullable=False)  # Texto en sánscrito
    transliteracion = db.Column(db.Text, nullable=False)  # Transliteración
    traduccion = db.Column(db.Text, nullable=False)  # Traducción al español
    libro = db.Column(db.String(50), nullable=False)  # Samadhi Pada, Sadhana Pada, etc.
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sutra {self.numero}: {self.traduccion[:50]}...>'
