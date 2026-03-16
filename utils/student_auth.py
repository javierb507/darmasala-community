from functools import wraps
from flask import session, redirect, url_for, flash
from models import Alumno

def student_login_required(f):
    """Decorador para proteger rutas del portal de alumnos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Por favor, inicia sesión para acceder al portal.', 'warning')
            return redirect(url_for('student_portal.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_student():
    """Obtener el alumno actual de la sesión"""
    if 'student_id' in session:
        return Alumno.query.get(session['student_id'])
    return None
