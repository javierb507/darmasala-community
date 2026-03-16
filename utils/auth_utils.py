from functools import wraps
from flask import session, redirect, url_for, flash
from models import Usuario

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación.
    Si el usuario es un alumno, le redirige a su portal."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Si es un alumno intentando acceder a la administración
        if session.get('rol') == 'alumno':
            return redirect(url_for('student_portal.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para rutas que solo el administrador puede acceder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('rol') != 'admin':
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Obtener el usuario actual de la sesión"""
    if 'user_id' in session:
        return Usuario.query.get(session['user_id'])
    return None
