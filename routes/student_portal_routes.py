from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from models import db, Alumno, Usuario, HorarioSemanal, Asistencia, Clase, EventoCalendario
from utils.student_auth import student_login_required

student_portal_bp = Blueprint('student_portal', __name__, url_prefix='/portal')

def get_quota_details(alumno):
    """Retorna el límite de clases y el periodo para el alumno"""
    limits = {
        'clase_suelta': (1, 'semanal'),
        '1_clase_semanal': (1, 'semanal'),
        '2_clases_semanal': (2, 'semanal'),
        'plana': (99, 'semanal'),
        '1_clase_bimensual': (2, 'mensual'), # 2 al mes
        '2_clases_bimensual': (4, 'mensual'), # 4 al mes
        'yogaterapia_individual': (1, 'semanal'),
        'yogaterapia_pareja': (1, 'semanal')
    }
    return limits.get(alumno.tipo_cuota, (1, 'semanal'))

def get_reservation_count(alumno_id, start_date, end_date):
    """Cuenta asistencias en un periodo dado"""
    return Asistencia.query.filter(
        Asistencia.alumno_id == alumno_id,
        Asistencia.fecha_clase >= start_date,
        Asistencia.fecha_clase <= end_date
    ).count()

@student_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login para alumnos usando Email y DNI"""
    if 'student_id' in session:
        return redirect(url_for('student_portal.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Buscamos en la tabla de usuarios (que está sincronizada con alumnos)
        user = Usuario.query.filter_by(email=email, rol='alumno', activo=True).first()

        if user and check_password_hash(user.password_hash, password):
            # Encontrar el alumno asociado al email
            student = Alumno.query.filter_by(email=email).first()
            if student:
                session['student_id'] = student.id
                session['user_id_portal'] = user.id # ID de usuario para gestión
                session['student_name'] = f"{student.nombre} {student.apellido}"
                
                # Actualizar último acceso del usuario
                user.ultimo_acceso = datetime.utcnow()
                db.session.commit()
                
                flash(f'¡Hola, {student.nombre}! Bienvenido a tu zona personal.', 'success')
                return redirect(url_for('student_portal.dashboard'))
            
        flash('Email o contraseña incorrectos.', 'error')

    from models import Configuracion
    configuraciones = Configuracion.query.all()
    config_dict = {c.clave: c.valor for c in configuraciones}

    return render_template('alumno/login.html', config=config_dict)

@student_portal_bp.route('/dashboard')
@student_login_required
def dashboard():
    """Panel de control del alumno con el calendario de clases"""
    student = Alumno.query.get(session['student_id'])
    
    # Obtener todas las clases activas para el calendario
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener info de cuota
    limite, periodo = get_quota_details(student)
    
    # Calcular periodo actual
    hoy = date.today()
    if periodo == 'semanal':
        inicio = hoy - timedelta(days=hoy.weekday())
        fin = inicio + timedelta(days=6)
    else: # mensual
        inicio = hoy.replace(day=1)
        if hoy.month == 12:
            fin = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fin = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
            
    consumidas = get_reservation_count(student.id, inicio, fin)
    
    # Obtener próximas reservas
    proximas = Asistencia.query.filter(
        Asistencia.alumno_id == student.id,
        Asistencia.fecha_clase >= hoy
    ).order_by(Asistencia.fecha_clase.asc()).all()
    
    # Obtener configuración
    from models import Configuracion
    configuraciones = Configuracion.query.all()
    config_dict = {c.clave: c.valor for c in configuraciones}
    
    return render_template('alumno/dashboard.html', 
                           student=student, 
                           asistencias_semana=consumidas,
                           limite_semanal=limite,
                           periodo_text=periodo,
                           inicio_periodo=inicio,
                           fin_periodo=fin,
                           config=config_dict,
                           proximas_reservas=proximas)


@student_portal_bp.route('/eventos')
@student_login_required
def eventos():
    """Genera los eventos para FullCalendar basándose en el horario semanal"""
    # Mostrar las clases de las últimas 2 semanas y las próximas 4 semanas
    start_date = date.today() - timedelta(days=14)
    end_date = date.today() + timedelta(days=28)
    
    student_id = session['student_id']
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Reservas actuales del alumno
    reservas = Asistencia.query.filter(
        Asistencia.alumno_id == student_id,
        Asistencia.fecha_clase >= start_date,
        Asistencia.fecha_clase <= end_date
    ).all()
    
    reserva_map = { (r.horario_id, r.fecha_clase): r for r in reservas }
    
    events = []
    curr = start_date
    while curr <= end_date:
        dia_semana = curr.weekday() # 0 = Lunes, 6 = Domingo
        
        for h in horarios:
            if h.dia_semana == dia_semana:
                # Verificar si ya está reservada por el alumno
                reservada = (h.id, curr) in reserva_map
                
                # Contar ocupación total para ese día/horario
                ocupacion = Asistencia.query.filter_by(horario_id=h.id, fecha_clase=curr).count()
                completa = ocupacion >= h.capacidad_maxima
                
                title = f"{h.clase.nombre}"
                if reservada:
                    title = f"✅ {title}"
                elif completa:
                    title = f"❌ {title} (Completa)"
                
                event = {
                    'id': h.id,
                    'title': title,
                    'start': f"{curr}T{h.hora_inicio.strftime('%H:%M:%S')}",
                    'end': f"{curr}T{h.hora_fin.strftime('%H:%M:%S')}",
                    'backgroundColor': h.clase.color,
                    'borderColor': h.clase.color,
                    'extendedProps': {
                        'horario_id': h.id,
                        'fecha': curr.strftime('%Y-%m-%d'),
                        'reservada': reservada,
                        'completa': completa,
                        'ocupacion': f"{ocupacion}/{h.capacidad_maxima}",
                        'instructor': h.instructor or 'Minouche'
                    }
                }
                
                # Dim if complete and not reserved
                if completa and not reservada:
                    event['classNames'] = ['event-full']
                
                events.append(event)
        
        curr += timedelta(days=1)
        
    return jsonify(events)

@student_portal_bp.route('/perfil', methods=['GET', 'POST'])
@student_login_required
def perfil():
    """Edición de perfil del alumno"""
    student = Alumno.query.get(session['student_id'])
    
    if request.method == 'POST':
        student.telefono = request.form.get('telefono')
        student.direccion = request.form.get('direccion')
        
        # Sincronizar con el usuario si cambia la contraseña
        user = Usuario.query.filter_by(email=student.email).first()
        
        new_password = request.form.get('new_password')
        if new_password and user:
            user.password_hash = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('student_portal.perfil'))

    return render_template('alumno/perfil.html', student=student)

@student_portal_bp.route('/reservar/<int:horario_id>', methods=['POST'])
@student_login_required
def reservar(horario_id):
    """Reservar una clase"""
    student = Alumno.query.get(session['student_id'])
    horario = HorarioSemanal.query.get_or_404(horario_id)
    
    # Lógica de validación de cuota
    limite, periodo = get_quota_details(student)
    
    fecha_str = request.json.get('fecha') if request.is_json else request.form.get('fecha')
    if not fecha_str:
        fecha_reserva = date.today()
    else:
        fecha_reserva = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    # Calcular rango para el límite
    if periodo == 'semanal':
        inicio_p = fecha_reserva - timedelta(days=fecha_reserva.weekday())
        fin_p = inicio_p + timedelta(days=6)
    else: # mensual
        inicio_p = fecha_reserva.replace(day=1)
        if fecha_reserva.month == 12:
            fin_p = fecha_reserva.replace(year=fecha_reserva.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fin_p = fecha_reserva.replace(month=fecha_reserva.month + 1, day=1) - timedelta(days=1)

    reservas_periodo = get_reservation_count(student.id, inicio_p, fin_p)
    
    if reservas_periodo >= limite:
        return jsonify({
            'success': False, 
            'message': f'Has agotado tus clases para el periodo ({limite} clases {periodo}).'
        })
    
    if fecha_reserva < date.today():
        return jsonify({'success': False, 'message': 'No puedes reservar clases en fechas pasadas.'})

    # Verificar si ya tiene reserva para este horario y día
    existente = Asistencia.query.filter_by(
        alumno_id=student.id, 
        horario_id=horario_id, 
        fecha_clase=fecha_reserva
    ).first()
    
    if existente:
        return jsonify({'success': False, 'message': 'Ya tienes una reserva para esta clase.'})

    # Verificar capacidad
    ocupacion = Asistencia.query.filter_by(horario_id=horario_id, fecha_clase=fecha_reserva).count()
    if ocupacion >= horario.capacidad_maxima:
        return jsonify({'success': False, 'message': 'Lo sentimos, esta clase está completa.'})

    nueva_reserva = Asistencia(
        alumno_id=student.id,
        horario_id=horario_id,
        fecha_clase=fecha_reserva,
        presente=True,
        observaciones='Reserva desde el portal del alumno'
    )
    
    db.session.add(nueva_reserva)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Reserva realizada con éxito.'})

@student_portal_bp.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('student_portal.login'))
