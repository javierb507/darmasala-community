from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from models import db, Usuario
from utils.app_utils import obtener_sutra_semanal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Verificación de primer uso: si no hay usuarios, redirigir a setup
    if Usuario.query.count() == 0:
        return redirect(url_for('setup.onboarding'))

    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter(
            ((Usuario.username == username_or_email) | (Usuario.email == username_or_email)),
            Usuario.activo == True
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['rol'] = user.rol
            
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            
            flash(f'¡Bienvenido, {user.nombre}!', 'success')
            
            if user.rol == 'alumno':
                from models import Alumno
                student = Alumno.query.filter_by(email=user.email).first()
                if student:
                    session['student_id'] = student.id
                    session['user_id_portal'] = user.id # ID de usuario para gestión
                    session['student_name'] = f"{student.nombre} {student.apellido}"
                return redirect(url_for('student_portal.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    # Obtener sutra semanal para mostrar en login
    sutra_semanal = obtener_sutra_semanal()
    
    from models import Configuracion
    configuraciones = Configuracion.query.all()
    config_dict = {c.clave: c.valor for c in configuraciones}
    
    return render_template('auth/login.html', sutra_semanal=sutra_semanal, config=config_dict)

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))
