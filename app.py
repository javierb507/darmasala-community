from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
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
    precio = db.Column(db.Float, default=15.00)  # Precio base de la clase
    color = db.Column(db.String(7), default='#007bff')  # Color para visualización
    nivel = db.Column(db.String(20), default='todos')  # principiante, intermedio, avanzado, todos
    duracion_minutos = db.Column(db.Integer, default=75)
    capacidad_maxima = db.Column(db.Integer, default=15)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    horarios = db.relationship('HorarioSemanal', backref='clase', lazy=True)
    
    def __repr__(self):
        return f'<Clase {self.nombre}>'
    
    def get_precio_por_tipo(self, tipo_cuota):
        """Obtiene el precio según el tipo de cuota"""
        precios = {
            'clase_suelta': self.precio_clase_suelta,
            '1_clase_semanal': self.precio_1_semanal,
            '2_clases_semanal': self.precio_2_semanal,
            'plana': self.precio_plana,
            '1_clase_bimensual': self.precio_1_bimensual,
            '2_clases_bimensual': self.precio_2_bimensual
        }
        return precios.get(tipo_cuota, self.precio_1_semanal)

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

# Modelo de Configuración
class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracion {self.clave}: {self.valor}>'

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
    nombre_persona = db.Column(db.String(100), nullable=False)  # Nombre de la persona
    email_persona = db.Column(db.String(100))  # Email opcional
    telefono_persona = db.Column(db.String(20))  # Teléfono opcional
    fecha_sesion = db.Column(db.Date, nullable=False)
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
    archivos = db.relationship('ArchivoYogaterapia', backref='sesion_yogaterapia', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SesionYogaterapia {self.nombre_persona} - {self.fecha_sesion}>'

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
    # Dashboard simple sin estadísticas
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    # Obtener parámetros de búsqueda y ordenación
    buscar = request.args.get('buscar', '').strip()
    orden = request.args.get('orden', 'alfabetico')  # alfabetico, antiguedad
    
    # Construir consulta base
    query = Alumno.query
    
    # Aplicar filtro de búsqueda si existe
    if buscar:
        query = query.filter(
            or_(
                Alumno.nombre.ilike(f'%{buscar}%'),
                Alumno.apellido.ilike(f'%{buscar}%'),
                Alumno.email.ilike(f'%{buscar}%')
            )
        )
    
    # Aplicar ordenación
    if orden == 'antiguedad':
        query = query.order_by(Alumno.fecha_registro.asc())
    else:  # alfabético por defecto
        query = query.order_by(Alumno.apellido.asc(), Alumno.nombre.asc())
    
    todos_alumnos = query.all()
    current_year = date.today().year
    current_month = date.today().month
    
    # Fecha límite para considerar inactividad (2 meses)
    fecha_limite = date.today() - timedelta(days=60)
    
    for alumno in todos_alumnos:
        # Inicializar propiedades
        alumno.inactivo_temporal = False
        alumno.ultimo_pago = None
        alumno.pago_mes_actual = False
        
        # Obtener el último pago
        try:
            ultimo_pago = Pago.query.filter_by(alumno_id=alumno.id).order_by(Pago.fecha_creacion.desc()).first()
            if ultimo_pago:
                alumno.ultimo_pago = ultimo_pago
        except:
            pass
        
        # Verificar si ha pagado el mes actual
        alumno.pago_mes_actual = False
        
        if alumno.tipo_cuota in ['1_clase_bimensual', '2_clases_bimensual']:
            # Para cuotas bimensuales, verificar si pagó en este bimestre
            # Los bimestres son: Ene-Feb, Mar-Abr, May-Jun, Jul-Ago, Sep-Oct, Nov-Dic
            bimestre_actual = ((current_month - 1) // 2) * 2 + 1  # Primer mes del bimestre
            mes1 = bimestre_actual
            mes2 = bimestre_actual + 1
            
            # Verificar pagos en cualquiera de los dos meses del bimestre
            pago_bimestre = Pago.query.filter(
                Pago.alumno_id == alumno.id,
                Pago.tipo_pago == 'cuota',
                or_(
                    Pago.mes == f"{current_year}-{mes1:02d}",
                    Pago.mes == f"{current_year}-{mes2:02d}"
                )
            ).first()
            
            alumno.pago_mes_actual = bool(pago_bimestre)
        else:
            # Para cuotas mensuales, verificar solo el mes actual
            mes_actual_str = f"{current_year}-{current_month:02d}"
            pago_mes_actual = Pago.query.filter(
                Pago.alumno_id == alumno.id,
                Pago.tipo_pago == 'cuota',
                Pago.mes == mes_actual_str
            ).first()
            
            alumno.pago_mes_actual = bool(pago_mes_actual)
            
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

@app.route('/alumnos/nuevo', methods=['GET', 'POST'])
def nuevo_alumno():
    if request.method == 'POST':
        try:
            matricula_pagada = 'matricula_pagada' in request.form
            fecha_matricula = date.today() if matricula_pagada else None
            
            alumno = Alumno(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
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
    pagos = Pago.query.filter_by(alumno_id=alumno_id).order_by(Pago.fecha_creacion.desc()).all()
    
    # Calcular año de matrícula (25/26 comienza en septiembre)
    current_date = date.today()
    if current_date.month >= 9:  # Septiembre o después
        matricula_year = f"{current_date.year % 100}/{(current_date.year + 1) % 100}"
    else:  # Antes de septiembre
        matricula_year = f"{(current_date.year - 1) % 100}/{current_date.year % 100}"
    
    # Obtener asistencias del alumno con información de clase
    asistencias = db.session.query(Asistencia).join(HorarioSemanal).join(Clase)\
        .filter(Asistencia.alumno_id == alumno_id)\
        .order_by(Asistencia.fecha_clase.desc()).limit(20).all()
    
    # Calcular estadísticas de asistencia
    total_asistencias = len(asistencias)
    asistencias_presentes = sum(1 for a in asistencias if a.presente)
    porcentaje_asistencia = round((asistencias_presentes / total_asistencias * 100), 1) if total_asistencias > 0 else 0
    
    # Las sesiones de yogaterapia ya no están asociadas a alumnos específicos
    sesiones_yogaterapia = []
    
    return render_template('ver_alumno_compacto.html', 
                         alumno=alumno, 
                         pagos=pagos, 
                         matricula_year=matricula_year,
                         asistencias=asistencias,
                         total_asistencias=total_asistencias,
                         asistencias_presentes=asistencias_presentes,
                         porcentaje_asistencia=porcentaje_asistencia,
                         sesiones_yogaterapia=sesiones_yogaterapia)

@app.route('/alumnos/<int:alumno_id>/editar', methods=['GET', 'POST'])
def editar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
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

    # Calcular año de matrícula (25/26 comienza en septiembre)
    current_date = date.today()
    if current_date.month >= 9:  # Septiembre o después
        matricula_year = f"{current_date.year % 100}/{(current_date.year + 1) % 100}"
        matricula_year_numeric = current_date.year
    else:  # Antes de septiembre
        matricula_year = f"{(current_date.year - 1) % 100}/{current_date.year % 100}"
        matricula_year_numeric = current_date.year - 1
    
    return render_template('agregar_pago.html', 
                         alumno=alumno, 
                         current_year=date.today().year,
                         matricula_year=matricula_year,
                         matricula_year_numeric=matricula_year_numeric)

@app.route('/pagos/<int:pago_id>/editar', methods=['GET', 'POST'])
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
def clases():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases.html', clases=clases)

@app.route('/horarios')
def horarios():
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return render_template('horarios.html', horarios=horarios)

@app.route('/horarios/calendario')
def horarios_calendario():
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return render_template('horarios_calendario.html', horarios=horarios)

@app.route('/horarios/nuevo', methods=['GET', 'POST'])
def nuevo_horario():
    """Crear nuevo horario semanal"""
    if request.method == 'POST':
        try:
            horario = HorarioSemanal(
                clase_id=int(request.form['clase_id']),
                dia_semana=int(request.form['dia_semana']),
                hora_inicio=datetime.strptime(request.form['hora_inicio'], '%H:%M').time(),
                hora_fin=datetime.strptime(request.form['hora_fin'], '%H:%M').time(),
                instructor=request.form.get('instructor', 'Minouche'),
                activo=True
            )
            db.session.add(horario)
            db.session.commit()
            flash('¡Horario creado exitosamente!', 'success')
            return redirect(url_for('horarios'))
        except Exception as e:
            flash(f'Error al crear horario: {str(e)}', 'error')
            db.session.rollback()
    
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('nuevo_horario.html', clases=clases)

@app.route('/horarios/<int:horario_id>/editar', methods=['GET', 'POST'])
def editar_horario(horario_id):
    """Editar horario existente"""
    horario = HorarioSemanal.query.get_or_404(horario_id)
    
    if request.method == 'POST':
        try:
            horario.clase_id = int(request.form['clase_id'])
            horario.dia_semana = int(request.form['dia_semana'])
            horario.hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            horario.hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            horario.instructor = request.form.get('instructor', 'Minouche')
            horario.activo = 'activo' in request.form
            
            db.session.commit()
            flash('¡Horario actualizado exitosamente!', 'success')
            return redirect(url_for('horarios'))
        except Exception as e:
            flash(f'Error al actualizar horario: {str(e)}', 'error')
            db.session.rollback()
    
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('editar_horario.html', horario=horario, clases=clases)

@app.route('/horarios/<int:horario_id>/eliminar')
def eliminar_horario(horario_id):
    """Eliminar horario (desactivar)"""
    horario = HorarioSemanal.query.get_or_404(horario_id)
    horario.activo = False
    db.session.commit()
    flash('Horario desactivado exitosamente', 'success')
    return redirect(url_for('horarios'))

@app.route('/calendario')
def calendario_unificado():
    """Calendario unificado con actividades periódicas y citas individuales"""
    # Obtener parámetros de fecha
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', datetime.now().month, type=int)
    
    # Obtener sesiones de yogaterapia del mes
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año,
        db.extract('month', SesionYogaterapia.fecha_sesion) == mes
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    return render_template('calendario_unificado.html', 
                         año=año, 
                         mes=mes,
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios,
                         clases=clases)

@app.route('/horarios/calendario-anual')
def calendario_anual():
    """Vista de calendario anual para agendar sesiones individuales"""
    año = request.args.get('año', datetime.now().year, type=int)
    
    # Obtener sesiones de yogaterapia del año
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    return render_template('calendario_anual.html', 
                         año=año, 
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios)

@app.route('/horarios/historico')
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
def yogaterapia():
    """Página principal de yogaterapia (sesiones de yogaterapia)"""
    sesiones = SesionYogaterapia.query.order_by(SesionYogaterapia.fecha_sesion.desc()).all()
    return render_template('yogaterapia.html', sesiones=sesiones)

@app.route('/yogaterapia/nueva')
def nueva_yogaterapia():
    """Formulario para nueva sesión de yogaterapia"""
    return render_template('nueva_yogaterapia.html')

@app.route('/yogaterapia/procesar', methods=['POST'])
def procesar_yogaterapia_general():
    """Procesar nueva sesión de yogaterapia general"""
    try:
        nombre_persona = request.form['nombre_persona']
        email_persona = request.form.get('email_persona', '')
        telefono_persona = request.form.get('telefono_persona', '')
        
        sesion = SesionYogaterapia(
            nombre_persona=nombre_persona,
            email_persona=email_persona,
            telefono_persona=telefono_persona,
            fecha_sesion=datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date(),
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
                    ruta_archivo=filepath,
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
        flash(f'¡Sesión de yogaterapia registrada exitosamente para {nombre_persona}!', 'success')
        return redirect(url_for('yogaterapia'))
        
    except Exception as e:
        flash(f'Error al registrar sesión: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('nueva_yogaterapia'))

@app.route('/yogaterapia/<int:sesion_id>')
def ver_sesion_yogaterapia(sesion_id):
    """Ver detalles de una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    archivos = ArchivoYogaterapia.query.filter_by(sesion_yogaterapia_id=sesion_id).all()
    return render_template('ver_sesion_yogaterapia.html', sesion=sesion, archivos=archivos)

@app.route('/yogaterapia/<int:sesion_id>/editar', methods=['GET', 'POST'])
def editar_sesion_yogaterapia(sesion_id):
    """Editar una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos de la sesión
            sesion.fecha_sesion = datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date()
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
                        ruta_archivo=filepath,
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

@app.route('/yogaterapia/<int:sesion_id>/marcar_pagado', methods=['POST'])
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
def nueva_yogaterapia_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            sesion = SesionYogaterapia(
                nombre_persona=f"{alumno.nombre} {alumno.apellido}",
                email_persona=alumno.email,
                telefono_persona=alumno.telefono,
                fecha_sesion=datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date(),
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
                        ruta_archivo=filepath,
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
    
    return render_template('nueva_yogaterapia.html', alumno=alumno, from_student=True)

# RUTAS PARA GESTIÓN ECONÓMICA

@app.route('/economia')
def economia():
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
    
    return render_template('economia/dashboard_mejorado.html',
                         periodo=periodo,
                         año=año,
                         mes=mes,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         ingresos_cuotas=ingresos_cuotas,
                         ingresos_matriculas=ingresos_matriculas,
                         ingresos_clases_sueltas=ingresos_clases_sueltas,
                         total_ingresos=total_ingresos,
                         total_gastos=total_gastos,
                         balance=balance)

@app.route('/gastos-mensuales')
def gastos_mensuales():
    """Vista de gastos mensuales"""
    gastos = GastoMensual.query.order_by(GastoMensual.fecha.desc()).all()
    return render_template('gastos_mensuales.html', gastos=gastos)

@app.route('/proveedores')
def proveedores():
    """Lista de proveedores"""
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/proveedores.html', proveedores=proveedores)

@app.route('/facturas')
def facturas():
    """Lista de facturas"""
    facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
    return render_template('economia/facturas.html', facturas=facturas)

# RUTAS DE CONFIGURACIÓN

@app.route('/configuracion')
def configuracion():
    configuraciones = Configuracion.query.all()
    config_dict = {config.clave: config.valor for config in configuraciones}
    clases = Clase.query.order_by(Clase.nombre).all()
    return render_template('configuracion.html', config=config_dict, clases=clases)

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
            ('precio_yogaterapia_individual', request.form.get('precio_yogaterapia_individual', '50.00'), 'Precio yogaterapia individual'),
            ('precio_yogaterapia_pareja', request.form.get('precio_yogaterapia_pareja', '70.00'), 'Precio yogaterapia en pareja'),
            
            # Información de la escuela
            ('nombre_escuela', request.form.get('nombre_escuela', 'Atma suddhi'), 'Nombre de la escuela'),
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
def tipos_clase():
    """Vista de gestión de tipos de clase"""
    tipos = TipoClase.query.order_by(TipoClase.orden, TipoClase.nombre).all()
    return render_template('configuracion/tipos_clase.html', tipos=tipos)

@app.route('/configuracion/tipos-clase/nuevo', methods=['GET', 'POST'])
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
def backup():
    """Página de gestión de backups"""
    return render_template('backup.html')

@app.route('/backup/crear', methods=['POST'])
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
def exportar():
    """Página principal de exportación"""
    return render_template('exportar.html')

# Función para inicializar las clases básicas
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
                'precio_clase_suelta': clase.precio_clase_suelta,
                'precio_1_semanal': clase.precio_1_semanal,
                'precio_2_semanal': clase.precio_2_semanal,
                'precio_plana': clase.precio_plana,
                'precio_1_bimensual': clase.precio_1_bimensual,
                'precio_2_bimensual': clase.precio_2_bimensual,
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

@app.route('/api/backup', methods=['POST'])
def api_backup():
    """API para crear backup de la base de datos"""
    try:
        # TODO: Implementar lógica de backup real
        import shutil
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_yoga_{timestamp}.db'
        
        # Copiar la base de datos actual
        shutil.copy2('yoga_school.db', f'backups/{backup_filename}')
        
        return jsonify({
            'success': True,
            'filename': backup_filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# RUTAS DE GESTIÓN DE CLASES

@app.route('/configuracion/clases/nueva', methods=['GET', 'POST'])
def nueva_clase():
    """Crear nueva clase"""
    if request.method == 'POST':
        try:
            clase = Clase(
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion'),
                precio=float(request.form.get('precio', 15.00)),
                duracion_minutos=int(request.form.get('duracion_minutos', 60)),
                color=request.form.get('color', '#007bff'),
                nivel=request.form.get('nivel', 'todos'),
                capacidad_maxima=int(request.form.get('capacidad_maxima', 15))
            )
            db.session.add(clase)
            db.session.commit()
            flash('¡Clase creada exitosamente!', 'success')
            return redirect(url_for('configuracion'))
        except Exception as e:
            flash(f'Error al crear clase: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('configuracion/nueva_clase.html')

@app.route('/configuracion/clases/<int:clase_id>/editar', methods=['GET', 'POST'])
def editar_clase(clase_id):
    """Editar clase existente"""
    clase = Clase.query.get_or_404(clase_id)
    
    if request.method == 'POST':
        try:
            clase.nombre = request.form['nombre']
            clase.descripcion = request.form.get('descripcion')
            clase.precio = float(request.form.get('precio', 15.00))
            clase.duracion_minutos = int(request.form.get('duracion_minutos', 60))
            clase.color = request.form.get('color', '#007bff')
            clase.nivel = request.form.get('nivel', 'todos')
            clase.capacidad_maxima = int(request.form.get('capacidad_maxima', 15))
            
            db.session.commit()
            flash('¡Clase actualizada exitosamente!', 'success')
            return redirect(url_for('configuracion'))
        except Exception as e:
            flash(f'Error al actualizar clase: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('configuracion/editar_clase.html', clase=clase)

# RUTAS PARA GESTIÓN DE USUARIOS

@app.route('/usuarios')
def usuarios():
    """Lista de usuarios del sistema"""
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
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
def ver_usuario(usuario_id):
    """Ver detalles de un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('ver_usuario.html', usuario=usuario)

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
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

# Initialize database and run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        inicializar_categorias_gastos()
        
        # Crear usuario administrador por defecto si no existe
        admin_existente = Usuario.query.filter_by(username='admin').first()
        if not admin_existente:
            import hashlib
            admin = Usuario(
                username='admin',
                email='admin@atmasuddhi.es',
                password_hash=hashlib.sha256('admin123'.encode()).hexdigest(),
                nombre='Administrador',
                apellido='Sistema',
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado: admin / admin123")
    
    app.run(debug=True, port=5000)