from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from models import db, Alumno, HorarioSemanal, Asistencia, Clase, EventoCalendario
from utils.student_auth import student_login_required

student_portal_bp = Blueprint('student_portal', __name__, url_prefix='/portal')

@student_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login para alumnos usando Email y DNI"""
    if 'student_id' in session:
        return redirect(url_for('student_portal.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') # El DNI será la contraseña inicial

        student = Alumno.query.filter_by(email=email, activo=True).first()

        # Si no tiene password_hash, usamos el DNI como contraseña inicial
        if student:
            is_valid = False
            if student.password_hash:
                is_valid = check_password_hash(student.password_hash, password)
            else:
                # Si no hay hash, el password debe coincidir con el DNI
                is_valid = (student.dni == password)
                if is_valid:
                    # Guardamos el hash para el futuro
                    student.password_hash = generate_password_hash(password)
                    db.session.commit()

            if is_valid:
                session['student_id'] = student.id
                session['student_name'] = f"{student.nombre} {student.apellido}"
                flash(f'¡Hola, {student.nombre}! Bienvenido a tu zona personal.', 'success')
                return redirect(url_for('student_portal.dashboard'))
            
        flash('Email o contraseña incorrectos.', 'error')

    return render_template('alumno/login.html')

@student_portal_bp.route('/dashboard')
@student_login_required
def dashboard():
    """Panel de control del alumno con el calendario de clases"""
    student = Alumno.query.get(session['student_id'])
    
    # Obtener todas las clases activas para el calendario
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener el conteo de reservas actuales del alumno para esta semana
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    asistencias_semana = Asistencia.query.filter(
        Asistencia.alumno_id == student.id,
        Asistencia.fecha_clase >= inicio_semana,
        Asistencia.fecha_clase <= fin_semana
    ).count()

    return render_template('alumno/dashboard.html', 
                           student=student, 
                           horarios=horarios,
                           asistencias_semana=asistencias_semana)

@student_portal_bp.route('/perfil', methods=['GET', 'POST'])
@student_login_required
def perfil():
    """Edición de perfil del alumno"""
    student = Alumno.query.get(session['student_id'])
    
    if request.method == 'POST':
        student.telefono = request.form.get('telefono')
        student.direccion = request.form.get('direccion')
        
        new_password = request.form.get('new_password')
        if new_password:
            student.password_hash = generate_password_hash(new_password)
            
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
    
    # Lógica de validación de cuota (simplificada)
    # TODO: Implementar lógica robusta según tipo_cuota
    
    fecha_reserva = date.today() # En un sistema real, el alumno elegiría el día
    
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
