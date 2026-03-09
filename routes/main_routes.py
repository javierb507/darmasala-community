from flask import Blueprint, render_template, redirect, url_for, request
from datetime import datetime, date, timedelta
from models import Alumno, EventoCalendario, Asistencia, db
from utils.auth_utils import login_required
from utils.app_utils import obtener_sutra_semanal, obtener_proximas_citas

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Página principal (Dashboard) Enfoque premium"""
    # Obtener fecha de la URL o usar hoy
    fecha_str = request.args.get('fecha')
    try:
        if fecha_str:
            hoy = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            hoy = date.today()
    except ValueError:
        hoy = date.today()
    
    # Próximas sesiones de yogaterapia (individuales)
    proximas_citas = obtener_proximas_citas(limite=5)
    
    # 1. Sesiones recurrentes para el día seleccionado
    dia_semana_hoy = hoy.weekday()
    from models import HorarioSemanal
    horarios_hoy = HorarioSemanal.query.filter_by(dia_semana=dia_semana_hoy, activo=True).all()
    
    sesiones_hoy_provinientes = []
    
    for h in horarios_hoy:
        sesiones_hoy_provinientes.append({
            'id': h.id,
            'titulo': h.clase.nombre,
            'hora_inicio': h.hora_inicio,
            'hora_fin': h.hora_fin,
            'instructor': h.instructor,
            'color': h.clase.color,
            'tipo': 'recurrente',
            'horario_id': h.id,
            'clase': h.clase.nombre
        })
    
    # 2. Eventos individuales para hoy
    hoy_inicio = datetime.combine(hoy, datetime.min.time())
    hoy_fin = datetime.combine(hoy, datetime.max.time())
    
    eventos_especiales = EventoCalendario.query.filter(
        EventoCalendario.fecha_inicio >= hoy_inicio,
        EventoCalendario.fecha_inicio <= hoy_fin,
        EventoCalendario.activo == True
    ).order_by(EventoCalendario.fecha_inicio).all()
    
    for e in eventos_especiales:
        sesiones_hoy_provinientes.append({
            'id': e.id,
            'titulo': e.titulo,
            'hora_inicio': e.fecha_inicio.time(),
            'hora_fin': e.fecha_fin.time(),
            'instructor': e.instructor,
            'color': e.color,
            'tipo': 'individual',
            'evento_id': e.id,
            'clase': e.clase.nombre if e.clase else 'Evento'
        })
        
    # Ordenar todas por hora de inicio
    sesiones_hoy_provinientes.sort(key=lambda x: x['hora_inicio'])
    
    # Estadísticas
    total_alumnos_activos = Alumno.query.filter_by(activo=True).count()
    sesiones_count = len(sesiones_hoy_provinientes)
    
    # Obtener sutra semanal
    sutra_semanal = obtener_sutra_semanal()
    
    # --- ESTADÍSTICAS DE ASISTENCIA (NUEVO) ---
    # Asistencia esta semana (desde el lunes)
    hoy_weekday = hoy.weekday()
    lunes_semana = hoy - timedelta(days=hoy_weekday)
    
    asistencias_semana = Asistencia.query.filter(
        Asistencia.fecha_clase >= lunes_semana,
        Asistencia.fecha_clase <= hoy,
        Asistencia.presente == True
    ).count()
    
    # Asistencia el mismo día de la semana pasada (comparativa)
    lunes_pasado = lunes_semana - timedelta(days=7)
    domingo_pasado = lunes_semana - timedelta(days=1)
    
    asistencias_semana_pasada = Asistencia.query.filter(
        Asistencia.fecha_clase >= lunes_pasado,
        Asistencia.fecha_clase <= domingo_pasado,
        Asistencia.presente == True
    ).count()
    
    # Porcentaje de cambio
    cambio_asistencia = 0
    if asistencias_semana_pasada > 0:
        cambio_asistencia = ((asistencias_semana - asistencias_semana_pasada) / asistencias_semana_pasada) * 100

    # Datos para gráfico simple (7 días hasta la fecha seleccionada)
    grafico_asistencia = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        count = Asistencia.query.filter_by(fecha_clase=d, presente=True).count()
        grafico_asistencia.append({
            'dia': d.strftime('%d/%m'),
            'count': count
        })
    
    return render_template('index.html', 
                         proximas_citas=proximas_citas,
                         sesiones_hoy=sesiones_hoy_provinientes,
                         total_alumnos=total_alumnos_activos,
                         sesiones_count=sesiones_count,
                         sutra_semanal=sutra_semanal,
                         asistencias_semana=asistencias_semana,
                         cambio_asistencia=round(cambio_asistencia, 1),
                         grafico_asistencia=grafico_asistencia,
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
