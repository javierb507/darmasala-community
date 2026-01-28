from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'atma-suddhi-yoga-management-2025-secure-key')

# Configuración de base de datos para producción
if os.environ.get('FLASK_ENV') == 'production':
    # Para Hostinger con MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://usuario:password@localhost/nombre_bd')
else:
    # Para desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_school.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Initialize database
db = SQLAlchemy(app)

# Función para obtener información de versión
def get_version_info():
    """Obtener información de versión desde el archivo JSON"""
    try:
        version_file = os.path.join(app.static_folder, 'version.json')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Fallback si no existe el archivo
    return {
        'version': '1.0.0',
        'build_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'git_info': {
            'commit_hash': 'unknown',
            'branch': 'main',
            'commit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

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

# Funciones de autenticación
def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Obtener el usuario actual de la sesión"""
    if 'user_id' in session:
        return Usuario.query.get(session['user_id'])
    return None

def obtener_sutra_semanal():
    """Obtener el sutra de la semana actual"""
    # Obtener el número de semana del año
    from datetime import datetime
    semana_actual = datetime.now().isocalendar()[1]
    
    # Obtener el sutra correspondiente a esta semana
    try:
        total_sutras = Sutra.query.count()
        if total_sutras == 0:
            return None
        
        # Usar el número de semana para seleccionar un sutra
        indice_sutra = (semana_actual - 1) % total_sutras
        sutra = Sutra.query.offset(indice_sutra).first()
        
        if sutra:
            # Formatear el número del sutra como I.1, I.2, etc.
            if '.' in str(sutra.numero):
                # Si ya tiene formato I.1, mantenerlo
                sutra.numero_formateado = sutra.numero
            else:
                # Si es solo un número, formatearlo como I.X
                try:
                    num = int(sutra.numero)
                    sutra.numero_formateado = f"I.{num}"
                except:
                    sutra.numero_formateado = sutra.numero
        
        return sutra
    except Exception as e:
        print(f"Error consultando sutras: {e}")
        return None

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
        return precios.get(tipo_cuota, self.precio_1_semanal)

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

# RUTAS DE AUTENTICACIÓN

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username, activo=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['rol'] = user.rol
            
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            
            flash(f'¡Bienvenido, {user.nombre}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    # Obtener sutra semanal para mostrar en login
    sutra_semanal = obtener_sutra_semanal()
    return render_template('auth/login.html', sutra_semanal=sutra_semanal)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

# RUTAS PRINCIPALES

# Context Processor para hacer disponibles las utilidades de calendario y versión en todos los templates
@app.context_processor
def inject_global_vars():
    """Inyecta utilidades de calendario y versión en todos los templates."""
    context = crear_contexto_calendario()
    context['version_info'] = get_version_info()
    return context

# Routes
@app.route('/')
@login_required
def index():
    # Dashboard con próximas citas y estadísticas
    proximas_citas = obtener_proximas_citas(5)
    total_alumnos = Alumno.query.filter_by(activo=True).count()
    total_sesiones_hoy = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion == datetime.now().date()
    ).count()
    
    # Sutra semanal
    sutra_semanal = obtener_sutra_semanal()
    
    return render_template('index.html', 
                         proximas_citas=proximas_citas,
                         total_alumnos=total_alumnos,
                         total_sesiones_hoy=total_sesiones_hoy,
                         sutra_semanal=sutra_semanal,
                         today=datetime.now().date())

@app.route('/alumnos')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
            alumno.tipo_cuota = request.form.get('tipo_cuota', '1_clase_semanal')
            
            db.session.commit()
            flash('¡Alumno actualizado exitosamente!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno.id))
        except Exception as e:
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_alumno.html', alumno=alumno)

@app.route('/alumnos/<int:alumno_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if request.method == 'POST':
        alumno.activo = False
        db.session.commit()
        flash('¡Alumno desactivado exitosamente!', 'success')
        return redirect(url_for('alumnos'))
    else:
        if request.args.get('confirm') == '1':
            alumno.activo = False
            db.session.commit()
            flash('¡Alumno desactivado exitosamente!', 'success')
            return redirect(url_for('alumnos'))
        else:
            flash('Confirma la desactivación del alumno.', 'warning')
            return redirect(url_for('alumnos'))

@app.route('/alumnos/<int:alumno_id>/reactivar', methods=['POST'])
@login_required
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
@login_required
def agregar_pago(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)

    if request.method == 'POST':
        try:
            tipo_pago = request.form['tipo_pago']
            monto = float(request.form['monto'])
            metodo_pago = request.form.get('metodo_pago', 'efectivo')
            
            # Manejar mes y año según el tipo de pago
            mes = None
            año = None
            fecha_clase = None
            
            if tipo_pago == 'cuota':
                mes = request.form.get('mes')
                # Verificar si ya existe un pago para este mes
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='cuota',
                    mes=mes
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de cuota para {mes}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('ver_alumno', alumno_id=alumno_id))
                    
            elif tipo_pago == 'matricula':
                año = int(request.form.get('año', date.today().year))
                # Verificar si ya existe un pago de matrícula para este año
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='matricula',
                    año=año
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de matrícula para el año {año}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('ver_alumno', alumno_id=alumno_id))
                    
            elif tipo_pago == 'clase_suelta':
                fecha_clase = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
                # Verificar si ya existe un pago para esta fecha específica
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='clase_suelta',
                    fecha_clase=fecha_clase
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de clase suelta para el {fecha_clase.strftime("%d/%m/%Y")}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('ver_alumno', alumno_id=alumno_id))
            
            # Crear descripción según el tipo de pago
            if tipo_pago == 'matricula':
                # Calcular formato de año académico
                if año >= 2025:
                    matricula_desc = f"Matrícula {(año % 100)}/{((año + 1) % 100)}"
                else:
                    matricula_desc = f"Matrícula {año}"
            
            descripciones = {
                'cuota': f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                'matricula': matricula_desc if tipo_pago == 'matricula' else f'Matrícula {año}',
                'clase_suelta': f'Clase suelta - {fecha_clase.strftime("%d/%m/%Y") if fecha_clase else ""}'
            }
            
            pago = Pago(
                alumno_id=alumno_id,
                mes=mes,
                año=año,
                fecha_clase=fecha_clase,
                monto=monto,
                tipo_pago=tipo_pago,
                descripcion=descripciones.get(tipo_pago, 'Pago'),
                metodo_pago=metodo_pago
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

@app.route('/pagos/<int:pago_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_pago(pago_id):
    """Editar un pago existente"""
    pago = Pago.query.get_or_404(pago_id)
    alumno = pago.alumno
    
    if request.method == 'POST':
        try:
            # Actualizar datos del pago
            pago.monto = float(request.form['monto'])
            pago.metodo_pago = request.form.get('metodo_pago', 'efectivo')
            
            # Actualizar campos específicos según el tipo
            if pago.tipo_pago == 'cuota':
                nuevo_mes = request.form.get('mes')
                # Verificar duplicados solo si cambió el mes
                if nuevo_mes != pago.mes:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='cuota',
                        mes=nuevo_mes
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de cuota para {nuevo_mes}', 'warning')
                        return redirect(url_for('ver_alumno', alumno_id=alumno.id))
                pago.mes = nuevo_mes
                
            elif pago.tipo_pago == 'matricula':
                nuevo_año = int(request.form.get('año', date.today().year))
                # Verificar duplicados solo si cambió el año
                if nuevo_año != pago.año:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='matricula',
                        año=nuevo_año
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de matrícula para el año {nuevo_año}', 'warning')
                        return redirect(url_for('ver_alumno', alumno_id=alumno.id))
                pago.año = nuevo_año
                
            elif pago.tipo_pago == 'clase_suelta':
                nueva_fecha = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
                # Verificar duplicados solo si cambió la fecha
                if nueva_fecha != pago.fecha_clase:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='clase_suelta',
                        fecha_clase=nueva_fecha
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de clase suelta para el {nueva_fecha.strftime("%d/%m/%Y")}', 'warning')
                        return redirect(url_for('ver_alumno', alumno_id=alumno.id))
                pago.fecha_clase = nueva_fecha
            
            db.session.commit()
            flash('¡Pago actualizado exitosamente!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno.id))
            
        except Exception as e:
            flash(f'Error al actualizar pago: {str(e)}', 'error')
            db.session.rollback()
    
    # Calcular año de matrícula para el template
    current_date = date.today()
    if current_date.month >= 9:
        matricula_year = f"{current_date.year % 100}/{(current_date.year + 1) % 100}"
        matricula_year_numeric = current_date.year
    else:
        matricula_year = f"{(current_date.year - 1) % 100}/{current_date.year % 100}"
        matricula_year_numeric = current_date.year - 1
    
    return render_template('editar_pago.html', 
                         pago=pago,
                         alumno=alumno,
                         current_year=date.today().year,
                         matricula_year=matricula_year,
                         matricula_year_numeric=matricula_year_numeric)

@app.route('/pagos/<int:pago_id>/eliminar', methods=['POST'])
@login_required
def eliminar_pago(pago_id):
    """Eliminar un pago"""
    try:
        pago = Pago.query.get_or_404(pago_id)
        alumno_id = pago.alumno_id
        
        # Si es matrícula, actualizar el estado del alumno
        if pago.tipo_pago == 'matricula':
            # Verificar si hay otros pagos de matrícula
            otros_pagos_matricula = Pago.query.filter_by(
                alumno_id=alumno_id,
                tipo_pago='matricula'
            ).filter(Pago.id != pago.id).first()
            
            if not otros_pagos_matricula:
                alumno = Alumno.query.get(alumno_id)
                alumno.matricula_pagada = False
                alumno.fecha_matricula = None
        
        db.session.delete(pago)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pago eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Rutas para Clases y Horarios
@app.route('/clases')
@login_required
def clases():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases.html', clases=clases)

@app.route('/horarios')
@login_required
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

@app.route('/horarios/calendario')
@login_required
def horarios_calendario():
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return render_template('horarios_calendario.html', horarios=horarios)

@app.route('/horarios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_horario():
    """Crear nuevo horario semanal"""
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
            return redirect(url_for('calendario'))
    
    # GET request
    return redirect(url_for('calendario'))

@app.route('/horarios/<int:horario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_horario(horario_id):
    horario = HorarioSemanal.query.get_or_404(horario_id)
    
    if request.method == 'POST':
        try:
            horario.dia_semana = int(request.form['dia_semana'])
            horario.hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            horario.hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            horario.instructor = request.form['instructor']
            horario.clase_id = int(request.form['clase_id'])
            
            db.session.commit()
            flash('Horario actualizado exitosamente', 'success')
            return redirect(url_for('horarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar horario: {str(e)}', 'error')

    clases = Clase.query.filter_by(activa=True).all()
    return render_template('editar_horario.html', horario=horario, clases=clases)

@app.route('/horarios/<int:horario_id>/eliminar')
@login_required
def eliminar_horario(horario_id):
    """Eliminar horario (desactivar)"""
    horario = HorarioSemanal.query.get_or_404(horario_id)
    horario.activo = False
    db.session.commit()
    flash('Horario desactivado exitosamente', 'success')
    return redirect(url_for('horarios'))

@app.route('/calendario')
@login_required
def calendario_unificado():
    """Calendario unificado editable basado en horarios semanales"""
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    clases = Clase.query.filter_by(activa=True).order_by(Clase.nombre).all()
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    
    return render_template('calendario_unificado_editable.html', 
                         horarios=horarios,
                         clases=clases,
                         alumnos=alumnos)

@app.route('/calendario-viejo')
@login_required
def calendario_unificado_viejo():
    """Calendario unificado con actividades periódicas y citas individuales (versión original)"""
    # Obtener parámetros de fecha
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', datetime.now().month, type=int)
    vista = request.args.get('vista', 'mes')  # mes, semana
    
    if vista == 'semana':
        return calendario_semanal(año, mes)
    
    # Obtener sesiones de yogaterapia del mes
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año,
        db.extract('month', SesionYogaterapia.fecha_sesion) == mes
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Calcular datos del calendario
    primer_dia = datetime(año, mes, 1).weekday()
    dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
        dias_mes[1] = 29
    dias_en_mes = dias_mes[mes-1]
    
    # Nombres de meses
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    nombre_mes = nombres_meses[mes-1]
    
    # Generar días del mes para el calendario
    dias_calendario = []
    for dia in range(1, dias_en_mes + 1):
        fecha_actual = datetime(año, mes, dia).date()
        dias_calendario.append(fecha_actual)
    
    # Obtener fecha actual
    today = datetime.now().date()
    
    return render_template('calendario_unificado.html', 
                         año=año, 
                         mes=mes,
                         nombre_mes=nombre_mes,
                         primer_dia=primer_dia,
                         dias_en_mes=dias_en_mes,
                         dias_calendario=dias_calendario,
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios,
                         clases=clases,
                         vista=vista,
                         today=today)

def calendario_semanal(año, mes):
    """Vista semanal del calendario"""
    # Obtener la semana actual
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Obtener sesiones de la semana
    fin_semana = inicio_semana + timedelta(days=6)
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion >= inicio_semana,
        SesionYogaterapia.fecha_sesion <= fin_semana
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Generar días de la semana
    dias_semana = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        dias_semana.append(dia)
    
    return render_template('calendario_semanal.html',
                         dias_semana=dias_semana,
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios,
                         clases=clases,
                         vista='semana')

@app.route('/calendario/anual')
@login_required
def calendario_anual():
    """Vista de calendario anual para agendar sesiones individuales"""
    año = request.args.get('año', datetime.now().year, type=int)
    
    # Obtener todas las sesiones de yogaterapia del año
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Generar datos para cada mes
    meses_datos = []
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    for mes in range(1, 13):
        # Obtener sesiones del mes
        sesiones_mes = [s for s in sesiones_yogaterapia if s.fecha_sesion.month == mes]
        
        # Calcular datos del mes
        primer_dia = datetime(año, mes, 1).weekday()
        dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
            dias_mes[1] = 29
        dias_en_mes = dias_mes[mes-1]
        
        # Generar días del mes
        dias_calendario = []
        for dia in range(1, dias_en_mes + 1):
            fecha_actual = datetime(año, mes, dia).date()
            dias_calendario.append(fecha_actual)
        
        meses_datos.append({
            'mes': mes,
            'nombre': nombres_meses[mes-1],
            'primer_dia': primer_dia,
            'dias_en_mes': dias_en_mes,
            'dias_calendario': dias_calendario,
            'sesiones': sesiones_mes
        })
    
    # Obtener fecha actual
    today = datetime.now().date()
    
    return render_template('calendario_anual.html',
                         año=año,
                         meses_datos=meses_datos,
                         horarios=horarios,
                         clases=clases,
                         today=today)

@app.route('/horarios/historico')
@login_required
def horarios_historico():
    """Vista del histórico de horarios y cambios"""
    # Obtener parámetros de filtro
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    clase_id = request.args.get('clase_id', type=int)
    
    # Consulta base de horarios (incluyendo inactivos para ver histórico)
    query = HorarioSemanal.query
    
    if clase_id:
        query = query.filter_by(clase_id=clase_id)
    
    horarios_historico = query.order_by(HorarioSemanal.fecha_creacion.desc()).all()
    
    # Obtener clases para el filtro
    clases = Clase.query.all()
    
    return render_template('horarios_historico.html', 
                         horarios=horarios_historico,
                         clases=clases,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta,
                         clase_id=clase_id)

@app.route('/asistencias/historico')
@login_required
def asistencias_historico():
    """Vista del histórico de asistencias por clase"""
    # Obtener parámetros de filtro
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    clase_id = request.args.get('clase_id', type=int)
    
    # Construir consulta
    query = db.session.query(Asistencia).join(HorarioSemanal).join(Clase)
    
    if fecha_desde:
        query = query.filter(Asistencia.fecha_clase >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())
    
    if fecha_hasta:
        query = query.filter(Asistencia.fecha_clase <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())
    
    if clase_id:
        query = query.filter(Clase.id == clase_id)
    
    asistencias = query.order_by(Asistencia.fecha_clase.desc()).all()
    
    # Calcular estadísticas por clase
    estadisticas = {}
    if asistencias:
        for asistencia in asistencias:
            clase_nombre = asistencia.horario.clase.nombre
            if clase_nombre not in estadisticas:
                estadisticas[clase_nombre] = {
                    'total_sesiones': 0,
                    'total_asistencias': 0,
                    'alumnos_unicos': set()
                }
            
            estadisticas[clase_nombre]['total_sesiones'] += 1
            if asistencia.presente:
                estadisticas[clase_nombre]['total_asistencias'] += 1
            estadisticas[clase_nombre]['alumnos_unicos'].add(asistencia.alumno_id)
        
        # Convertir sets a conteos
        for clase in estadisticas:
            estadisticas[clase]['alumnos_unicos'] = len(estadisticas[clase]['alumnos_unicos'])
            if estadisticas[clase]['total_sesiones'] > 0:
                estadisticas[clase]['porcentaje_asistencia'] = round(
                    (estadisticas[clase]['total_asistencias'] / estadisticas[clase]['total_sesiones']) * 100, 1
                )
    
    # Obtener clases para el filtro
    clases = Clase.query.all()
    
    return render_template('asistencias_historico.html',
                         asistencias=asistencias,
                         estadisticas=estadisticas,
                         clases=clases,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta,
                         clase_id=clase_id)

# Rutas para Yogaterapia
@app.route('/yogaterapia')
@login_required
def yogaterapia():
    """Página principal de yogaterapia (sesiones de yogaterapia)"""
    sesiones = SesionYogaterapia.query.order_by(SesionYogaterapia.fecha_sesion.desc()).all()
    return render_template('yogaterapia.html', sesiones=sesiones)

@app.route('/yogaterapia/nueva')
@login_required
def nueva_yogaterapia():
    """Formulario para nueva sesión de yogaterapia"""
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    return render_template('nueva_yogaterapia.html', alumnos=alumnos)

@app.route('/yogaterapia/procesar', methods=['POST'])
@login_required
def procesar_yogaterapia_general():
    """Procesar nueva sesión de yogaterapia general"""
    try:
        alumno_id = request.form['alumno_id']
        alumno = Alumno.query.get_or_404(alumno_id)
        
        # Procesar horas
        hora_inicio = None
        hora_fin = None
        if request.form.get('hora_inicio'):
            hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
        if request.form.get('hora_fin'):
            hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
        
        # Verificar conflicto de horarios
        fecha_sesion = datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date()
        if hora_inicio and hora_fin:
            conflicto, info_conflicto = verificar_conflicto_horario(fecha_sesion, hora_inicio, hora_fin)
            if conflicto:
                flash(f'⚠️ {info_conflicto["mensaje"]}', 'warning')
                return redirect(url_for('nueva_yogaterapia'))
        
        sesion = SesionYogaterapia(
            alumno_id=alumno_id,
            fecha_sesion=datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date(),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_minutos=int(request.form.get('duracion_minutos', 60)),
            tipo_sesion=request.form.get('tipo_sesion', 'individual'),
            motivo_consulta=request.form.get('motivo_consulta'),
            objetivos_terapeuticos=request.form.get('objetivos_terapeuticos'),
            tecnicas_aplicadas=request.form.get('tecnicas_aplicadas'),
            posturas_trabajadas=request.form.get('posturas_trabajadas'),
            respiracion_pranayama=request.form.get('respiracion_pranayama'),
            meditacion_relajacion=request.form.get('meditacion_relajacion'),
            estado_inicial=request.form.get('estado_inicial'),
            respuesta_sesion=request.form.get('respuesta_sesion'),
            estado_final=request.form.get('estado_final'),
            observaciones_terapeuta=request.form.get('observaciones_terapeuta'),
            recomendaciones_casa=request.form.get('recomendaciones_casa'),
            proxima_sesion=request.form.get('proxima_sesion'),
            instructor=request.form.get('instructor', 'Minouche'),
            precio=float(request.form.get('precio', 50.00)),
            pagado='pagado' in request.form,
            metodo_pago=request.form.get('metodo_pago')
        )
        
        db.session.add(sesion)
        db.session.flush()
        
        # Manejar archivos subidos
        archivos = request.files.getlist('archivos')
        for archivo in archivos:
            if archivo and archivo.filename:
                # Crear directorio para archivos de yogaterapia
                upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{archivo.filename}"
                filepath = os.path.join(upload_dir, filename)
                
                # Guardar archivo
                archivo.save(filepath)
                
                # Crear registro en base de datos
                archivo_db = ArchivoYogaterapia(
                    sesion_yogaterapia_id=sesion.id,
                    nombre_archivo=archivo.filename,
                    ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                    tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                    tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                )
                db.session.add(archivo_db)
        
        # Si está pagado, crear registro de pago
        if sesion.pagado:
            pago = Pago(
                alumno_id=alumno_id,
                fecha_clase=sesion.fecha_sesion,
                monto=sesion.precio,
                tipo_pago='yogaterapia',
                descripcion=f'Yogaterapia - {sesion.tipo_sesion}',
                metodo_pago=sesion.metodo_pago
            )
            db.session.add(pago)
        
        db.session.commit()
        flash(f'¡Sesión de yogaterapia registrada exitosamente para {alumno.nombre} {alumno.apellido}!', 'success')
        return redirect(url_for('yogaterapia'))
        
    except Exception as e:
        flash(f'Error al registrar sesión: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('nueva_yogaterapia'))

@app.route('/yogaterapia/<int:sesion_id>')
@login_required
def ver_sesion_yogaterapia(sesion_id):
    """Ver detalles de una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    archivos = ArchivoYogaterapia.query.filter_by(sesion_yogaterapia_id=sesion_id).all()
    return render_template('ver_sesion_yogaterapia.html', sesion=sesion, archivos=archivos)

@app.route('/yogaterapia/<int:sesion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_sesion_yogaterapia(sesion_id):
    """Editar una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos de la sesión
            sesion.fecha_sesion = datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date()
            
            # Procesar horas
            hora_inicio_nueva = None
            hora_fin_nueva = None
            if request.form.get('hora_inicio'):
                hora_inicio_nueva = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            if request.form.get('hora_fin'):
                hora_fin_nueva = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            
            # Verificar conflicto de horarios
            if hora_inicio_nueva and hora_fin_nueva:
                conflicto, sesion_conflicto = verificar_conflicto_horario(fecha_sesion, hora_inicio_nueva, hora_fin_nueva, sesion_id)
                if conflicto:
                    flash(f'⚠️ Conflicto de horario detectado! Ya existe una cita de {sesion_conflicto.hora_inicio.strftime("%H:%M")} a {sesion_conflicto.hora_fin.strftime("%H:%M")} con {sesion_conflicto.alumno.nombre} {sesion_conflicto.alumno.apellido}', 'warning')
                    return redirect(url_for('editar_sesion_yogaterapia', sesion_id=sesion_id))
            
            sesion.hora_inicio = hora_inicio_nueva
            sesion.hora_fin = hora_fin_nueva
            
            sesion.duracion_minutos = int(request.form.get('duracion_minutos', 75))
            sesion.tipo_sesion = request.form.get('tipo_sesion', 'individual')
            sesion.motivo_consulta = request.form.get('motivo_consulta')
            sesion.objetivos_terapeuticos = request.form.get('objetivos_terapeuticos')
            sesion.tecnicas_aplicadas = request.form.get('tecnicas_aplicadas')
            sesion.posturas_trabajadas = request.form.get('posturas_trabajadas')
            sesion.respiracion_pranayama = request.form.get('respiracion_pranayama')
            sesion.meditacion_relajacion = request.form.get('meditacion_relajacion')
            sesion.estado_inicial = request.form.get('estado_inicial')
            sesion.respuesta_sesion = request.form.get('respuesta_sesion')
            sesion.estado_final = request.form.get('estado_final')
            sesion.observaciones_terapeuta = request.form.get('observaciones_terapeuta')
            sesion.recomendaciones_casa = request.form.get('recomendaciones_casa')
            sesion.proxima_sesion = request.form.get('proxima_sesion')
            sesion.instructor = request.form.get('instructor', 'Minouche')
            sesion.precio = float(request.form.get('precio', 50.00))
            sesion.pagado = 'pagado' in request.form
            sesion.metodo_pago = request.form.get('metodo_pago')
            
            # Manejar archivos adicionales
            archivos = request.files.getlist('archivos')
            for archivo in archivos:
                if archivo and archivo.filename:
                    upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{archivo.filename}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    archivo.save(filepath)
                    
                    archivo_db = ArchivoYogaterapia(
                        sesion_yogaterapia_id=sesion.id,
                        nombre_archivo=archivo.filename,
                        ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                        tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                        tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    )
                    db.session.add(archivo_db)
            
            db.session.commit()
            flash('¡Sesión de yogaterapia actualizada exitosamente!', 'success')
            return redirect(url_for('ver_sesion_yogaterapia', sesion_id=sesion_id))
            
        except Exception as e:
            flash(f'Error al actualizar sesión: {str(e)}', 'error')
            db.session.rollback()
    
    archivos = ArchivoYogaterapia.query.filter_by(sesion_yogaterapia_id=sesion_id).all()
    return render_template('editar_sesion_yogaterapia.html', sesion=sesion, archivos=archivos)

@app.route('/api/citas/<fecha>')
@login_required
def obtener_citas_fecha(fecha):
    """API para obtener citas de una fecha específica (para el calendario)"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        dia_semana = fecha_obj.weekday()
        
        # Obtener sesiones de yogaterapia
        citas = SesionYogaterapia.query.filter(
            SesionYogaterapia.fecha_sesion == fecha_obj,
            SesionYogaterapia.hora_inicio.isnot(None)
        ).order_by(SesionYogaterapia.hora_inicio).all()
        
        # Obtener horarios semanales para ese día
        horarios_semanal = HorarioSemanal.query.filter(
            HorarioSemanal.dia_semana == dia_semana,
            HorarioSemanal.activo == True
        ).all()
        
        citas_data = []
        
        # Agregar sesiones de yogaterapia
        for cita in citas:
            citas_data.append({
                'id': cita.id,
                'alumno': f"{cita.alumno.nombre} {cita.alumno.apellido}",
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_fin': cita.hora_fin.strftime('%H:%M') if cita.hora_fin else None,
                'duracion': cita.duracion_minutos,
                'precio': cita.precio,
                'pagado': cita.pagado,
                'tipo': 'yogaterapia',
                'color': '#8B5FBF'
            })
        
        # Agregar clases grupales
        for horario in horarios_semanal:
            citas_data.append({
                'id': f"grupal_{horario.id}",
                'alumno': horario.clase.nombre,
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
                'duracion': horario.clase.duracion_minutos,
                'precio': horario.clase.precio,
                'pagado': True,
                'tipo': 'clase_grupal',
                'color': '#28a745'
            })
        
        # Ordenar por hora de inicio
        citas_data.sort(key=lambda x: x['hora_inicio'])
        
        return jsonify(citas_data)
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400

@app.route('/api/verificar-conflicto', methods=['POST'])
@login_required
def verificar_conflicto_api():
    """API para verificar conflictos de horario en tiempo real"""
    try:
        data = request.get_json()
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        sesion_id = data.get('sesion_id')
        
        conflicto, info_conflicto = verificar_conflicto_horario(fecha, hora_inicio, hora_fin, sesion_id)
        
        return jsonify({
            'conflicto': conflicto,
            'mensaje': info_conflicto['mensaje'] if conflicto else None,
            'tipo': info_conflicto['tipo'] if conflicto else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/yogaterapia/<int:sesion_id>/archivos/eliminar/<int:archivo_id>', methods=['POST'])
@login_required
def eliminar_archivo_yogaterapia(sesion_id, archivo_id):
    """Eliminar un archivo de yogaterapia"""
    try:
        archivo = ArchivoYogaterapia.query.filter_by(
            id=archivo_id, 
            sesion_yogaterapia_id=sesion_id
        ).first_or_404()
        
        # Eliminar archivo físico
        if os.path.exists(archivo.ruta_archivo):
            os.remove(archivo.ruta_archivo)
        
        # Eliminar registro de base de datos
        db.session.delete(archivo)
        db.session.commit()
        
        flash('Archivo eliminado correctamente', 'success')
        return redirect(url_for('ver_sesion_yogaterapia', sesion_id=sesion_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar archivo: {str(e)}', 'error')
        return redirect(url_for('ver_sesion_yogaterapia', sesion_id=sesion_id))

@app.route('/yogaterapia/<int:sesion_id>/archivos/agregar', methods=['POST'])
@login_required
def agregar_archivo_yogaterapia(sesion_id):
    """Agregar archivos a una sesión de yogaterapia"""
    try:
        sesion = SesionYogaterapia.query.get_or_404(sesion_id)
        
        archivos = request.files.getlist('archivos')
        archivos_agregados = 0
        
        for archivo in archivos:
            if archivo and archivo.filename:
                # Crear directorio para archivos de yogaterapia
                upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{archivo.filename}"
                filepath = os.path.join(upload_dir, filename)
                
                # Guardar archivo
                archivo.save(filepath)
                
                # Crear registro en base de datos
                archivo_db = ArchivoYogaterapia(
                    sesion_yogaterapia_id=sesion.id,
                    nombre_archivo=archivo.filename,
                    ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                    tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                    tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                )
                db.session.add(archivo_db)
                archivos_agregados += 1
        
        db.session.commit()
        flash(f'{archivos_agregados} archivo(s) agregado(s) correctamente', 'success')
        return redirect(url_for('ver_sesion_yogaterapia', sesion_id=sesion_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar archivos: {str(e)}', 'error')
        return redirect(url_for('ver_sesion_yogaterapia', sesion_id=sesion_id))

@app.route('/yogaterapia/<int:sesion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_sesion_yogaterapia(sesion_id):
    """Eliminar una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    try:
        # Eliminar archivos asociados
        for archivo in sesion.archivos:
            try:
                if os.path.exists(archivo.ruta_archivo):
                    os.remove(archivo.ruta_archivo)
            except Exception as e:
                print(f"Error eliminando archivo {archivo.ruta_archivo}: {e}")
        
        # Eliminar la sesión
        db.session.delete(sesion)
        db.session.commit()
        
        flash(f'✅ Sesión de {sesion.alumno.nombre} {sesion.alumno.apellido} eliminada exitosamente', 'success')
        return redirect(url_for('yogaterapia'))
        
    except Exception as e:
        flash(f'Error al eliminar sesión: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('yogaterapia'))

@app.route('/yogaterapia/<int:sesion_id>/marcar_pagado', methods=['POST'])
@login_required
def marcar_sesion_pagada(sesion_id):
    """Marcar una sesión como pagada"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    try:
        sesion.pagado = True
        sesion.metodo_pago = request.form.get('metodo_pago', 'efectivo')
        
        # Crear registro de pago si no existe
        # Para yogaterapia no creamos registro de pago automáticamente
        # ya que no está asociado a un alumno específico
        
        db.session.commit()
        flash('¡Sesión marcada como pagada!', 'success')
        
    except Exception as e:
        flash(f'Error al marcar como pagada: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('yogaterapia'))

@app.route('/alumnos/<int:alumno_id>/yogaterapia/nueva', methods=['GET', 'POST'])
@login_required
def nueva_yogaterapia_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            # Procesar horas
            hora_inicio = None
            hora_fin = None
            if request.form.get('hora_inicio'):
                hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            if request.form.get('hora_fin'):
                hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            
            sesion = SesionYogaterapia(
                alumno_id=alumno_id,
                fecha_sesion=datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date(),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                duracion_minutos=int(request.form.get('duracion_minutos', 60)),
                tipo_sesion=request.form.get('tipo_sesion', 'individual'),
                motivo_consulta=request.form.get('motivo_consulta'),
                objetivos_terapeuticos=request.form.get('objetivos_terapeuticos'),
                tecnicas_aplicadas=request.form.get('tecnicas_aplicadas'),
                posturas_trabajadas=request.form.get('posturas_trabajadas'),
                respiracion_pranayama=request.form.get('respiracion_pranayama'),
                meditacion_relajacion=request.form.get('meditacion_relajacion'),
                estado_inicial=request.form.get('estado_inicial'),
                respuesta_sesion=request.form.get('respuesta_sesion'),
                estado_final=request.form.get('estado_final'),
                observaciones_terapeuta=request.form.get('observaciones_terapeuta'),
                recomendaciones_casa=request.form.get('recomendaciones_casa'),
                proxima_sesion=request.form.get('proxima_sesion'),
                instructor=request.form.get('instructor', 'Minouche'),
                precio=float(request.form.get('precio', 45.00)),
                pagado='pagado' in request.form,
                metodo_pago=request.form.get('metodo_pago')
            )
            
            db.session.add(sesion)
            db.session.flush()
            
            # Manejar archivos subidos
            archivos = request.files.getlist('archivos')
            for archivo in archivos:
                if archivo and archivo.filename:
                    # Crear directorio para archivos de yogaterapia
                    upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generar nombre único para el archivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{archivo.filename}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    # Guardar archivo
                    archivo.save(filepath)
                    
                    # Crear registro en base de datos
                    archivo_db = ArchivoYogaterapia(
                        sesion_yogaterapia_id=sesion.id,
                        nombre_archivo=archivo.filename,
                        ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                        tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                        tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    )
                    db.session.add(archivo_db)
            
            # Si está pagado, crear registro de pago
            if sesion.pagado:
                pago = Pago(
                    alumno_id=alumno_id,
                    fecha_clase=sesion.fecha_sesion,
                    monto=sesion.precio,
                    tipo_pago='yogaterapia',
                    descripcion=f'Yogaterapia - {sesion.tipo_sesion}',
                    metodo_pago=sesion.metodo_pago
                )
                db.session.add(pago)
            
            db.session.commit()
            flash(f'¡Sesión de yogaterapia registrada exitosamente para {alumno.nombre} {alumno.apellido}!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno_id))
            
        except Exception as e:
            flash(f'Error al registrar sesión: {str(e)}', 'error')
            db.session.rollback()
    
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    return render_template('nueva_yogaterapia.html', alumno=alumno, alumnos=alumnos, from_student=True)

# RUTAS PARA GESTIÓN ECONÓMICA

@app.route('/economia/historico')
@login_required
def economia_historico():
    """Dashboard principal de contabilidad con períodos"""
    # Obtener parámetros de período
    periodo = request.args.get('periodo', 'mes_actual')
    año = int(request.args.get('año', date.today().year))
    mes = int(request.args.get('mes', date.today().month))
    
    # Calcular fechas según el período
    if periodo == 'mes_actual':
        fecha_inicio = date(año, mes, 1)
        if mes == 12:
            fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
    elif periodo == 'trimestre':
        trimestre = ((mes - 1) // 3) + 1
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_inicio = date(año, mes_inicio, 1)
        if trimestre == 4:
            fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(año, mes_inicio + 3, 1) - timedelta(days=1)
    elif periodo == 'año':
        fecha_inicio = date(año, 1, 1)
        fecha_fin = date(año, 12, 31)
    else:  # mes_actual por defecto
        fecha_inicio = date(año, mes, 1)
        fecha_fin = date(año, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(año, 12, 31)
    
    # Calcular ingresos del período
    ingresos_cuotas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'cuota',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    ingresos_matriculas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'matricula',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    ingresos_clases_sueltas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'clase_suelta',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    total_ingresos = ingresos_cuotas + ingresos_matriculas + ingresos_clases_sueltas
    
    # Calcular gastos del período
    total_gastos = db.session.query(db.func.sum(GastoMensual.importe)).filter(
        GastoMensual.fecha >= fecha_inicio,
        GastoMensual.fecha <= fecha_fin
    ).scalar() or 0
    
    # Balance
    balance = total_ingresos - total_gastos
    
    # Calcular facturas pendientes
    facturas_pendientes = FacturaProveedor.query.filter_by(estado='pendiente').count()
    
    # Calcular gastos pendientes (simplificado)
    gastos_pendientes = 0  # Por ahora 0, se puede implementar lógica más compleja
    
    # Desglose de ingresos
    ingresos_detalle = {
        'cuotas': ingresos_cuotas,
        'matriculas': ingresos_matriculas,
        'clases_sueltas': ingresos_clases_sueltas,
        'yogaterapia': 0  # Se puede calcular si hay datos de yogaterapia
    }
    
    # Desglose de gastos
    gastos_detalle = {
        'gastos_mensuales': total_gastos,
        'facturas': facturas_pendientes,
        'gastos_fijos': 0  # Se puede calcular si hay gastos fijos
    }
    
    return render_template('economia/dashboard_simple.html',
                         periodo=periodo,
                         año=año,
                         mes=mes,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         ingresos_cuotas=ingresos_cuotas,
                         ingresos_matriculas=ingresos_matriculas,
                         ingresos_clases_sueltas=ingresos_clases_sueltas,
                         ingresos_total=total_ingresos,
                         total_ingresos=total_ingresos,
                         total_gastos=total_gastos,
                         balance=balance,
                         facturas_pendientes=facturas_pendientes,
                         gastos_pendientes=gastos_pendientes,
                         ingresos_detalle=ingresos_detalle,
                         gastos_detalle=gastos_detalle)

@app.route('/gastos-mensuales')
@login_required
def gastos_mensuales():
    """Vista de gastos mensuales"""
    gastos = GastoMensual.query.order_by(GastoMensual.fecha.desc()).all()
    
    # Calcular ingresos del mes actual
    hoy = date.today()
    fecha_inicio = date(hoy.year, hoy.month, 1)
    if hoy.month == 12:
        fecha_fin = date(hoy.year + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    ingresos_mes = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    # Calcular gastos del mes actual
    gastos_mes = db.session.query(db.func.sum(GastoMensual.importe)).filter(
        GastoMensual.fecha >= fecha_inicio,
        GastoMensual.fecha <= fecha_fin
    ).scalar() or 0
    
    # Calcular balance del mes
    balance_mes = ingresos_mes - gastos_mes
    
    return render_template('gastos_mensuales.html', gastos=gastos, ingresos_mes=ingresos_mes, gastos_mes=gastos_mes, balance_mes=balance_mes)

@app.route('/agregar_gasto_mensual', methods=['POST'])
@login_required
def agregar_gasto_mensual():
    """Agregar nuevo gasto mensual"""
    try:
        gasto = GastoMensual(
            fecha=datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date(),
            concepto=request.form.get('concepto'),
            categoria=request.form.get('categoria'),
            importe=float(request.form.get('importe')),
            pagado='pagado' in request.form,
            metodo_pago=request.form.get('metodo_pago', ''),
            notas=request.form.get('notas', '')
        )
        
        db.session.add(gasto)
        db.session.commit()
        flash('Gasto mensual agregado exitosamente', 'success')
        return redirect(url_for('gastos_mensuales'))
        
    except Exception as e:
        flash(f'Error al agregar gasto: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('gastos_mensuales'))

@app.route('/proveedores')
@login_required
def proveedores():
    """Lista de proveedores"""
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/proveedores.html', proveedores=proveedores)

@app.route('/facturas')
@login_required
def facturas():
    """Lista de facturas"""
    facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
    return render_template('economia/facturas.html', facturas=facturas)

@app.route('/facturas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    """Crear nueva factura"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            numero_factura = request.form.get('numero_factura')
            proveedor_id = request.form.get('proveedor_id')
            categoria_id = request.form.get('categoria_id')
            fecha_factura = datetime.strptime(request.form.get('fecha_factura'), '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(request.form.get('fecha_vencimiento'), '%Y-%m-%d').date() if request.form.get('fecha_vencimiento') else None
            importe_sin_iva = float(request.form.get('importe_sin_iva'))
            iva = float(request.form.get('iva', 21.0))
            descripcion = request.form.get('descripcion', '')
            notas = request.form.get('notas', '')
            
            # Calcular importe total
            importe_total = importe_sin_iva * (1 + iva / 100)
            
            # Crear factura
            factura = FacturaProveedor(
                numero_factura=numero_factura,
                proveedor_id=proveedor_id,
                categoria_id=categoria_id,
                fecha_factura=fecha_factura,
                fecha_vencimiento=fecha_vencimiento,
                importe_sin_iva=importe_sin_iva,
                iva=iva,
                importe_total=importe_total,
                descripcion=descripcion,
                notas=notas
            )
            
            db.session.add(factura)
            db.session.commit()
            flash('Factura creada exitosamente', 'success')
            return redirect(url_for('facturas'))
            
        except Exception as e:
            flash(f'Error al crear factura: {str(e)}', 'error')
            db.session.rollback()
    
    # Obtener datos para el formulario
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    
    return render_template('economia/nueva_factura.html', 
                         proveedores=proveedores, 
                         categorias=categorias,
                         date=date)

@app.route('/facturas/<int:factura_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_factura(factura_id):
    """Editar factura existente"""
    factura = FacturaProveedor.query.get_or_404(factura_id)
    
    if request.method == 'POST':
        try:
            factura.numero_factura = request.form.get('numero_factura')
            factura.proveedor_id = request.form.get('proveedor_id')
            factura.categoria_id = request.form.get('categoria_id')
            factura.fecha_factura = datetime.strptime(request.form.get('fecha_factura'), '%Y-%m-%d').date()
            factura.fecha_vencimiento = datetime.strptime(request.form.get('fecha_vencimiento'), '%Y-%m-%d').date() if request.form.get('fecha_vencimiento') else None
            factura.importe_sin_iva = float(request.form.get('importe_sin_iva'))
            factura.iva = float(request.form.get('iva', 21.0))
            factura.importe_total = factura.importe_sin_iva * (1 + factura.iva / 100)
            factura.descripcion = request.form.get('descripcion', '')
            factura.notas = request.form.get('notas', '')
            factura.estado = request.form.get('estado', 'pendiente')
            factura.metodo_pago = request.form.get('metodo_pago', '')
            
            if factura.estado == 'pagada' and not factura.fecha_pago:
                factura.fecha_pago = date.today()
            
            db.session.commit()
            flash('Factura actualizada exitosamente', 'success')
            return redirect(url_for('facturas'))
            
        except Exception as e:
            flash(f'Error al actualizar factura: {str(e)}', 'error')
            db.session.rollback()
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    
    return render_template('economia/editar_factura.html', 
                         factura=factura,
                         proveedores=proveedores, 
                         categorias=categorias)

@app.route('/facturas/<int:factura_id>/marcar_pagada', methods=['POST'])
@login_required
def marcar_factura_pagada(factura_id):
    """Marcar factura como pagada"""
    try:
        factura = FacturaProveedor.query.get_or_404(factura_id)
        factura.estado = 'pagada'
        factura.fecha_pago = date.today()
        factura.metodo_pago = request.form.get('metodo_pago', 'transferencia')
        
        db.session.commit()
        flash('Factura marcada como pagada', 'success')
    except Exception as e:
        flash(f'Error al marcar factura: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('facturas'))

@app.route('/facturas/<int:factura_id>/eliminar', methods=['POST'])
@login_required
def eliminar_factura(factura_id):
    """Eliminar factura"""
    try:
        factura = FacturaProveedor.query.get_or_404(factura_id)
        db.session.delete(factura)
        db.session.commit()
        flash('Factura eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar factura: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('facturas'))

@app.route('/gastos-fijos')
@login_required
def gastos_fijos():
    """Lista de gastos fijos"""
    gastos = GastoFijo.query.filter_by(activo=True).order_by(GastoFijo.nombre).all()
    return render_template('economia/gastos_fijos.html', gastos=gastos)

@app.route('/gastos-fijos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_gasto_fijo():
    """Crear nuevo gasto fijo"""
    if request.method == 'POST':
        try:
            gasto = GastoFijo(
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion', ''),
                categoria_id=request.form.get('categoria_id'),
                proveedor_id=request.form.get('proveedor_id') or None,
                importe=float(request.form.get('importe')),
                frecuencia=request.form.get('frecuencia', 'mensual'),
                dia_cargo=int(request.form.get('dia_cargo', 1)),
                fecha_inicio=datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date(),
                fecha_fin=datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
                notas=request.form.get('notas', '')
            )
            
            db.session.add(gasto)
            db.session.commit()
            flash('Gasto fijo creado exitosamente', 'success')
            return redirect(url_for('gastos_fijos'))
            
        except Exception as e:
            flash(f'Error al crear gasto fijo: {str(e)}', 'error')
            db.session.rollback()
    
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    fecha_hoy = date.today()
    return render_template('economia/nuevo_gasto_fijo.html', categorias=categorias, proveedores=proveedores, fecha_hoy=fecha_hoy)

@app.route('/gastos-fijos/<int:gasto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_gasto_fijo(gasto_id):
    """Editar gasto fijo existente"""
    gasto = GastoFijo.query.get_or_404(gasto_id)
    
    if request.method == 'POST':
        try:
            gasto.nombre = request.form.get('nombre')
            gasto.descripcion = request.form.get('descripcion', '')
            gasto.categoria_id = request.form.get('categoria_id')
            gasto.proveedor_id = request.form.get('proveedor_id') or None
            gasto.importe = float(request.form.get('importe'))
            gasto.frecuencia = request.form.get('frecuencia', 'mensual')
            gasto.dia_cargo = int(request.form.get('dia_cargo', 1))
            gasto.fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
            gasto.fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date() if request.form.get('fecha_fin') else None
            gasto.notas = request.form.get('notas', '')
            gasto.activo = 'activo' in request.form
            
            db.session.commit()
            flash('Gasto fijo actualizado exitosamente', 'success')
            return redirect(url_for('gastos_fijos'))
            
        except Exception as e:
            flash(f'Error al actualizar gasto fijo: {str(e)}', 'error')
            db.session.rollback()
    
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/editar_gasto_fijo.html', gasto=gasto, categorias=categorias, proveedores=proveedores)

@app.route('/gastos-fijos/<int:gasto_id>/eliminar', methods=['POST'])
@login_required
def eliminar_gasto_fijo(gasto_id):
    """Eliminar gasto fijo"""
    try:
        gasto = GastoFijo.query.get_or_404(gasto_id)
        gasto.activo = False
        db.session.commit()
        flash('Gasto fijo desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar gasto fijo: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('gastos_fijos'))

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form.get('nombre'),
                cif_nif=request.form.get('cif_nif', ''),
                direccion=request.form.get('direccion', ''),
                telefono=request.form.get('telefono', ''),
                email=request.form.get('email', ''),
                contacto_principal=request.form.get('contacto_principal', ''),
                notas=request.form.get('notas', '')
            )
            
            db.session.add(proveedor)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            flash(f'Error al crear proveedor: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('economia/nuevo_proveedor.html')

@app.route('/proveedores/<int:proveedor_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_proveedor(proveedor_id):
    """Editar proveedor existente"""
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form.get('nombre')
            proveedor.cif_nif = request.form.get('cif_nif', '')
            proveedor.direccion = request.form.get('direccion', '')
            proveedor.telefono = request.form.get('telefono', '')
            proveedor.email = request.form.get('email', '')
            proveedor.contacto_principal = request.form.get('contacto_principal', '')
            proveedor.notas = request.form.get('notas', '')
            proveedor.activo = 'activo' in request.form
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('economia/editar_proveedor.html', proveedor=proveedor)

@app.route('/proveedores/<int:proveedor_id>/eliminar', methods=['POST'])
@login_required
def eliminar_proveedor(proveedor_id):
    """Eliminar proveedor"""
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        proveedor.activo = False
        db.session.commit()
        flash('Proveedor desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar proveedor: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('proveedores'))

# RUTAS DE EXPORTACIÓN Y REPORTES

@app.route('/exportar/<tipo>')
@login_required
def exportar_datos(tipo):
    """Exportar datos a Excel"""
    try:
        if tipo == 'facturas':
            facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
            return exportar_facturas_excel(facturas)
        elif tipo == 'gastos-fijos':
            gastos = GastoFijo.query.filter_by(activo=True).all()
            return exportar_gastos_fijos_excel(gastos)
        elif tipo == 'proveedores':
            proveedores = Proveedor.query.filter_by(activo=True).all()
            return exportar_proveedores_excel(proveedores)
        elif tipo == 'ingresos':
            return exportar_ingresos_excel()
        else:
            flash('Tipo de exportación no válido', 'error')
            return redirect(url_for('economia'))
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'error')
        return redirect(url_for('economia'))

@app.route('/reporte-contabilidad-pdf')
@login_required
def reporte_contabilidad_pdf():
    """Generar reporte de contabilidad en PDF"""
    try:
        # Obtener parámetros
        periodo = request.args.get('periodo', 'mes_actual')
        año = int(request.args.get('año', date.today().year))
        mes = int(request.args.get('mes', date.today().month))
        
        # Calcular fechas
        if periodo == 'mes_actual':
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
        elif periodo == 'año':
            fecha_inicio = date(año, 1, 1)
            fecha_fin = date(año, 12, 31)
        else:
            fecha_inicio = date(año, mes, 1)
            fecha_fin = date(año, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(año, 12, 31)
        
        # Obtener datos
        facturas = FacturaProveedor.query.filter(
            FacturaProveedor.fecha_factura >= fecha_inicio,
            FacturaProveedor.fecha_factura <= fecha_fin
        ).all()
        
        gastos_fijos = GastoFijo.query.filter_by(activo=True).all()
        
        ingresos = db.session.query(db.func.sum(Pago.monto)).filter(
            Pago.fecha_creacion >= fecha_inicio,
            Pago.fecha_creacion <= fecha_fin
        ).scalar() or 0
        
        return generar_reporte_pdf(facturas, gastos_fijos, ingresos, fecha_inicio, fecha_fin)
        
    except Exception as e:
        flash(f'Error al generar reporte PDF: {str(e)}', 'error')
        return redirect(url_for('economia'))

# RUTAS DE CONFIGURACIÓN

@app.route('/configuracion')
@login_required
def configuracion():
    configuraciones = Configuracion.query.all()
    config_dict = {config.clave: config.valor for config in configuraciones}
    clases = Clase.query.order_by(Clase.nombre).all()
    tarifas = Tarifa.query.all()
    return render_template('configuracion.html', config=config_dict, clases=clases, tarifas=tarifas)

@app.route('/configuracion/guardar', methods=['POST'])
@login_required
def guardar_configuracion():
    try:
        # Manejar subida de logo
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                # Crear directorio para logos
                logo_dir = os.path.join('static', 'images')
                os.makedirs(logo_dir, exist_ok=True)
                
                # Generar nombre único para el logo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"logo_{timestamp}.{logo_file.filename.split('.')[-1]}"
                filepath = os.path.join(logo_dir, filename)
                
                # Guardar archivo
                logo_file.save(filepath)
                
                # Actualizar configuración con la ruta del logo
                config_logo = Configuracion.query.filter_by(clave='logo_escuela').first()
                if config_logo:
                    config_logo.valor = f"images/{filename}"
                else:
                    config_logo = Configuracion(
                        clave='logo_escuela',
                        valor=f"images/{filename}",
                        descripcion='Logo de la escuela'
                    )
                    db.session.add(config_logo)
        
        configuraciones = [
            # Tarifas
            ('precio_clase_suelta', request.form.get('precio_clase_suelta', '15.00'), 'Precio por clase suelta'),
            ('precio_1_clase_semanal', request.form.get('precio_1_clase_semanal', '40.00'), 'Precio 1 clase por semana'),
            ('precio_2_clases_semanal', request.form.get('precio_2_clases_semanal', '70.00'), 'Precio 2 clases por semana'),
            ('precio_tarifa_plana', request.form.get('precio_tarifa_plana', '90.00'), 'Precio tarifa plana'),
            ('precio_1_clase_bimensual', request.form.get('precio_1_clase_bimensual', '75.00'), 'Precio 1 clase bimensual'),
            ('precio_2_clases_bimensual', request.form.get('precio_2_clases_bimensual', '135.00'), 'Precio 2 clases bimensual'),
            ('precio_matricula', request.form.get('precio_matricula', '25.00'), 'Precio de matrícula anual'),
            ('precio_yogaterapia_individual', request.form.get('precio_yogaterapia_individual', '50.00'), 'Precio yogaterapia individual'),
            ('precio_yogaterapia_pareja', request.form.get('precio_yogaterapia_pareja', '70.00'), 'Precio yogaterapia en pareja'),
            
            # Información de la escuela
            ('nombre_escuela', request.form.get('nombre_escuela', 'ATMA SUDDHI'), 'Nombre de la escuela'),
            ('direccion_escuela', request.form.get('direccion_escuela', ''), 'Dirección de la escuela'),
            ('telefono_escuela', request.form.get('telefono_escuela', ''), 'Teléfono de contacto'),
            ('email_escuela', request.form.get('email_escuela', ''), 'Email de contacto'),
            ('web_escuela', request.form.get('web_escuela', 'http://atmasuddhi.es'), 'Página web'),
            
            # Instructor principal
            ('nombre_instructora', request.form.get('nombre_instructora', 'Minouche'), 'Nombre de la instructora principal'),
            ('email_instructora', request.form.get('email_instructora', ''), 'Email de la instructora'),
            ('telefono_instructora', request.form.get('telefono_instructora', ''), 'Teléfono de la instructora'),
            
            # Configuración de pagos
            ('numero_cuenta', request.form.get('numero_cuenta', ''), 'Número de cuenta bancaria'),
            ('cif_escuela', request.form.get('cif_escuela', ''), 'CIF de la escuela'),
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

# RUTAS DE GESTIÓN DE TIPOS DE CLASE

@app.route('/configuracion/tipos-clase')
@login_required
def tipos_clase():
    """Vista de gestión de tipos de clase"""
    tipos = TipoClase.query.order_by(TipoClase.orden, TipoClase.nombre).all()
    return render_template('configuracion/tipos_clase.html', tipos=tipos)

@app.route('/configuracion/tipos-clase/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_tipo_clase():
    """Crear nuevo tipo de clase"""
    if request.method == 'POST':
        try:
            tipo = TipoClase(
                codigo=request.form['codigo'],
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion'),
                precio=float(request.form['precio']),
                frecuencia=request.form.get('frecuencia', 'mensual'),
                color=request.form.get('color', '#007bff'),
                orden=int(request.form.get('orden', 0))
            )
            db.session.add(tipo)
            db.session.commit()
            flash('¡Tipo de clase creado exitosamente!', 'success')
            return redirect(url_for('tipos_clase'))
        except Exception as e:
            flash(f'Error al crear tipo de clase: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('configuracion/nuevo_tipo_clase.html')

@app.route('/configuracion/tipos-clase/<int:tipo_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_tipo_clase(tipo_id):
    """Editar tipo de clase existente"""
    tipo = TipoClase.query.get_or_404(tipo_id)
    
    if request.method == 'POST':
        try:
            tipo.codigo = request.form['codigo']
            tipo.nombre = request.form['nombre']
            tipo.descripcion = request.form.get('descripcion')
            tipo.precio = float(request.form['precio'])
            tipo.frecuencia = request.form.get('frecuencia', 'mensual')
            tipo.color = request.form.get('color', '#007bff')
            tipo.orden = int(request.form.get('orden', 0))
            
            db.session.commit()
            flash('¡Tipo de clase actualizado exitosamente!', 'success')
            return redirect(url_for('tipos_clase'))
        except Exception as e:
            flash(f'Error al actualizar tipo de clase: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('configuracion/editar_tipo_clase.html', tipo=tipo)

@app.route('/configuracion/tipos-clase/<int:tipo_id>/toggle', methods=['POST'])
@login_required
def toggle_tipo_clase(tipo_id):
    """Activar/desactivar tipo de clase"""
    try:
        tipo = TipoClase.query.get_or_404(tipo_id)
        tipo.activo = not tipo.activo
        db.session.commit()
        
        estado = "activado" if tipo.activo else "desactivado"
        return jsonify({'success': True, 'message': f'Tipo de clase {estado} exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# RUTAS DE BACKUP Y EXPORTACIÓN

@app.route('/backup')
@login_required
def backup():
    """Página de gestión de backups"""
    return render_template('backup.html')

@app.route('/backup/crear', methods=['POST'])
@login_required
def crear_backup():
    """Crear backup de la base de datos"""
    try:
        import shutil
        from datetime import datetime
        
        # Crear backup simple copiando la base de datos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'yoga_school_backup_{timestamp}.db'
        backup_path = os.path.join('backups', filename)
        
        # Asegurar que existe el directorio
        os.makedirs('backups', exist_ok=True)
        
        # Copiar la base de datos
        if os.path.exists('yoga_school.db'):
            shutil.copy2('yoga_school.db', backup_path)
            flash(f'Backup creado exitosamente: {filename}', 'success')
        else:
            flash('Error: Base de datos no encontrada', 'error')
            
    except Exception as e:
        flash(f'Error al crear backup: {str(e)}', 'error')
    
    return redirect(url_for('backup'))

@app.route('/backup/restaurar', methods=['POST'])
@login_required
def restaurar_backup():
    """Restaurar backup de la base de datos"""
    try:
        if 'backup_file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('backup'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('backup'))
        
        if file and file.filename.endswith('.db'):
            # Crear backup del archivo actual antes de restaurar
            import shutil
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_actual = f'yoga_school_backup_before_restore_{timestamp}.db'
            
            if os.path.exists('yoga_school.db'):
                shutil.copy2('yoga_school.db', os.path.join('backups', backup_actual))
            
            # Restaurar el archivo subido
            file.save('yoga_school.db')
            flash('Backup restaurado exitosamente. Se creó un backup del estado anterior.', 'success')
        else:
            flash('Formato de archivo no válido. Solo se permiten archivos .db', 'error')
            
    except Exception as e:
        flash(f'Error al restaurar backup: {str(e)}', 'error')
    
    return redirect(url_for('backup'))

@app.route('/exportar')
@login_required
def exportar():
    """Página principal de exportación"""
    return render_template('exportar.html')

# Función para inicializar las clases básicas
# FUNCIONES AUXILIARES
def verificar_conflicto_horario(fecha, hora_inicio, hora_fin, sesion_id=None):
    """Verificar si hay conflicto de horarios en una fecha específica"""
    if not hora_inicio or not hora_fin:
        return False, None
    
    # Obtener el día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fecha.weekday()
    
    # 1. Verificar conflictos con sesiones de yogaterapia existentes
    sesiones_existentes = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion == fecha,
        SesionYogaterapia.hora_inicio.isnot(None),
        SesionYogaterapia.hora_fin.isnot(None)
    ).all()
    
    # Si estamos editando, excluir la sesión actual
    if sesion_id:
        sesiones_existentes = [s for s in sesiones_existentes if s.id != sesion_id]
    
    for sesion in sesiones_existentes:
        # Verificar si los horarios se solapan
        if (hora_inicio < sesion.hora_fin and hora_fin > sesion.hora_inicio):
            return True, {
                'tipo': 'yogaterapia',
                'sesion': sesion,
                'mensaje': f'Ya existe una cita de yogaterapia de {sesion.hora_inicio.strftime("%H:%M")} a {sesion.hora_fin.strftime("%H:%M")} con {sesion.alumno.nombre} {sesion.alumno.apellido}'
            }
    
    # 2. Verificar conflictos con clases grupales del horario semanal
    horarios_semanal = HorarioSemanal.query.filter(
        HorarioSemanal.dia_semana == dia_semana,
        HorarioSemanal.activo == True
    ).all()
    
    for horario in horarios_semanal:
        # Verificar si los horarios se solapan
        if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
            return True, {
                'tipo': 'clase_grupal',
                'horario': horario,
                'mensaje': f'Conflicto con clase grupal: {horario.clase.nombre} de {horario.hora_inicio.strftime("%H:%M")} a {horario.hora_fin.strftime("%H:%M")} ({horario.get_dia_display()})'
            }
    
    return False, None

def obtener_proximas_citas(limite=5):
    """Obtener las próximas citas individuales para el dashboard"""
    hoy = datetime.now().date()
    proximas = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion >= hoy
    ).order_by(
        SesionYogaterapia.fecha_sesion.asc(),
        SesionYogaterapia.hora_inicio.asc()
    ).limit(limite).all()
    
    return proximas

def inicializar_clases():
    clases_basicas = [
        {'nombre': 'Yoga menopausia', 'descripcion': 'Clase especializada para mujeres en etapa de menopausia', 'precio': 15.00, 'duracion_minutos': 60},
        {'nombre': 'Yoga integral', 'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación', 'precio': 15.00, 'duracion_minutos': 60},
        {'nombre': 'Yoga embarazadas', 'descripcion': 'Yoga adaptado para mujeres embarazadas', 'precio': 15.00, 'duracion_minutos': 60},
        {'nombre': 'Meditación', 'descripcion': 'Práctica de meditación y mindfulness', 'precio': 12.00, 'duracion_minutos': 45},
        {'nombre': 'Yogaterapia', 'descripcion': 'Sesión individual de yogaterapia personalizada', 'precio': 45.00, 'duracion_minutos': 60}
    ]
    
    for clase_data in clases_basicas:
        clase_existente = Clase.query.filter_by(nombre=clase_data['nombre']).first()
        if not clase_existente:
            clase = Clase(
                nombre=clase_data['nombre'],
                descripcion=clase_data['descripcion'],
                precio=clase_data['precio'],
                duracion_minutos=clase_data['duracion_minutos']
            )
            db.session.add(clase)
    
    try:
        db.session.commit()
        print("✅ Clases básicas inicializadas")
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar clases: {e}")

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

# RUTAS API

@app.route('/api/stats')
@login_required
def api_stats():
    """API para obtener estadísticas del sistema"""
    try:
        alumnos_activos = Alumno.query.filter_by(activo=True).count()
        total_pagos = db.session.query(db.func.sum(Pago.monto)).scalar() or 0
        
        return jsonify({
            'success': True,
            'alumnos_activos': alumnos_activos,
            'total_pagos': round(total_pagos, 2),
            'ultimo_backup': 'Nunca'  # TODO: implementar tracking de backups
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clases')
@login_required
def api_clases():
    """API para obtener todas las clases"""
    try:
        clases = Clase.query.all()
        clases_data = []
        
        for clase in clases:
            horarios_count = HorarioSemanal.query.filter_by(clase_id=clase.id, activo=True).count()
            clases_data.append({
                'id': clase.id,
                'nombre': clase.nombre,
                'descripcion': clase.descripcion,
                'precio': clase.precio,
                'color': clase.color,
                'nivel': clase.nivel,
                'duracion_minutos': clase.duracion_minutos,
                'capacidad_maxima': clase.capacidad_maxima,
                'activa': clase.activa,
                'horarios_count': horarios_count
            })
        
        return jsonify({
            'success': True,
            'clases': clases_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clases/<int:clase_id>/toggle', methods=['POST'])
@login_required
def api_toggle_clase(clase_id):
    """API para activar/desactivar una clase"""
    try:
        clase = Clase.query.get_or_404(clase_id)
        clase.activa = not clase.activa
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activa': clase.activa
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500





@app.route('/usuarios')
@login_required
def usuarios():
    """Lista de usuarios del sistema"""
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_usuario():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            # Verificar que el username y email no existan
            if Usuario.query.filter_by(username=request.form['username']).first():
                flash('El nombre de usuario ya existe', 'error')
                return render_template('nuevo_usuario.html')
            
            if Usuario.query.filter_by(email=request.form['email']).first():
                flash('El email ya está registrado', 'error')
                return render_template('nuevo_usuario.html')
            
            # Crear hash de la contraseña (simple para demo)
            import hashlib
            password_hash = hashlib.sha256(request.form['password'].encode()).hexdigest()
            
            usuario = Usuario(
                username=request.form['username'],
                email=request.form['email'],
                password_hash=password_hash,
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                rol=request.form['rol']
            )
            
            db.session.add(usuario)
            db.session.commit()
            flash('¡Usuario creado exitosamente!', 'success')
            return redirect(url_for('usuarios'))
            
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('nuevo_usuario.html')

@app.route('/usuarios/<int:usuario_id>')
@login_required
def ver_usuario(usuario_id):
    """Ver detalles de un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('ver_usuario.html', usuario=usuario)

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    """Editar usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        try:
            # Verificar que el username y email no existan (excepto para el usuario actual)
            username_existente = Usuario.query.filter(
                Usuario.username == request.form['username'],
                Usuario.id != usuario_id
            ).first()
            
            if username_existente:
                flash('El nombre de usuario ya existe', 'error')
                return render_template('editar_usuario.html', usuario=usuario)
            
            email_existente = Usuario.query.filter(
                Usuario.email == request.form['email'],
                Usuario.id != usuario_id
            ).first()
            
            if email_existente:
                flash('El email ya está registrado', 'error')
                return render_template('editar_usuario.html', usuario=usuario)
            
            # Actualizar datos
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            usuario.nombre = request.form['nombre']
            usuario.apellido = request.form['apellido']
            usuario.rol = request.form['rol']
            usuario.activo = 'activo' in request.form
            
            # Actualizar contraseña si se proporciona
            if request.form['password']:
                import hashlib
                usuario.password_hash = hashlib.sha256(request.form['password'].encode()).hexdigest()
            
            db.session.commit()
            flash('¡Usuario actualizado exitosamente!', 'success')
            return redirect(url_for('ver_usuario', usuario_id=usuario_id))
            
        except Exception as e:
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    """Eliminar usuario (desactivar)"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    try:
        usuario.activo = False
        db.session.commit()
        flash('Usuario desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar usuario: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/<int:usuario_id>/reactivar', methods=['POST'])
@login_required
def reactivar_usuario(usuario_id):
    """Reactivar usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    try:
        usuario.activo = True
        db.session.commit()
        flash('Usuario reactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al reactivar usuario: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('usuarios'))

# Ruta para servir archivos estáticos de uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Servir archivos subidos desde la carpeta uploads"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Ruta para calendario de selección de citas
@app.route('/calendario_seleccion_citas')
@app.route('/calendario_seleccion_citas/<int:alumno_id>')
@login_required
def calendario_seleccion_citas(alumno_id=None):
    """Mostrar calendario interactivo para seleccionar fecha y hora de cita"""
    alumno = None
    if alumno_id:
        alumno = Alumno.query.get_or_404(alumno_id)
    
    # Calcular fechas para el calendario
    hoy = date.today()
    mes_actual = hoy.strftime('%B')
    año_actual = hoy.year
    
    # Calcular inicio de semana (lunes)
    lunes = hoy - timedelta(days=(hoy.weekday()))
    fecha_inicio_semana = lunes
    
    return render_template('calendario_seleccion_citas.html', 
                         alumno=alumno,
                         mes_actual=mes_actual,
                         año_actual=año_actual,
                         fecha_inicio_semana=fecha_inicio_semana)

# FUNCIONES DE EXPORTACIÓN

def exportar_facturas_excel(facturas):
    """Exportar facturas a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import make_response
        
        data = []
        for factura in facturas:
            data.append({
                'Número Factura': factura.numero_factura,
                'Proveedor': factura.proveedor.nombre,
                'Categoría': factura.categoria.nombre,
                'Fecha Factura': factura.fecha_factura.strftime('%d/%m/%Y'),
                'Fecha Vencimiento': factura.fecha_vencimiento.strftime('%d/%m/%Y') if factura.fecha_vencimiento else '',
                'Importe sin IVA': factura.importe_sin_iva,
                'IVA %': factura.iva,
                'Importe Total': factura.importe_total,
                'Estado': factura.estado.title(),
                'Fecha Pago': factura.fecha_pago.strftime('%d/%m/%Y') if factura.fecha_pago else '',
                'Método Pago': factura.metodo_pago or '',
                'Descripción': factura.descripcion or '',
                'Notas': factura.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Facturas', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=facturas_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('facturas'))
    except Exception as e:
        flash(f'Error al exportar facturas: {str(e)}', 'error')
        return redirect(url_for('facturas'))

def exportar_gastos_fijos_excel(gastos):
    """Exportar gastos fijos a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import make_response
        
        data = []
        for gasto in gastos:
            data.append({
                'Nombre': gasto.nombre,
                'Descripción': gasto.descripcion or '',
                'Categoría': gasto.categoria.nombre,
                'Importe': gasto.importe,
                'Frecuencia': gasto.frecuencia.title(),
                'Día de Cargo': gasto.dia_cargo,
                'Fecha Inicio': gasto.fecha_inicio.strftime('%d/%m/%Y'),
                'Fecha Fin': gasto.fecha_fin.strftime('%d/%m/%Y') if gasto.fecha_fin else '',
                'Activo': 'Sí' if gasto.activo else 'No',
                'Notas': gasto.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Gastos Fijos', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=gastos_fijos_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('gastos_fijos'))
    except Exception as e:
        flash(f'Error al exportar gastos fijos: {str(e)}', 'error')
        return redirect(url_for('gastos_fijos'))

def exportar_proveedores_excel(proveedores):
    """Exportar proveedores a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import make_response
        
        data = []
        for proveedor in proveedores:
            data.append({
                'Nombre': proveedor.nombre,
                'CIF/NIF': proveedor.cif_nif or '',
                'Dirección': proveedor.direccion or '',
                'Teléfono': proveedor.telefono or '',
                'Email': proveedor.email or '',
                'Contacto Principal': proveedor.contacto_principal or '',
                'Activo': 'Sí' if proveedor.activo else 'No',
                'Fecha Registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
                'Notas': proveedor.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Proveedores', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=proveedores_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('proveedores'))
    except Exception as e:
        flash(f'Error al exportar proveedores: {str(e)}', 'error')
        return redirect(url_for('proveedores'))

def exportar_ingresos_excel():
    """Exportar ingresos a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import make_response
        
        # Obtener ingresos de los últimos 12 meses
        fecha_inicio = date.today() - timedelta(days=365)
        fecha_fin = date.today()
        
        pagos = Pago.query.filter(
            Pago.fecha_creacion >= fecha_inicio,
            Pago.fecha_creacion <= fecha_fin
        ).order_by(Pago.fecha_creacion.desc()).all()
        
        data = []
        for pago in pagos:
            data.append({
                'Fecha': pago.fecha_creacion.strftime('%d/%m/%Y'),
                'Alumno': f"{pago.alumno.nombre} {pago.alumno.apellido}",
                'Tipo Pago': pago.tipo_pago.title(),
                'Mes/Año': pago.mes or f"{pago.año}" if pago.año else '',
                'Fecha Clase': pago.fecha_clase.strftime('%d/%m/%Y') if pago.fecha_clase else '',
                'Monto': pago.monto,
                'Método Pago': pago.metodo_pago or '',
                'Descripción': pago.descripcion or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ingresos', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=ingresos_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('economia'))
    except Exception as e:
        flash(f'Error al exportar ingresos: {str(e)}', 'error')
        return redirect(url_for('economia'))

def generar_reporte_pdf(facturas, gastos_fijos, ingresos, fecha_inicio, fecha_fin):
    """Generar reporte de contabilidad en PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from io import BytesIO
        from flask import make_response
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        # Título
        story.append(Paragraph("REPORTE DE CONTABILIDAD", title_style))
        story.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resumen financiero
        total_facturas = sum(f.importe_total for f in facturas)
        total_gastos_fijos = sum(g.importe for g in gastos_fijos)
        balance = ingresos - total_facturas - total_gastos_fijos
        
        resumen_data = [
            ['Concepto', 'Importe (€)'],
            ['Ingresos Totales', f"{ingresos:.2f}"],
            ['Gastos en Facturas', f"{total_facturas:.2f}"],
            ['Gastos Fijos', f"{total_gastos_fijos:.2f}"],
            ['BALANCE', f"{balance:.2f}"]
        ]
        
        resumen_table = Table(resumen_data)
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(Paragraph("RESUMEN FINANCIERO", styles['Heading2']))
        story.append(resumen_table)
        story.append(Spacer(1, 20))
        
        # Facturas
        if facturas:
            story.append(Paragraph("FACTURAS DEL PERÍODO", styles['Heading2']))
            facturas_data = [['Número', 'Proveedor', 'Fecha', 'Importe', 'Estado']]
            for factura in facturas:
                facturas_data.append([
                    factura.numero_factura,
                    factura.proveedor.nombre,
                    factura.fecha_factura.strftime('%d/%m/%Y'),
                    f"{factura.importe_total:.2f}",
                    factura.estado.title()
                ])
            
            facturas_table = Table(facturas_data)
            facturas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(facturas_table)
            story.append(Spacer(1, 20))
        
        # Gastos fijos
        if gastos_fijos:
            story.append(Paragraph("GASTOS FIJOS", styles['Heading2']))
            gastos_data = [['Nombre', 'Categoría', 'Importe', 'Frecuencia']]
            for gasto in gastos_fijos:
                gastos_data.append([
                    gasto.nombre,
                    gasto.categoria.nombre,
                    f"{gasto.importe:.2f}",
                    gasto.frecuencia.title()
                ])
            
            gastos_table = Table(gastos_data)
            gastos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(gastos_table)
        
        doc.build(story)
        
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_contabilidad_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.pdf'
        
        return response
        
    except ImportError:
        flash('Error: reportlab no está instalado. Instale con: pip install reportlab', 'error')
        return redirect(url_for('economia'))
    except Exception as e:
        flash(f'Error al generar reporte PDF: {str(e)}', 'error')
        return redirect(url_for('economia'))

# ===================== NUEVAS RUTAS API PARA CALENDARIO COMPLETO =====================

@app.route('/calendario-completo')
@login_required
def calendario_completo():
    """Vista del calendario completo con grid horario 8:00-21:00"""
    try:
        # Obtener todas las clases activas
        clases = Clase.query.filter_by(activa=True).order_by(Clase.nombre).all()
        
        # Obtener todos los alumnos para yogaterapia
        alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
        
        return render_template('calendario_horarios_completo.html', 
                             clases=clases,
                             alumnos=alumnos)
    except Exception as e:
        flash(f'Error cargando calendario: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/eventos-semana')
@login_required
def api_eventos_semana():
    """API para obtener eventos de una semana específica"""
    try:
        fecha_inicio = request.args.get('inicio')
        fecha_fin = request.args.get('fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'success': False, 'message': 'Fechas requeridas'}), 400
        
        # Convertir strings a fechas
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Obtener eventos del calendario
        # eventos_calendario = EventoCalendario.query.filter(
        #     EventoCalendario.fecha >= inicio,
        #     EventoCalendario.fecha <= fin,
        #     EventoCalendario.activo == True,
        #     EventoCalendario.cancelado == False
        # ).all()
        eventos_calendario = []  # Temporary fix - EventoCalendario model not defined
        
        # Obtener horarios semanales que no tienen eventos específicos
        horarios_semanales = HorarioSemanal.query.filter_by(activo=True).all()
        
        eventos_data = []
        
        # Procesar eventos específicos del calendario
        for evento in eventos_calendario:
            # Contar asistencias
            # asistencias_count = AsistenciaEvento.query.filter_by(
            #     evento_id=evento.id,
            #     confirmado=True
            # ).count()
            asistencias_count = 0  # Temporary fix - AsistenciaEvento model not defined
            
            # Determinar clase CSS basada en el tipo
            css_class = 'evento-calendario'
            if evento.clase:
                css_class += f' {evento.clase.nombre.lower().replace(" ", "-")}'
            elif evento.tipo_evento == 'yogaterapia':
                css_class += ' yogaterapia'
            
            eventos_data.append({
                'id': evento.id,
                'titulo': evento.titulo,
                'fecha': evento.fecha.strftime('%Y-%m-%d'),
                'hora_inicio': evento.hora_inicio.strftime('%H:%M'),
                'hora_fin': evento.hora_fin.strftime('%H:%M'),
                'tipo_evento': evento.tipo_evento,
                'instructor': evento.instructor,
                'capacidad_maxima': evento.capacidad_maxima,
                'precio': float(evento.precio) if evento.precio else 0,
                'descripcion': evento.descripcion,
                'css_class': css_class,
                'color': evento.color,
                'asistencias': asistencias_count,
                'clase_id': evento.clase_id,
                'alumno_id': evento.alumno_id
            })
        
        # Generar eventos virtuales para horarios semanales
        fecha_actual = inicio
        while fecha_actual <= fin:
            dia_semana = fecha_actual.weekday() + 1  # Lunes = 1
            
            # Buscar horarios para este día
            horarios_dia = [h for h in horarios_semanales if str(dia_semana) in (h.dias_semana or '').split(',')]
            
            for horario in horarios_dia:
                # Verificar si ya existe un evento específico para esta fecha/hora
                evento_existente = any(
                    e['fecha'] == fecha_actual.strftime('%Y-%m-%d') and
                    e['hora_inicio'] == horario.hora_inicio.strftime('%H:%M')
                    for e in eventos_data
                )
                
                if not evento_existente:
                    # Crear evento virtual
                    css_class = f'evento-calendario {horario.clase.nombre.lower().replace(" ", "-")}'
                    
                    eventos_data.append({
                        'id': f'virtual-{horario.id}-{fecha_actual.strftime("%Y%m%d")}',
                        'titulo': f'{horario.clase.nombre} (Horario Regular)',
                        'fecha': fecha_actual.strftime('%Y-%m-%d'),
                        'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                        'hora_fin': horario.hora_fin.strftime('%H:%M'),
                        'tipo_evento': 'clase_grupal',
                        'instructor': horario.instructor,
                        'capacidad_maxima': horario.capacidad_maxima,
                        'precio': float(horario.clase.precio) if horario.clase.precio else 0,
                        'descripcion': f'Clase regular de {horario.clase.nombre}',
                        'css_class': css_class,
                        'color': horario.clase.color if hasattr(horario.clase, 'color') else '#007bff',
                        'asistencias': 0,
                        'clase_id': horario.clase_id,
                        'horario_id': horario.id,
                        'es_virtual': True
                    })
            
            fecha_actual += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'eventos': eventos_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/evento/crear', methods=['POST'])
@login_required
def api_crear_evento():
    """API para crear un nuevo evento - STUB"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not all(k in data for k in ['fecha', 'hora_inicio', 'hora_fin']):
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # Convertir datos
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        
        # Verificar conflictos
        # conflictos = EventoCalendario.query.filter(
        #     EventoCalendario.fecha == fecha,
        #     EventoCalendario.activo == True,
        #     EventoCalendario.cancelado == False,
        #     EventoCalendario.hora_inicio < hora_fin,
        #     EventoCalendario.hora_fin > hora_inicio
        # ).first()
        conflictos = None  # Temporary fix - EventoCalendario model not defined
        
        if conflictos:
            return jsonify({
                'success': False, 
                'message': f'Conflicto de horario con: {conflictos.titulo}'
            }), 400
        
        # Determinar tipo de evento
        if data.get('tipo_clase') == 'yogaterapia':
            tipo_evento = 'yogaterapia'
            titulo = f"Yogaterapia - {data.get('alumno_nombre', 'Sesión Individual')}"
            clase_id = None
            alumno_id = data.get('alumno_id')
        else:
            tipo_evento = 'clase_grupal'
            clase = Clase.query.get(data['tipo_clase'])
            if not clase:
                return jsonify({'success': False, 'message': 'Clase no encontrada'}), 404
            titulo = clase.nombre
            clase_id = clase.id
            alumno_id = None
        
        # Crear evento
        evento = EventoCalendario(
            titulo=titulo,
            descripcion=data.get('descripcion', ''),
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_evento=tipo_evento,
            clase_id=clase_id,
            alumno_id=alumno_id,
            instructor=data.get('instructor', 'Minouche'),
            capacidad_maxima=data.get('capacidad_maxima', 15),
            precio=data.get('precio', 0),
            color=data.get('color', '#007bff'),
            es_recurrente=data.get('es_recurrente', False),
            patron_recurrencia='semanal' if data.get('es_recurrente') else None,
            fecha_fin_recurrencia=datetime.strptime(data['fecha_fin_recurrencia'], '%Y-%m-%d').date() if data.get('fecha_fin_recurrencia') else None
        )
        
        db.session.add(evento)
        db.session.flush()  # Para obtener el ID
        
        # Si es recurrente, crear eventos adicionales
        if data.get('es_recurrente') and data.get('fecha_fin_recurrencia'):
            fecha_fin_recurrencia = datetime.strptime(data['fecha_fin_recurrencia'], '%Y-%m-%d').date()
            fecha_actual = fecha + timedelta(days=7)
            
            while fecha_actual <= fecha_fin_recurrencia:
                evento_recurrente = EventoCalendario(
                    titulo=titulo,
                    descripcion=data.get('descripcion', ''),
                    fecha=fecha_actual,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    tipo_evento=tipo_evento,
                    clase_id=clase_id,
                    alumno_id=alumno_id,
                    instructor=data.get('instructor', 'Minouche'),
                    capacidad_maxima=data.get('capacidad_maxima', 15),
                    precio=data.get('precio', 0),
                    color=data.get('color', '#007bff'),
                    es_recurrente=True,
                    patron_recurrencia='semanal',
                    horario_semanal_id=evento.id  # Referencia al evento padre
                )
                
                db.session.add(evento_recurrente)
                fecha_actual += timedelta(days=7)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'evento_id': evento.id,
            'message': 'Evento creado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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

@app.route('/api/evento/<int:evento_id>/eliminar', methods=['DELETE'])
@login_required
def api_eliminar_evento(evento_id):
    """API para eliminar un evento"""
    try:
        evento = EventoCalendario.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'message': 'Evento no encontrado'}), 404
        
        # Eliminar asistencias asociadas
        AsistenciaEvento.query.filter_by(evento_id=evento_id).delete()
        
        # Eliminar evento
        db.session.delete(evento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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

@app.route('/api/eventos-disponibles')
@login_required
def api_eventos_disponibles():
    """API para obtener eventos disponibles para un alumno"""
    try:
        alumno_id = request.args.get('alumno_id', type=int)
        fecha_inicio = request.args.get('inicio')
        fecha_fin = request.args.get('fin')
        
        if not all([alumno_id, fecha_inicio, fecha_fin]):
            return jsonify({'success': False, 'message': 'Parámetros incompletos'}), 400
        
        # Convertir fechas
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            # Soportar formato ISO si viene así
            inicio = datetime.fromisoformat(fecha_inicio).date()
            fin = datetime.fromisoformat(fecha_fin).date()

        # Obtener eventos futuros con capacidad disponible
        eventos_query = EventoCalendario.query.filter(
            EventoCalendario.fecha_inicio >= datetime.combine(inicio, datetime.min.time()),
            EventoCalendario.fecha_fin <= datetime.combine(fin, datetime.max.time()),
            EventoCalendario.activo == True,
            EventoCalendario.tipo != 'yogaterapia'  # Excluir yogaterapia
        ).order_by(EventoCalendario.fecha_inicio).all()
        
        eventos_disponibles = []
        
        for evento in eventos_query:
            # Verificar si el alumno ya está inscrito
            # Verificar si el alumno ya está inscrito
            ya_inscrito = Asistencia.query.filter_by(
                evento_id=evento.id,
                alumno_id=alumno_id
            ).first()
            
            if ya_inscrito:
                continue

            # Contar asistencias actuales
            asistencias_count = Asistencia.query.filter_by(
                evento_id=evento.id
            ).count()
            
            # Verificar capacidad disponible
            # Usar un valor por defecto si no tiene atributo capacidad_maxima (o 15)
            capacidad_maxima = getattr(evento, 'capacidad_maxima', 15)
            if asistencias_count >= capacidad_maxima:
                continue  # Skip si está lleno
            
            eventos_disponibles.append({
                'id': evento.id,
                'titulo': evento.titulo,
                'fecha': evento.fecha_inicio.strftime('%Y-%m-%d'),
                'hora_inicio': evento.fecha_inicio.strftime('%H:%M'),
                'hora_fin': evento.fecha_fin.strftime('%H:%M'),
                'instructor': evento.instructor,
                'capacidad_maxima': capacidad_maxima,
                'asistencias': asistencias_count,
                'precio': getattr(evento, 'precio', 0),
                'color': evento.color,
                'descripcion': evento.descripcion
            })
        
        # También incluir eventos virtuales de horarios semanales
        horarios_semanales = HorarioSemanal.query.filter_by(activo=True).all()
        
        fecha_actual = inicio
        while fecha_actual <= fin:
            dia_semana = fecha_actual.weekday()  # Monday is 0
            
            for horario in horarios_semanales:
                # HorarioSemanal dia_semana: 0=Lunes...
                if horario.dia_semana == dia_semana:
                    # Verificar si ya existe un evento específico para esta fecha/hora
                    evento_existente = any(
                        e['fecha'] == fecha_actual.strftime('%Y-%m-%d') and
                        e['hora_inicio'] == horario.hora_inicio.strftime('%H:%M')
                        for e in eventos_disponibles
                    )
                    
                    if not evento_existente:
                        # Crear evento virtual
                        eventos_disponibles.append({
                            'id': f'virtual-{horario.id}-{fecha_actual.strftime("%Y%m%d")}',
                            'titulo': f'{horario.clase.nombre}',
                            'fecha': fecha_actual.strftime('%Y-%m-%d'),
                            'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                            'hora_fin': horario.hora_fin.strftime('%H:%M'),
                            'instructor': horario.instructor,
                            'capacidad_maxima': 15, # Default
                            'asistencias': 0,
                            'precio': 0, # Default
                            'color': getattr(horario.clase, 'color', '#007bff'),
                            'descripcion': f'Clase regular de {horario.clase.nombre}',
                            'es_virtual': True,
                            'horario_id': horario.id
                        })
            
            fecha_actual += timedelta(days=1)
        
        # Ordenar por fecha y hora
        eventos_disponibles.sort(key=lambda x: (x['fecha'], x['hora_inicio']))
        
        return jsonify({
            'success': True,
            'eventos': eventos_disponibles
        })
        
    except Exception as e:
        print(f"Error en api_eventos_disponibles: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/economia/facturas/nueva', methods=['GET', 'POST'])
def nueva_factura_proveedor():
    """Registrar nueva factura de proveedor"""
    if request.method == 'POST':
        try:
            importe_sin_iva = float(request.form.get('importe_sin_iva', 0))
            iva = float(request.form.get('iva', 0))
            importe_total = float(request.form.get('importe_total', 0))

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
                getattr(ingreso, 'monto', getattr(ingreso, 'importe', 0)),
                ingreso.fecha_creacion.strftime('%Y-%m-%d') if getattr(ingreso, 'fecha_creacion', None) else '',
                getattr(ingreso, 'tipo_pago', 'Pago'),
                getattr(ingreso, 'metodo_pago', ''),
                alumno_nombre,
                getattr(ingreso, 'descripcion', '')
            ])
            
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=export_{tipo}_{date.today()}.csv"
    response.headers["Content-type"] = "text/csv"
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

# NUEVAS RUTAS DE API PARA HORARIOS (SOPORTE PARA CALENDARIO UNIFICADO)

@app.route('/api/horario/<int:horario_id>')
@login_required
def get_horario_api_detalles(horario_id):
    """Obtiene los detalles de un horario específico"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        return jsonify({
            'success': True,
            'horario': horario.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/horario/crear', methods=['POST'])
@login_required
def api_crear_horario():
    """Crea uno o varios horarios semanales"""
    try:
        data = request.get_json()
        clase_id = data.get('clase_id')
        hora_inicio_str = data.get('hora_inicio')
        hora_fin_str = data.get('hora_fin')
        dias_semana_str = data.get('dias_semana') # Ej: "1,3,5"
        
        if not all([clase_id, hora_inicio_str, hora_fin_str, dias_semana_str]):
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400
            
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
        # El front envía 1-7 (Lunes-Domingo), convertimos a 0-6
        dias_semana = [int(d.strip()) - 1 for d in str(dias_semana_str).split(',')]
        
        nuevos_ids = []
        for dia in dias_semana:
            horario = HorarioSemanal(
                clase_id=clase_id,
                dia_semana=dia,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                instructor=data.get('instructor', 'Minouche'),
                capacidad_maxima=data.get('capacidad_maxima', 15),
                observaciones=data.get('observaciones', '')
            )
            db.session.add(horario)
            db.session.flush()
            nuevos_ids.append(horario.id)
            
        db.session.commit()
        return jsonify({'success': True, 'ids': nuevos_ids})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/horario/actualizar', methods=['POST'])
@login_required
def api_actualizar_horario():
    """Actualiza un horario semanal existente"""
    try:
        data = request.get_json()
        horario_id = data.get('horario_id')
        horario = HorarioSemanal.query.get_or_404(horario_id)
        
        clase_id = data.get('clase_id')
        hora_inicio_str = data.get('hora_inicio')
        hora_fin_str = data.get('hora_fin')
        dia_semana_str = data.get('dias_semana')
        
        if not all([clase_id, hora_inicio_str, hora_fin_str, dia_semana_str]):
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400
            
        horario.clase_id = clase_id
        horario.hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        horario.hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
        horario.dia_semana = int(str(dia_semana_str).split(',')[0]) - 1
        horario.instructor = data.get('instructor', 'Minouche')
        horario.capacidad_maxima = data.get('capacidad_maxima', 15)
        horario.observaciones = data.get('observaciones', '')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/horario/<int:horario_id>/eliminar', methods=['DELETE'])
@login_required
def api_eliminar_horario(horario_id):
    """Elimina un horario semanal"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        db.session.delete(horario)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/alumnos-disponibles')
@login_required
def api_alumnos_disponibles():
    """Obtiene lista de alumnos activos"""
    try:
        alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
        return jsonify({
            'success': True,
            'alumnos': [{
                'id': a.id,
                'nombre': a.nombre,
                'apellido': a.apellido,
                'tipo_clase': a.get_tipo_cuota_display()
            } for a in alumnos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/horario/<int:horario_id>/alumnos')
@login_required
def get_alumnos_horario(horario_id):
    """Obtiene alumnos inscritos en un horario"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        alumnos = [{
            'id': a.id,
            'nombre': a.nombre,
            'apellido': a.apellido,
            'tipo_clase': a.get_tipo_cuota_display()
        } for a in horario.alumnos_inscritos]
        
        return jsonify({
            'success': True,
            'alumnos': alumnos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/horario/agregar-alumno', methods=['POST'])
@login_required
def agregar_alumno_horario():
    """Inscribe un alumno en un horario semanal"""
    try:
        data = request.get_json()
        alumno = Alumno.query.get_or_404(data['alumno_id'])
        horario = HorarioSemanal.query.get_or_404(data['horario_id'])
        
        if alumno not in horario.alumnos_inscritos:
            horario.alumnos_inscritos.append(alumno)
            db.session.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/horario/quitar-alumno', methods=['POST'])
@login_required
def quitar_alumno_horario():
    """Desinscribe un alumno de un horario semanal"""
    try:
        data = request.get_json()
        alumno = Alumno.query.get_or_404(data['alumno_id'])
        horario = HorarioSemanal.query.get_or_404(data['horario_id'])
        
        if alumno in horario.alumnos_inscritos:
            horario.alumnos_inscritos.remove(alumno)
            db.session.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/horario/<int:horario_id>/limpiar-alumnos', methods=['POST'])
@login_required
def limpiar_alumnos_horario(horario_id):
    """Quita todos los alumnos de un horario semanal"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        horario.alumnos_inscritos = []
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/alumno/<int:alumno_id>/asistencias')
@login_required
def get_asistencias_alumno_api(alumno_id):
    """API para obtener todas las asistencias de un alumno"""
    try:
        alumno = Alumno.query.get_or_404(alumno_id)
        # Obtener todas las asistencias
        asistencias = Asistencia.query.filter_by(alumno_id=alumno_id).order_by(Asistencia.fecha_clase.desc()).all()
        
        asistencias_data = []
        presentes = 0
        ausentes = 0
        pendientes = 0
        
        for a in asistencias:
            # Determinar info del evento/clase
            if a.evento:
                evento_info = {
                    'titulo': a.evento.titulo,
                    'color': a.evento.color,
                    'hora_inicio': a.evento.fecha_inicio.strftime('%H:%M'),
                    'hora_fin': a.evento.fecha_fin.strftime('%H:%M'),
                    'instructor': a.evento.instructor
                }
            elif a.horario:
                evento_info = {
                    'titulo': a.horario.clase.nombre,
                    'color': a.horario.clase.color,
                    'hora_inicio': a.horario.hora_inicio.strftime('%H:%M'),
                    'hora_fin': a.horario.hora_fin.strftime('%H:%M'),
                    'instructor': a.horario.instructor
                }
            else:
                evento_info = {
                    'titulo': 'Clase sin asignar',
                    'color': '#6c757d',
                    'hora_inicio': '--:--',
                    'hora_fin': '--:--',
                    'instructor': 'N/A'
                }
            
            asistencias_data.append({
                'id': a.id,
                'fecha': a.fecha_clase.isoformat(),
                'asistio': a.presente,
                'evento': evento_info,
                'observaciones': a.observaciones
            })
            
            if a.presente is True:
                presentes += 1
            elif a.presente is False:
                ausentes += 1
            else:
                pendientes += 1
                
        total = presentes + ausentes
        porcentaje = round((presentes / total * 100), 1) if total > 0 else 0
        
        return jsonify({
            'success': True,
            'asistencias': asistencias_data,
            'estadisticas': {
                'presentes': presentes,
                'ausentes': ausentes,
                'pendientes': pendientes,
                'porcentaje_asistencia': porcentaje
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/evento/agregar-alumno', methods=['POST'])
@login_required
def api_agregar_alumno_evento():
    """Inscribe un alumno en un evento o clase semanal virtual"""
    try:
        data = request.get_json()
        alumno_id = data.get('alumno_id')
        evento_id = data.get('evento_id')
        
        if not alumno_id or not evento_id:
            return jsonify({'success': False, 'message': 'IDs de alumno y evento requeridos'}), 400
            
        alumno = Alumno.query.get_or_404(alumno_id)
        
        # El evento_id puede ser un entero (EventoCalendario) o un string "virtual-ID-FECHA" (HorarioSemanal)
        if isinstance(evento_id, str) and evento_id.startswith('virtual-'):
            parts = evento_id.split('-')
            horario_id = int(parts[1])
            fecha_str = parts[2]
            fecha_obj = datetime.strptime(fecha_str, '%Y%m%d').date()
            
            # Verificar si ya existe
            existente = Asistencia.query.filter_by(
                alumno_id=alumno_id,
                horario_id=horario_id,
                fecha_clase=fecha_obj
            ).first()
            
            if existente:
                return jsonify({'success': False, 'message': 'El alumno ya está inscrito en esta clase'}), 400
                
            nueva_asistencia = Asistencia(
                alumno_id=alumno_id,
                horario_id=horario_id,
                fecha_clase=fecha_obj,
                presente=None
            )
            db.session.add(nueva_asistencia)
            db.session.commit()
            return jsonify({'success': True})
        else:
            # Asumimos que evento_id es de EventoCalendario
            evento = EventoCalendario.query.get_or_404(evento_id)
            
            # Verificar si ya existe la asistencia
            existente = Asistencia.query.filter_by(
                alumno_id=alumno_id,
                evento_id=evento.id,
                fecha_clase=evento.fecha_inicio.date()
            ).first()
            
            if existente:
                return jsonify({'success': False, 'message': 'El alumno ya está inscrito en esta clase'}), 400
                
            nueva_asistencia = Asistencia(
                alumno_id=alumno_id,
                evento_id=evento.id,
                fecha_clase=evento.fecha_inicio.date(),
                presente=None
            )
            db.session.add(nueva_asistencia)
            db.session.commit()
            
            return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/asistencias/clase/<int:horario_id>/<fecha>')
@login_required
def api_get_asistencias_clase_fecha(horario_id, fecha):
    """Obtiene alumnos y su estado de asistencia para una clase y fecha concreta"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        horario = HorarioSemanal.query.get_or_404(horario_id)
        
        # Alumnos inscritos en el horario recurrente (el "roster")
        alumnos_inscritos = horario.alumnos_inscritos
        
        # Asistencias ya registradas para ese día
        asistencias_db = Asistencia.query.filter_by(
            horario_id=horario_id,
            fecha_clase=fecha_obj
        ).all()
        
        asistencias_map = {a.alumno_id: a for a in asistencias_db}
        
        resultado = []
        # Primero procesamos los que están en el roster
        ids_procesados = set()
        for alumno in alumnos_inscritos:
            asistencia = asistencias_map.get(alumno.id)
            resultado.append({
                'id': alumno.id,
                'nombre': f"{alumno.nombre} {alumno.apellido}",
                'inscrito': True,
                'asistio': asistencia.presente if asistencia else None,
                'observaciones': asistencia.observaciones if asistencia else ""
            })
            ids_procesados.add(alumno.id)
            
        # Luego añadimos alumnos que asistieron pero no están en el roster (casos especiales)
        for alumno_id, asistencia in asistencias_map.items():
            if alumno_id not in ids_procesados:
                alumno = Alumno.query.get(alumno_id)
                if alumno:
                    resultado.append({
                        'id': alumno.id,
                        'nombre': f"{alumno.nombre} {alumno.apellido}",
                        'inscrito': False,
                        'asistio': asistencia.presente,
                        'observaciones': asistencia.observaciones
                    })
        
        return jsonify({
            'success': True,
            'alumnos': resultado,
            'clase': horario.clase.nombre,
            'fecha': fecha_obj.strftime('%d/%m/%Y')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/asistencias/registrar-lote', methods=['POST'])
@login_required
def api_registrar_asistencia_lote():
    """Registra la asistencia de múltiples alumnos para una clase y fecha"""
    try:
        data = request.get_json()
        horario_id = data.get('horario_id')
        fecha_str = data.get('fecha')
        registro = data.get('registro') # Lista de {alumno_id, asistio, observaciones}
        
        if not all([horario_id, fecha_str, registro]):
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
            
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        for item in registro:
            alumno_id = item['alumno_id']
            asistio = item['asistio']
            obs = item.get('observaciones', "")
            
            asistencia = Asistencia.query.filter_by(
                alumno_id=alumno_id,
                horario_id=horario_id,
                fecha_clase=fecha_obj
            ).first()
            
            if asistencia:
                asistencia.presente = asistio
                asistencia.observaciones = obs
            else:
                nueva = Asistencia(
                    alumno_id=alumno_id,
                    horario_id=horario_id,
                    fecha_clase=fecha_obj,
                    presente=asistio,
                    observaciones=obs
                )
                db.session.add(nueva)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        inicializar_categorias_gastos()
        
        # Crear usuario administrador por defecto si no existe
        admin_existente = Usuario.query.filter_by(username='admin').first()
        if not admin_existente:
            admin = Usuario(
                username='admin',
                email='admin@atmasuddhi.es',
                password_hash=generate_password_hash('AtmaSuddhi74'),
                nombre='Administrador',
                apellido='Sistema',
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado: admin / AtmaSuddhi74")
    
    
    app.run(debug=True, port=5000)