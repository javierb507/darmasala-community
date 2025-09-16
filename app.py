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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    # Mostrar solo alumnos activos
    alumnos_activos = Alumno.query.filter_by(activo=True).all()
    current_year = date.today().year
    return render_template('alumnos.html', 
                         alumnos=alumnos_activos,
                         current_year=current_year)

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

# RUTAS PARA GESTIÓN ECONÓMICA

@app.route('/economia')
def economia():
    """Dashboard principal de gestión económica"""
    # Resumen financiero del mes actual
    current_month = date.today().month
    current_year = date.today().year
    
    # Ingresos del mes
    ingresos_mes = db.session.query(db.func.sum(Ingreso.importe)).filter(
        db.extract('month', Ingreso.fecha) == current_month,
        db.extract('year', Ingreso.fecha) == current_year
    ).scalar() or 0
    
    # Gastos del mes (facturas pagadas)
    gastos_mes = db.session.query(db.func.sum(FacturaProveedor.importe_total)).filter(
        FacturaProveedor.estado == 'pagada',
        db.extract('month', FacturaProveedor.fecha_pago) == current_month,
        db.extract('year', FacturaProveedor.fecha_pago) == current_year
    ).scalar() or 0
    
    # Facturas pendientes
    facturas_pendientes = FacturaProveedor.query.filter_by(estado='pendiente').count()
    
    # Facturas vencidas
    facturas_vencidas = FacturaProveedor.query.filter(
        FacturaProveedor.estado == 'pendiente',
        FacturaProveedor.fecha_vencimiento < date.today()
    ).count()
    
    return render_template('economia/dashboard.html',
                         ingresos_mes=ingresos_mes,
                         gastos_mes=gastos_mes,
                         balance_mes=ingresos_mes - gastos_mes,
                         facturas_pendientes=facturas_pendientes,
                         facturas_vencidas=facturas_vencidas)

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
    return render_template('economia/nuevo_gasto_fijo.html', categorias=categorias)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_clases()
        inicializar_categorias_gastos()
        crear_datos_prueba()
    app.run(debug=True, host='0.0.0.0', port=5000)
