from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'atma-suddhi-yoga-management-2025-secure-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS

# Modelo de Alumno
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
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
    asistencias = db.relationship('Asistencia', backref='alumno', lazy=True)
    sesiones_yogaterapia = db.relationship('SesionYogaterapia', backref='alumno', lazy=True)
    clases_personales = db.relationship('ClasePersonal', backref='alumno', lazy=True)
    
    def __repr__(self):
        return f'<Alumno {self.nombre} {self.apellido}>'
    
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
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    horarios = db.relationship('HorarioSemanal', backref='clase', lazy=True)
    
    def __repr__(self):
        return f'<Clase {self.nombre}>'

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
    
    # Relaciones
    asistencias = db.relationship('Asistencia', backref='horario', lazy=True)
    
    def __repr__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f'<Horario {dias[self.dia_semana]} {self.hora_inicio} - {self.hora_fin}>'
    
    def get_dia_display(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[self.dia_semana]

# Modelo de Asistencia
class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario_semanal.id'), nullable=False)
    fecha_clase = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Asistencia {self.alumno.nombre} - {self.fecha_clase}>'

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

# Modelo de Gasto Fijo
class GastoFijo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_gasto.id'), nullable=False)
    importe = db.Column(db.Float, nullable=False)
    frecuencia = db.Column(db.String(20), default='mensual')  # mensual, trimestral, anual
    dia_cargo = db.Column(db.Integer, default=1)  # Día del mes para el cargo
    activo = db.Column(db.Boolean, default=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)  # Opcional, para gastos temporales
    notas = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GastoFijo {self.nombre} - {self.importe}€>'

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

# MODELOS DE YOGATERAPIA

# Modelo de Yogaterapia (Sesiones Individuales)
class SesionYogaterapia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    fecha_sesion = db.Column(db.Date, nullable=False)
    duracion_minutos = db.Column(db.Integer, default=75)
    tipo_sesion = db.Column(db.String(50), default='individual')  # individual, pareja
    
    # Información terapéutica
    motivo_consulta = db.Column(db.Text)  # Por qué viene el alumno
    objetivos_terapeuticos = db.Column(db.Text)  # Objetivos específicos
    tecnicas_aplicadas = db.Column(db.Text)  # Técnicas de yoga utilizadas
    posturas_trabajadas = db.Column(db.Text)  # Asanas específicas
    respiracion_pranayama = db.Column(db.Text)  # Ejercicios de respiración
    meditacion_relajacion = db.Column(db.Text)  # Técnicas de meditación
    
    # Evaluación y seguimiento
    estado_inicial = db.Column(db.Text)  # Cómo llegó el alumno
    respuesta_sesion = db.Column(db.Text)  # Cómo respondió durante la sesión
    estado_final = db.Column(db.Text)  # Cómo se fue el alumno
    observaciones_terapeuta = db.Column(db.Text)  # Observaciones profesionales
    recomendaciones_casa = db.Column(db.Text)  # Práctica para casa
    proxima_sesion = db.Column(db.Text)  # Plan para próxima sesión
    
    # Información administrativa
    instructor = db.Column(db.String(50), default='Minouche')
    precio = db.Column(db.Float, default=50.00)
    pagado = db.Column(db.Boolean, default=False)
    metodo_pago = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    archivos = db.relationship('ArchivoYogaterapia', backref='sesion_yogaterapia', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SesionYogaterapia {self.alumno.nombre} - {self.fecha_sesion}>'

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

# RUTAS PRINCIPALES

@app.route('/')
def index():
    # Estadísticas para el dashboard
    alumnos_activos = Alumno.query.filter_by(activo=True).count()
    total_ingresos = db.session.query(db.func.sum(Pago.monto)).scalar() or 0
    pagos_pendientes = 0  # Calcular según lógica de negocio
    
    return render_template('index.html', 
                         alumnos_activos=alumnos_activos,
                         ingresos_mes=total_ingresos,
                         pagos_pendientes=pagos_pendientes)

@app.route('/alumnos')
def alumnos():
    # Mostrar todos los alumnos
    todos_alumnos = Alumno.query.all()
    current_year = date.today().year
    
    # Fecha límite para considerar inactividad (2 meses)
    fecha_limite = date.today() - timedelta(days=60)
    
    for alumno in todos_alumnos:
        # Inicializar propiedades
        alumno.inactivo_temporal = False
        alumno.ultimo_pago = None
        
        # Obtener el último pago
        try:
            ultimo_pago = Pago.query.filter_by(alumno_id=alumno.id).order_by(Pago.fecha_creacion.desc()).first()
            if ultimo_pago:
                alumno.ultimo_pago = ultimo_pago
        except:
            pass
            
        # Verificar si tiene pagos recientes (últimos 2 meses)
        try:
            pago_reciente = Pago.query.filter(
                Pago.alumno_id == alumno.id,
                Pago.fecha_creacion >= fecha_limite
            ).first()
            
            # Verificar asistencias recientes
            asistencia_reciente = Asistencia.query.filter(
                Asistencia.alumno_id == alumno.id,
                Asistencia.fecha_clase >= fecha_limite
            ).first()
            
            # Marcar como inactivo si no tiene pagos NI asistencias recientes
            if not pago_reciente and not asistencia_reciente:
                alumno.inactivo_temporal = True
        except:
            alumno.inactivo_temporal = True
    
    return render_template('alumnos_mejorado.html', 
                         alumnos=todos_alumnos,
                         current_year=current_year)

# Continúa con todas las rutas...
# (Por brevedad, incluiré las rutas principales. El archivo completo sería muy largo)

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

# Initialize database and run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        inicializar_categorias_gastos()
    app.run(debug=True, port=5000)