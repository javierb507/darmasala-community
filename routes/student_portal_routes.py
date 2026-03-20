from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from models import db, Alumno, Usuario, HorarioSemanal, Asistencia, Clase, EventoCalendario, SolicitudYogaterapia
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
                
                # Actualizar último acceso del usuario (opcional, no bloqueante)
                try:
                    user.ultimo_acceso = datetime.utcnow()
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error al actualizar último acceso: {e}")
                
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
    """Genera los eventos para FullCalendar basándose en el horario semanal y eventos puntuales"""
    # Mostrar las clases de las últimas 2 semanas y las próximas 4 semanas
    start_date = date.today() - timedelta(days=14)
    end_date = date.today() + timedelta(days=28)
    
    student_id = session['student_id']
    horarios_semanales = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Eventos puntuales (clases únicas)
    # Convertir fechas a datetimes para la consulta
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    eventos_puntuales = EventoCalendario.query.filter(
        EventoCalendario.fecha_inicio >= start_dt,
        EventoCalendario.fecha_inicio <= end_dt,
        EventoCalendario.activo == True
    ).all()
    
    # Reservas actuales del alumno
    reservas = Asistencia.query.filter(
        Asistencia.alumno_id == student_id,
        Asistencia.fecha_clase >= start_date,
        Asistencia.fecha_clase <= end_date
    ).all()
    
    reserva_map = { (r.horario_id, r.evento_id, r.fecha_clase): r for r in reservas }
    
    events = []
    
    # 1. Clases Recurrentes (HorarioSemanal)
    curr = start_date
    while curr <= end_date:
        dia_semana = curr.weekday() # 0 = Lunes, 6 = Domingo
        
        for h in horarios_semanales:
            if h.dia_semana == dia_semana:
                # Verificar si ya está reservada por el alumno
                # Buscamos en reserva_map usando horario_id
                reservada = (h.id, None, curr) in reserva_map
                
                # Contar ocupación: Alumnos en roster + Alumnos con Asistencia NO en roster
                roster_ids = [a.id for a in h.alumnos]
                extra_count = Asistencia.query.filter(
                    Asistencia.horario_id == h.id,
                    Asistencia.fecha_clase == curr,
                    ~Asistencia.alumno_id.in_(roster_ids) if roster_ids else True
                ).count()
                
                ocupacion_total = len(roster_ids) + extra_count
                completa = ocupacion_total >= (h.capacidad_maxima or 15)
                
                title = f"{h.clase.nombre}"
                if reservada:
                    title = f"✅ {title}"
                elif completa:
                    title = f"❌ {title} (Completa)"
                
                # Color de la clase
                color = h.clase.color if h.clase else '#8B5FBF'
                
                event = {
                    'id': f"h_{h.id}_{curr}",
                    'title': title,
                    'start': f"{curr}T{h.hora_inicio.strftime('%H:%M:%S')}",
                    'end': f"{curr}T{h.hora_fin.strftime('%H:%M:%S')}",
                    'backgroundColor': color,
                    'borderColor': color,
                    'extendedProps': {
                        'horario_id': h.id,
                        'evento_id': None,
                        'fecha': curr.strftime('%Y-%m-%d'),
                        'reservada': reservada,
                        'asistencia_id': reserva_map.get((h.id, None, curr)).id if reservada and (h.id, None, curr) in reserva_map else None,
                        'completa': completa,
                        'ocupacion': f"{ocupacion_total}/{h.capacidad_maxima or 15}",
                        'instructor': h.instructor or 'Minouche'
                    }
                }
                
                if completa and not reservada:
                    event['classNames'] = ['event-full']
                
                events.append(event)
        
        curr += timedelta(days=1)
    
    # 2. Eventos Puntuales (EventoCalendario)
    for ev in eventos_puntuales:
        ev_date = ev.fecha_inicio.date()
        # Si es una Yogaterapia personal de otro alumno, no mostrarla
        # Si es una clase puntual (tiene clase_id), mostrarla si es para todos o si el alumno está invitado
        if ev.clase_id or ev.alumno_id == student_id or ev.alumno_id is None:
            reservada = (None, ev.id, ev_date) in reserva_map or ev.alumno_id == student_id
            
            # Para eventos puntuales, la ocupación es diferente (suelen ser 1 a 1 si es Yogaterapia)
            # Si tiene clase_id, puede ser grupal puntual
            ocupacion = Asistencia.query.filter_by(evento_id=ev.id, fecha_clase=ev_date).count()
            capacidad = 1 if ev.alumno_id else 15 # Simplificación
            completa = ocupacion >= capacidad
            
            title = ev.titulo
            if reservada:
                title = f"✅ {title}"
            
            color = ev.color or '#ffc107'
            if ev.clase:
                color = ev.clase.color
            
            event = {
                'id': f"e_{ev.id}",
                'title': title,
                'start': ev.fecha_inicio.isoformat(),
                'end': ev.fecha_fin.isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'horario_id': None,
                    'evento_id': ev.id,
                    'fecha': ev_date.strftime('%Y-%m-%d'),
                    'reservada': reservada,
                    'asistencia_id': reserva_map.get((None, ev.id, ev_date)).id if reservada and (None, ev.id, ev_date) in reserva_map else None,
                    'completa': completa,
                    'ocupacion': f"{ocupacion}/{capacidad}",
                    'instructor': ev.instructor or 'Minouche'
                }
            }
            events.append(event)
            
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

@student_portal_bp.route('/reservar', methods=['POST'])
@student_portal_bp.route('/reservar/<int:horario_id>', methods=['POST'])
@student_login_required
def reservar(horario_id=None):
    """Reservar una clase o evento puntual"""
    student = Alumno.query.get(session['student_id'])
    
    data = request.get_json() if request.is_json else {}
    horario_id = data.get('horario_id') or horario_id
    evento_id = data.get('evento_id')
    fecha_str = data.get('fecha') or request.form.get('fecha')
    
    if not fecha_str:
        return jsonify({'success': False, 'message': 'Fecha no proporcionada.'}), 400
    
    fecha_reserva = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    if fecha_reserva < date.today():
        return jsonify({'success': False, 'message': 'No puedes reservar clases en fechas pasadas.'})

    try:
        # Lógica de validación de cuota (Omitir si es tarifa plana)
        if student.tipo_cuota != 'plana':
            limite, periodo = get_quota_details(student)

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

        # Verificar si ya tiene reserva para este horario/evento y día
        existente = Asistencia.query.filter_by(
            alumno_id=student.id, 
            horario_id=horario_id, 
            evento_id=evento_id,
            fecha_clase=fecha_reserva
        ).first()
        
        if existente:
            return jsonify({'success': False, 'message': 'Ya tienes una reserva para esta sesión.'})

        # Verificar capacidad
        if horario_id:
            horario = HorarioSemanal.query.get_or_404(horario_id)
            # Contar alumnos del roster + extra (Asistencia que no están en roster)
            roster_ids = [a.id for a in horario.alumnos]
            extra_count = Asistencia.query.filter(
                Asistencia.horario_id == horario_id,
                Asistencia.fecha_clase == fecha_reserva,
                ~Asistencia.alumno_id.in_(roster_ids) if roster_ids else True
            ).count()
            
            # Usar capacidad_centro si no hay capacidad_maxima en el horario
            capacidad_max = horario.capacidad_maxima
            if not capacidad_max:
                from models import Configuracion
                config_cap = Configuracion.query.filter_by(clave='capacidad_centro').first()
                capacidad_max = int(config_cap.valor) if config_cap else 15

            if (len(roster_ids) + extra_count) >= capacidad_max:
                return jsonify({'success': False, 'message': 'Lo sentimos, esta clase está completa.'})
        elif evento_id:
            evento = EventoCalendario.query.get_or_404(evento_id)
            # Si es un evento puntual con alumno_id, ya está "reservado" para ese alumno
            if evento.alumno_id and evento.alumno_id != student.id:
                return jsonify({'success': False, 'message': 'Esta sesión privada ya está ocupada.'})
            
            ocupacion = Asistencia.query.filter_by(evento_id=evento_id, fecha_clase=fecha_reserva).count()
            capacidad = 1 if evento.alumno_id else 15
            if ocupacion >= capacidad:
                return jsonify({'success': False, 'message': 'Esta sesión ya está completa.'})

        nueva_reserva = Asistencia(
            alumno_id=student.id,
            horario_id=horario_id,
            evento_id=evento_id,
            fecha_clase=fecha_reserva,
            presente=True,
            observaciones='Reserva desde el portal'
        )
        
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reserva realizada con éxito.'})

    except Exception as e:
        db.session.rollback()
        print(f"Error en reserva: {e}")
        return jsonify({'success': False, 'message': f'Error al procesar la reserva: {str(e)}'})

@student_portal_bp.route('/cancelar-reserva/<int:asistencia_id>', methods=['POST'])
@student_login_required
def cancelar_reserva(asistencia_id):
    """Anula una reserva realizada desde el portal"""
    student_id = session.get('student_id')
    reserva = Asistencia.query.filter_by(id=asistencia_id, alumno_id=student_id).first_or_404()
    
    # Solo permitir cancelar si la clase es hoy o en el futuro
    if reserva.fecha_clase < date.today():
        return jsonify({'success': False, 'message': 'No puedes cancelar sesiones pasadas.'})
        
    try:
        db.session.delete(reserva)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reserva cancelada correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al cancelar: {str(e)}'})

@student_portal_bp.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('student_portal.login'))

@student_portal_bp.route('/solicitar-yogaterapia', methods=['GET', 'POST'])
def solicitar_yogaterapia():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        motivo = request.form.get('motivo')
        
        # Si está logueado, asociar el alumno
        alumno_id = session.get('student_id')
        
        solicitud = SolicitudYogaterapia(
            nombre=nombre,
            email=email,
            telefono=telefono,
            motivo=motivo,
            alumno_id=alumno_id
        )
        
        try:
            db.session.add(solicitud)
            db.session.commit()
            flash('Tu solicitud de Yogaterapia ha sido enviada. Nos pondremos en contacto contigo pronto.', 'success')
            if alumno_id:
                return redirect(url_for('student_portal.dashboard'))
            return redirect(url_for('student_portal.login'))
        except Exception as e:
            db.session.rollback()
            flash('Hubo un error al enviar tu solicitud. Por favor, inténtalo de nuevo.', 'error')
            
    student = None
    if 'student_id' in session:
        student = Alumno.query.get(session['student_id'])
            
    return render_template('alumno/solicitar_yogaterapia.html', student=student)
