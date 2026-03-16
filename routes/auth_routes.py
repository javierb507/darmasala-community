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
        return redirect(url_for('auth.setup'))

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
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    # Obtener sutra semanal para mostrar en login
    sutra_semanal = obtener_sutra_semanal()
    return render_template('auth/login.html', sutra_semanal=sutra_semanal)

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """Configuración inicial del primer administrador"""
    # Si ya hay usuarios, esta ruta no debe permitirse
    if Usuario.query.count() > 0:
        flash('El sistema ya ha sido inicializado.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')

        if not all([username, password, nombre, apellido, email]):
            flash('Todos los campos son obligatorios', 'error')
        elif password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        else:
            new_admin = Usuario(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                nombre=nombre,
                apellido=apellido,
                rol='admin',
                activo=True
            )
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador creado correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/setup.html')

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))
