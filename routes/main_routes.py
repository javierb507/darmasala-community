from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime, date
from models import Alumno, EventoCalendario
from utils.auth_utils import login_required
from utils.app_utils import obtener_sutra_semanal, obtener_proximas_citas

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Página principal (Dashboard) Enfoque premium"""
    hoy = date.today()
    
    # Próximas sesiones de yogaterapia (individuales)
    proximas_citas = obtener_proximas_citas(limite=5)
    
    # Sesiones de cualquier tipo para hoy
    hoy_inicio = datetime.combine(hoy, datetime.min.time())
    hoy_fin = datetime.combine(hoy, datetime.max.time())
    
    sesiones_hoy = EventoCalendario.query.filter(
        EventoCalendario.fecha_inicio >= hoy_inicio,
        EventoCalendario.fecha_inicio <= hoy_fin,
        EventoCalendario.activo == True
    ).order_by(EventoCalendario.fecha_inicio).all()
    
    # Estadísticas
    total_alumnos_activos = Alumno.query.filter_by(activo=True).count()
    sesiones_count = len(sesiones_hoy)
    
    # Obtener sutra semanal
    sutra_semanal = obtener_sutra_semanal()
    
    return render_template('index.html', 
                         proximas_citas=proximas_citas,
                         sesiones_hoy=sesiones_hoy,
                         total_alumnos=total_alumnos_activos,
                         sesiones_count=sesiones_count,
                         sutra_semanal=sutra_semanal,
                         today=hoy)

@main_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """Redirección para compatibilidad con la URL /dashboard"""
    return redirect(url_for('main.index'))

@main_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    from flask import send_from_directory, current_app
    import os
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
