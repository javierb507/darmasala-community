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

    # Relación con pagos
    pagos = db.relationship('Pago', backref='alumno', lazy=True)
    
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
    tipo_pago = db.Column(db.String(20), default='cuota')  # cuota, matricula, clase_suelta
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
    
    # Relación con clase
    clase = db.relationship('Clase', backref='horarios')
    
    def __repr__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f'<Horario {dias[self.dia_semana]} {self.hora_inicio} - {self.hora_fin}>'
    
    def get_dia_display(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[self.dia_semana]

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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

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
            
            # Marcar como inactivo si no tiene pagos recientes
            if not pago_reciente:
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
    current_year = date.today().year
    return render_template('ver_alumno_compacto.html', alumno=alumno, pagos=pagos, current_year=current_year)

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
            elif tipo_pago == 'matricula':
                año = int(request.form.get('año', date.today().year))
            elif tipo_pago == 'clase_suelta':
                fecha_clase = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
            
            # Crear descripción según el tipo de pago
            descripciones = {
                'cuota': f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                'matricula': f'Matrícula anual {año}',
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

    return render_template('agregar_pago.html', alumno=alumno, current_year=date.today().year)

# Rutas para Clases
@app.route('/clases')
def clases():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases.html', clases=clases)

@app.route('/horarios')
def horarios():
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return render_template('horarios.html', horarios=horarios)

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

# Initialize database and run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
    app.run(debug=True, port=5000)