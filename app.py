from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os

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

    # Relación con pagos
    pagos = db.relationship('Pago', backref='alumno', lazy=True)
    
    def __repr__(self):
        return f'<Alumno {self.nombre} {self.apellido}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
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
    activa = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Clase {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activa': self.activa
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
    horario_id = db.Column(db.Integer, db.ForeignKey('horario_semanal.id'), nullable=False)
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
            'clase_nombre': self.horario.clase.nombre,
            'dia_display': self.horario.get_dia_display(),
            'fecha_clase': self.fecha_clase.isoformat(),
            'presente': self.presente,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat()
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    alumnos = Alumno.query.filter_by(activo=True).all()
    return render_template('alumnos.html', alumnos=alumnos)

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
    pagos = Pago.query.filter_by(alumno_id=alumno_id).order_by(Pago.mes.desc()).all()
    return render_template('ver_alumno.html', alumno=alumno, pagos=pagos)

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
            alumno.tipo_cuota = request.form.get('tipo_cuota', '1_clase')
            
            db.session.commit()
            flash('¡Alumno actualizado exitosamente!', 'success')
            return redirect(url_for('ver_alumno', alumno_id=alumno.id))
        except Exception as e:
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_alumno.html', alumno=alumno)

@app.route('/alumnos/<int:alumno_id>/eliminar', methods=['POST'])
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    alumno.activo = False
    db.session.commit()
    flash('¡Alumno desactivado exitosamente!', 'success')
    return redirect(url_for('alumnos'))

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

@app.route('/horarios/nuevo', methods=['GET', 'POST'])
def nuevo_horario():
    if request.method == 'POST':
        try:
            # Procesar múltiples horarios desde el formulario
            horarios_data = request.form.getlist('horarios[]')
            horarios_creados = 0
            
            for horario_data in horarios_data:
                if horario_data:  # Verificar que no esté vacío
                    data = horario_data.split('|')
                    if len(data) == 3:  # clase_id|dia_semana|hora_inicio
                        clase_id, dia_semana, hora_inicio = data
                        
                        # Calcular hora de fin (1 hora y 15 minutos)
                        hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
                        hora_fin_obj = datetime.combine(date.today(), hora_inicio_obj) + timedelta(hours=1, minutes=15)
                        hora_fin_obj = hora_fin_obj.time()
                        
                        horario = HorarioSemanal(
                            clase_id=int(clase_id),
                            dia_semana=int(dia_semana),
                            hora_inicio=hora_inicio_obj,
                            hora_fin=hora_fin_obj,
                            instructor='Minouche'
                        )
                        db.session.add(horario)
                        horarios_creados += 1
            
            db.session.commit()
            flash(f'¡{horarios_creados} horarios creados exitosamente!', 'success')
            return redirect(url_for('horarios'))
        except Exception as e:
            flash(f'Error al crear horarios: {str(e)}', 'error')
            db.session.rollback()
    
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('calendario_horarios.html', clases=clases)

@app.route('/asistencias')
def asistencias():
    # Obtener asistencias de la semana actual
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    asistencias = Asistencia.query.filter(
        Asistencia.fecha_clase >= inicio_semana,
        Asistencia.fecha_clase <= fin_semana
    ).order_by(Asistencia.fecha_clase.desc(), Asistencia.horario_id).all()
    
    return render_template('asistencias.html', asistencias=asistencias, 
                         inicio_semana=inicio_semana, fin_semana=fin_semana)

@app.route('/asistencias/registrar', methods=['GET', 'POST'])
def registrar_asistencia():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            alumno_id = int(request.form['alumno_id'])
            horario_id = int(request.form['horario_id'])
            fecha_clase = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
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
            return redirect(url_for('asistencias'))
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
def crear_datos_prueba():
    import random
    from datetime import date, timedelta
    
    # Crear 10 alumnos de prueba
    nombres = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Sofia', 'Patricia', 'Rosa', 'Mónica']
    apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín']
    
    for i in range(10):
        alumno_existente = Alumno.query.filter_by(email=f"alumno{i+1}@test.com").first()
        if not alumno_existente:
            alumno = Alumno(
                nombre=random.choice(nombres),
                apellido=random.choice(apellidos),
                email=f"alumno{i+1}@test.com",
                telefono=f"6{random.randint(10000000, 99999999)}",
                fecha_nacimiento=date(1960 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)),
                direccion=f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja'])} {random.randint(1, 100)}",
                condiciones_medicas=random.choice(['Ninguna', 'Hipertensión', 'Diabetes', 'Problemas de espalda', '']),
                tipo_cuota=random.choice(['clase_suelta', '1_clase_semanal', '2_clases_semanal', 'plana', '1_clase_bimensual', '2_clases_bimensual'])
            )
            db.session.add(alumno)
    
    try:
        db.session.commit()
        print("✅ Datos de prueba creados exitosamente")
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear datos de prueba: {e}")

# Rutas para Configuración
@app.route('/configuracion')
def configuracion():
    configuraciones = Configuracion.query.all()
    config_dict = {config.clave: config.valor for config in configuraciones}
    return render_template('configuracion.html', config=config_dict)

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

# Rutas API
@app.route('/api/alumnos')
def api_alumnos():
    alumnos = Alumno.query.filter_by(activo=True).all()
    return jsonify([alumno.to_dict() for alumno in alumnos])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        crear_datos_prueba()
    app.run(debug=True, host='0.0.0.0', port=5000)
