from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from models import db, Clase, HorarioSemanal, Asistencia, EventoCalendario, SesionYogaterapia, Alumno
from utils.auth_utils import login_required
from utils.app_utils import obtener_sutra_semanal, obtener_proximas_citas
from utils.calendar_utils import CalendarioAcademico

class_bp = Blueprint('classes', __name__)

@class_bp.route('/clases')
@login_required
def clases():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases.html', clases=clases)

@class_bp.route('/horarios')
@login_required
def horarios():
    # Obtener todos los horarios activos
    horarios_list = HorarioSemanal.query.filter_by(activo=True).order_by(
        HorarioSemanal.dia_semana,
        HorarioSemanal.hora_inicio
    ).all()

    # Obtener todas las clases
    clases = Clase.query.filter_by(activa=True).all()

    # Calcular estadísticas de periodicidad
    clases_periodicidad = {
        'semanal': Clase.query.filter_by(activa=True, periodicidad='semanal').count(),
        'quincenal': Clase.query.filter_by(activa=True, periodicidad='quincenal').count(),
        'mensual': Clase.query.filter_by(activa=True, periodicidad='mensual').count()
    }

    # Calcular total de horas semanales
    total_horas_semanales = 0
    for horario in horarios_list:
        duracion_horas = horario.clase.duracion_minutos / 60.0
        total_horas_semanales += duracion_horas
    total_horas_semanales = round(total_horas_semanales, 1)

    return render_template('horarios.html',
                         horarios=horarios_list,
                         clases=clases,
                         clases_periodicidad=clases_periodicidad,
                         total_horas_semanales=total_horas_semanales)

@class_bp.route('/horarios/calendario')
@login_required
def horarios_calendario():
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return render_template('horarios_calendario.html', horarios=horarios)

@class_bp.route('/horarios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_horario():
    """Crear nuevo horario semanal"""
    if request.method == 'POST':
        try:
            clase_id = int(request.form['clase_id'])
            dia_semana = int(request.form['dia_semana'])
            hora_inicio_str = request.form['hora_inicio']
            hora_fin_str = request.form['hora_fin']
            instructor = request.form.get('instructor', 'Minouche')

            # Convertir horas de string a time
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

            # Crear el horario
            horario = HorarioSemanal(
                clase_id=clase_id,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                instructor=instructor
            )

            db.session.add(horario)
            db.session.commit()

            flash('Horario creado exitosamente!', 'success')
            return redirect(url_for('classes.horarios'))

        except Exception as e:
            flash(f'Error al crear el horario: {str(e)}', 'danger')
            db.session.rollback()
            return redirect(url_for('classes.horarios'))

    # Para GET, simplemente redirigir a horarios (el modal está en esa página)
    return redirect(url_for('classes.horarios'))

@class_bp.route('/asistencias')
@login_required
def asistencias():
    # Redirigir a la vista de calendario centralizado
    return redirect(url_for('classes.calendario_unificado'))

@class_bp.route('/clase/<int:evento_id>/asistencia')
@login_required
def gestionar_asistencia(evento_id):
    """Vista para gestionar asistencia de un evento específico"""
    evento = EventoCalendario.query.get_or_404(evento_id)
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre).all()
    # Si es una clase grupal recurrente, buscar el horario
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    return render_template('registrar_asistencia.html', 
                         evento=evento, 
                         alumnos=alumnos,
                         horarios=horarios)

@class_bp.route('/asistencias/registrar', methods=['GET', 'POST'])
@login_required
def registrar_asistencia():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            alumno_id = int(request.form['alumno_id'])
            horario_id = int(request.form['horario_id'])
            fecha_clase = CalendarioAcademico.parsear_fecha(request.form['fecha_clase'], 'iso')
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
            return redirect(url_for('classes.calendario_unificado'))
        except Exception as e:
            flash(f'Error al registrar asistencia: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('classes.calendario_unificado'))
    
    # GET request
    return redirect(url_for('classes.calendario_unificado'))

@class_bp.route('/horarios/<int:horario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_horario(horario_id):
    horario = HorarioSemanal.query.get_or_404(horario_id)
    
    if request.method == 'POST':
        try:
            horario.dia_semana = int(request.form['dia_semana'])
            horario.hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            horario.hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            horario.instructor = request.form['instructor']
            horario.clase_id = int(request.form['clase_id'])
            
            db.session.commit()
            flash('Horario actualizado exitosamente', 'success')
            return redirect(url_for('classes.horarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar horario: {str(e)}', 'error')

    clases = Clase.query.filter_by(activa=True).all()
    return render_template('editar_horario.html', horario=horario, clases=clases)

@class_bp.route('/horarios/<int:horario_id>/eliminar')
@login_required
def eliminar_horario(horario_id):
    """Eliminar horario (desactivar)"""
    horario = HorarioSemanal.query.get_or_404(horario_id)
    horario.activo = False
    db.session.commit()
    flash('Horario desactivado exitosamente', 'success')
    return redirect(url_for('classes.horarios'))

@class_bp.route('/calendario')
@login_required
def calendario_unificado():
    """Calendario unificado editable basado en horarios semanales"""
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    clases = Clase.query.filter_by(activa=True).order_by(Clase.nombre).all()
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    
    return render_template('calendario_unificado_editable.html', 
                         horarios=horarios,
                         clases=clases,
                         alumnos=alumnos)

@class_bp.route('/calendario-viejo')
@login_required
def calendario_unificado_viejo():
    """Calendario unificado con actividades periódicas y citas individuales (versión original)"""
    # Obtener parámetros de fecha
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', datetime.now().month, type=int)
    vista = request.args.get('vista', 'mes')
    
    if vista == 'semana':
        return calendario_semanal(año, mes)
    
    # Obtener sesiones de yogaterapia del mes
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año,
        db.extract('month', SesionYogaterapia.fecha_sesion) == mes
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Calcular datos del calendario
    primer_dia = datetime(año, mes, 1).weekday()
    dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
        dias_mes[1] = 29
    dias_en_mes = dias_mes[mes-1]
    
    # Nombres de meses
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    nombre_mes = nombres_meses[mes-1]
    
    # Generar días del mes para el calendario
    dias_calendario = []
    for dia in range(1, dias_en_mes + 1):
        fecha_actual = datetime(año, mes, dia).date()
        dias_calendario.append(fecha_actual)
    
    # Obtener fecha actual
    today = datetime.now().date()
    
    return render_template('calendario_unificado.html', 
                         año=año, 
                         mes=mes,
                         nombre_mes=nombre_mes,
                         primer_dia=primer_dia,
                         dias_en_mes=dias_en_mes,
                         dias_calendario=dias_calendario,
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios,
                         clases=clases,
                         vista=vista,
                         today=today)

def calendario_semanal(año, mes):
    """Vista semanal del calendario"""
    # Obtener la semana actual
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Obtener sesiones de la semana
    fin_semana = inicio_semana + timedelta(days=6)
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion >= inicio_semana,
        SesionYogaterapia.fecha_sesion <= fin_semana
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Generar días de la semana
    dias_semana = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        dias_semana.append(dia)
    
    return render_template('calendario_semanal.html',
                         dias_semana=dias_semana,
                         sesiones_yogaterapia=sesiones_yogaterapia,
                         horarios=horarios,
                         clases=clases,
                         vista='semana')

@class_bp.route('/calendario/anual')
@login_required
def calendario_anual():
    """Vista de calendario anual para agendar sesiones individuales"""
    año = request.args.get('año', datetime.now().year, type=int)
    
    # Obtener todas las sesiones de yogaterapia del año
    sesiones_yogaterapia = SesionYogaterapia.query.filter(
        db.extract('year', SesionYogaterapia.fecha_sesion) == año
    ).order_by(SesionYogaterapia.fecha_sesion).all()
    
    # Obtener horarios semanales
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    # Obtener clases disponibles
    clases = Clase.query.filter_by(activa=True).all()
    
    # Generar datos para cada mes
    meses_datos = []
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    for mes in range(1, 13):
        # Obtener sesiones del mes
        sesiones_mes = [s for s in sesiones_yogaterapia if s.fecha_sesion.month == mes]
        
        # Calcular datos del mes
        primer_dia = datetime(año, mes, 1).weekday()
        dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
            dias_mes[1] = 29
        dias_en_mes = dias_mes[mes-1]
        
        # Generar días del mes
        dias_calendario = []
        for dia in range(1, dias_en_mes + 1):
            fecha_actual = datetime(año, mes, dia).date()
            dias_calendario.append(fecha_actual)
        
        meses_datos.append({
            'mes': mes,
            'nombre': nombres_meses[mes-1],
            'primer_dia': primer_dia,
            'dias_en_mes': dias_en_mes,
            'dias_calendario': dias_calendario,
            'sesiones': sesiones_mes
        })
    
    # Obtener fecha actual
    today = datetime.now().date()
    
    return render_template('calendario_anual.html',
                         año=año,
                         meses_datos=meses_datos,
                         horarios=horarios,
                         clases=clases,
                         today=today)
@class_bp.route('/api/horarios')
@login_required
def get_horarios_api():
    """API para obtener todos los horarios semanales"""
    horarios = HorarioSemanal.query.filter_by(activo=True).order_by(HorarioSemanal.dia_semana, HorarioSemanal.hora_inicio).all()
    return jsonify([{
        'id': h.id,
        'clase_id': h.clase_id,
        'clase_nombre': h.clase.nombre,
        'dia_semana': h.dia_semana,
        'hora_inicio': h.hora_inicio.strftime('%H:%M'),
        'hora_fin': h.hora_fin.strftime('%H:%M'),
        'instructor': h.instructor,
        'activo': h.activo
    } for h in horarios])

@class_bp.route('/api/calendario/eventos')
@login_required
def get_eventos_calendario():
    """Obtiene todos los eventos para el calendario (horarios recurrentes + eventos individuales + asistencias)"""
    eventos = []

    # Obtener rango de fechas del request
    start = request.args.get('start')
    end = request.args.get('end')

    if start and end:
        import re
        start_clean = re.split(r'[\s+Z]', start)[0]
        end_clean = re.split(r'[\s+Z]', end)[0]

        start_date = datetime.fromisoformat(start_clean)
        end_date = datetime.fromisoformat(end_clean)
    else:
        # Default: próximas 2 semanas
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() + timedelta(days=14)

    # 1. Generar eventos desde horarios recurrentes
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    current_date = start_date.date()

    while current_date <= end_date.date():
        dia_semana = current_date.weekday()

        for horario in horarios:
            if horario.dia_semana == dia_semana:
                # Crear evento para este día
                fecha_inicio = datetime.combine(current_date, horario.hora_inicio)
                fecha_fin = datetime.combine(current_date, horario.hora_fin)

                # Contar asistencias para esta clase
                asistencias_clase = Asistencia.query.filter_by(
                    horario_id=horario.id,
                    fecha_clase=current_date
                ).all()

                total_asistencias = len(asistencias_clase)
                presentes = sum(1 for a in asistencias_clase if a.presente)

                # Obtener nombres de alumnos presentes y ausentes
                alumnos_presentes = []
                alumnos_ausentes = []
                for asistencia in asistencias_clase:
                    nombre_completo = f"{asistencia.alumno.nombre} {asistencia.alumno.apellido}"
                    if asistencia.presente:
                        alumnos_presentes.append(nombre_completo)
                    else:
                        alumnos_ausentes.append(nombre_completo)

                # Construir título con información de asistencia
                titulo = horario.clase.nombre
                if total_asistencias > 0:
                    titulo += f" ({presentes}/{total_asistencias})"

                eventos.append({
                    'id': f'h_{horario.id}_{current_date.isoformat()}',
                    'title': titulo,
                    'start': fecha_inicio.isoformat(),
                    'end': fecha_fin.isoformat(),
                    'className': horario.clase.nombre,
                    'color': horario.clase.color or '#4ECDC4',
                    'instructor': horario.instructor,
                    'tipo': 'recurrente',
                    'horario_id': horario.id,
                    'total_asistencias': total_asistencias,
                    'presentes': presentes,
                    'alumnos_presentes': alumnos_presentes,
                    'alumnos_ausentes': alumnos_ausentes,
                    'fecha': current_date.isoformat(),
                    'editable': False
                })

        current_date += timedelta(days=1)

    # 2. Añadir eventos individuales
    eventos_individuales = EventoCalendario.query.filter(
        EventoCalendario.activo == True,
        EventoCalendario.fecha_inicio >= start_date,
        EventoCalendario.fecha_inicio <= end_date
    ).all()

    for evento in eventos_individuales:
        eventos.append({
            'id': f'e_{evento.id}',
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat(),
            'description': evento.descripcion,
            'className': evento.clase.nombre if evento.clase else 'Individual',
            'alumno': f"{evento.alumno.nombre} {evento.alumno.apellido}" if evento.alumno else None,
            'tipo': evento.tipo,
            'color': evento.color,
            'instructor': evento.instructor,
            'evento_id': evento.id,
            'editable': True
        })

    return jsonify(eventos)

@class_bp.route('/api/calendario/eventos/<int:evento_id>')
@login_required
def get_evento_calendario(evento_id):
    """Obtiene detalles de un evento individual"""
    evento = EventoCalendario.query.get_or_404(evento_id)

    return jsonify({
        'id': evento.id,
        'titulo': evento.titulo,
        'descripcion': evento.descripcion,
        'clase_id': evento.clase_id,
        'alumno_id': evento.alumno_id,
        'fecha_inicio': evento.fecha_inicio.isoformat(),
        'fecha_fin': evento.fecha_fin.isoformat(),
        'tipo': evento.tipo,
        'color': evento.color,
        'instructor': evento.instructor
    })

@class_bp.route('/api/calendario/eventos', methods=['POST'])
@login_required
def crear_evento_calendario():
    """Crea un nuevo evento individual"""
    try:
        data = request.get_json()

        # Generar título automático si no se proporciona
        titulo = data.get('titulo')
        if not titulo:
            if data.get('alumno_id'):
                alumno = Alumno.query.get(data['alumno_id'])
                titulo = f"Clase Individual - {alumno.nombre} {alumno.apellido}"
            else:
                titulo = "Evento Especial"

        evento = EventoCalendario(
            titulo=titulo,
            descripcion=data.get('descripcion'),
            clase_id=data.get('clase_id') if data.get('clase_id') else None,
            alumno_id=data.get('alumno_id') if data.get('alumno_id') else None,
            fecha_inicio=datetime.fromisoformat(data['fecha_inicio']),
            fecha_fin=datetime.fromisoformat(data['fecha_fin']),
            tipo=data.get('tipo', 'individual'),
            color=data.get('color', '#8B5FBF'),
            instructor=data.get('instructor', 'Minouche')
        )

        db.session.add(evento)
        db.session.commit()

        return jsonify({'success': True, 'id': evento.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@class_bp.route('/api/calendario/eventos/<int:evento_id>', methods=['PUT', 'POST'])
@login_required
def actualizar_evento_calendario(evento_id):
    """Actualiza un evento individual"""
    try:
        evento = EventoCalendario.query.get_or_404(evento_id)
        data = request.get_json()

        if 'titulo' in data:
            evento.titulo = data['titulo']
        if 'descripcion' in data:
            evento.descripcion = data['descripcion']
        if 'clase_id' in data:
            evento.clase_id = data['clase_id'] if data['clase_id'] else None
        if 'alumno_id' in data:
            evento.alumno_id = data['alumno_id'] if data['alumno_id'] else None
        if 'fecha_inicio' in data:
            evento.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        if 'fecha_fin' in data:
            evento.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
        if 'tipo' in data:
            evento.tipo = data['tipo']
        if 'color' in data:
            evento.color = data['color']
        if 'instructor' in data:
            evento.instructor = data['instructor']

        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@class_bp.route('/api/calendario/eventos/<int:evento_id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar_evento_calendario(evento_id):
    """Elimina un evento individual"""
    try:
        evento = EventoCalendario.query.get_or_404(evento_id)
        evento.activo = False  # Soft delete
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
@class_bp.route('/api/eventos-disponibles')
@login_required
def api_eventos_disponibles():
    """API para obtener eventos disponibles para un alumno"""
    try:
        alumno_id = request.args.get('alumno_id', type=int)
        fecha_inicio = request.args.get('inicio')
        fecha_fin = request.args.get('fin')
        
        if not all([alumno_id, fecha_inicio, fecha_fin]):
            return jsonify({'success': False, 'message': 'Parámetros incompletos'}), 400
        
        # Convertir fechas
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Obtener eventos específicos
        eventos_query = EventoCalendario.query.filter(
            EventoCalendario.fecha_inicio >= datetime.combine(inicio, datetime.min.time()),
            EventoCalendario.fecha_inicio <= datetime.combine(fin, datetime.max.time()),
            EventoCalendario.activo == True
        ).all()
        
        eventos_disponibles = []
        for evento in eventos_query:
            # Contar asistencias
            asistencias_count = Asistencia.query.filter_by(
                evento_id=evento.id
            ).count()
            
            # Verificar si el alumno ya está inscrito
            ya_inscrito = Asistencia.query.filter_by(
                evento_id=evento.id,
                alumno_id=alumno_id
            ).first() is not None
            
            if not ya_inscrito:
                capacidad_maxima = 15 # Default
                if evento.clase:
                    capacidad_maxima = evento.clase.capacidad_maxima
                
                if asistencias_count < capacidad_maxima:
                    eventos_disponibles.append({
                        'id': evento.id,
                        'titulo': evento.titulo,
                        'fecha': evento.fecha_inicio.date().isoformat(),
                        'hora_inicio': evento.fecha_inicio.strftime('%H:%M'),
                        'hora_fin': evento.fecha_fin.strftime('%H:%M'),
                        'instructor': evento.instructor,
                        'capacidad_maxima': capacidad_maxima,
                        'asistencias': asistencias_count,
                        'color': evento.color,
                        'tipo': 'evento'
                    })

        # También incluir eventos basados en horarios semanales
        horarios = HorarioSemanal.query.filter_by(activo=True).all()
        current_date = inicio
        while current_date <= fin:
            dia_semana = current_date.weekday()
            for h in horarios:
                if h.dia_semana == dia_semana:
                    # Verificar si ya está inscrito
                    ya_inscrito = Asistencia.query.filter_by(
                        horario_id=h.id,
                        fecha_clase=current_date,
                        alumno_id=alumno_id
                    ).first() is not None
                    
                    if not ya_inscrito:
                        # Contar asistencias totales
                        asistencias_total = Asistencia.query.filter_by(
                            horario_id=h.id,
                            fecha_clase=current_date
                        ).count()
                        
                        if asistencias_total < h.capacidad_maxima:
                            eventos_disponibles.append({
                                'id': f"h-{h.id}",
                                'horario_id': h.id,
                                'titulo': h.clase.nombre,
                                'fecha': current_date.isoformat(),
                                'hora_inicio': h.hora_inicio.strftime('%H:%M'),
                                'hora_fin': h.hora_fin.strftime('%H:%M'),
                                'instructor': h.instructor,
                                'capacidad_maxima': h.capacidad_maxima,
                                'asistencias': asistencias_total,
                                'color': h.clase.color,
                                'tipo': 'horario'
                            })
            current_date += timedelta(days=1)

        return jsonify({
            'success': True,
            'eventos': eventos_disponibles
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/evento/agregar-alumno', methods=['POST'])
@login_required
def agregar_alumno_evento_api():
    """API para registrar asistencia/inscripción de un alumno en un evento o clase"""
    try:
        data = request.get_json()
        alumno_id = data.get('alumno_id')
        fecha = data.get('fecha')
        
        # Puede venir de un evento específico o de un horario semanal
        evento_id = data.get('evento_id')
        horario_id = data.get('horario_id')
        
        if not all([alumno_id, fecha]) or (not evento_id and not horario_id):
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
            
        # Convertir fecha
        fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Verificar si ya existe
        asistencia = Asistencia.query.filter_by(
            alumno_id=alumno_id,
            fecha_clase=fecha_date,
            evento_id=evento_id,
            horario_id=horario_id
        ).first()
        
        if not asistencia:
            asistencia = Asistencia(
                alumno_id=alumno_id,
                fecha_clase=fecha_date,
                evento_id=evento_id,
                horario_id=horario_id,
                presente=True # Por defecto al inscribirse desde esta vista se marca como presente/confirmado
            )
            db.session.add(asistencia)
            db.session.commit()
            
        return jsonify({'success': True, 'message': 'Inscripción realizada con éxito'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
@class_bp.route('/calendario_seleccion_citas')
@class_bp.route('/calendario_seleccion_citas/<int:alumno_id>')
@login_required
def calendario_seleccion_citas(alumno_id=None):
    """Mostrar calendario interactivo para seleccionar fecha y hora de cita"""
    alumno = None
    if alumno_id:
        alumno = Alumno.query.get_or_404(alumno_id)
    
    # Calcular fechas para el calendario
    hoy = date.today()
    mes_actual = hoy.strftime('%B')
    año_actual = hoy.year
    
    # Calcular inicio de semana (lunes)
    lunes = hoy - timedelta(days=(hoy.weekday()))
    fecha_inicio_semana = lunes
    
    return render_template('calendario_seleccion_citas.html', 
                         alumno=alumno,
                         mes_actual=mes_actual,
                         año_actual=año_actual,
                         fecha_inicio_semana=fecha_inicio_semana)

@class_bp.route('/api/asistencias/clase/<int:horario_id>/<string:fecha>')
@login_required
def api_asistencias_clase(horario_id, fecha):
    """API para obtener la lista de asistencia de una clase en una fecha específica"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # 1. Alumnos en el roster permanente
        alumnos_roster = Alumno.query.join(
            'horarios' # Asumiendo relación 'horarios' en Alumno o similar
        ).filter(HorarioSemanal.id == horario_id).all()
        
        # Si la relación no existe o falla, buscar por la tabla intermedia (si existe)
        # En models.py: class HorarioSemanal: alumnos = db.relationship('Alumno', secondary='alumno_horario')
        
        alumnos_data = []
        for alumno in alumnos_roster:
            # Buscar si ya tiene registro de asistencia para este día
            asistencia = Asistencia.query.filter_by(
                alumno_id=alumno.id,
                horario_id=horario_id,
                fecha_clase=fecha_date
            ).first()
            
            alumnos_data.append({
                'id': alumno.id,
                'nombre': f"{alumno.nombre} {alumno.apellido}",
                'asistio': asistencia.presente if asistencia else None,
                'observaciones': asistencia.observaciones if asistencia else '',
                'inscrito': True
            })
            
        # 2. Alumnos extra (asistieron pero no están en el roster)
        asistencias_extra = Asistencia.query.filter_by(
            horario_id=horario_id,
            fecha_clase=fecha_date
        ).filter(~Asistencia.alumno_id.in_([a.id for a in alumnos_roster])).all()
        
        for asist in asistencias_extra:
            alumnos_data.append({
                'id': asist.alumno.id,
                'nombre': f"{asist.alumno.nombre} {asist.alumno.apellido}",
                'asistio': asist.presente,
                'observaciones': asist.observaciones,
                'inscrito': False
            })
            
        return jsonify({
            'success': True,
            'clase': horario.clase.nombre,
            'fecha': fecha,
            'alumnos': alumnos_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/asistencias/registrar-lote', methods=['POST'])
@login_required
def api_registrar_asistencias_lote():
    """API para registrar múltiples asistencias a la vez"""
    try:
        data = request.get_json()
        horario_id = data.get('horario_id')
        fecha = data.get('fecha')
        registros = data.get('registro', [])
        
        fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        for reg in registros:
            alumno_id = reg.get('alumno_id')
            asistio = reg.get('asistio')
            observaciones = reg.get('observaciones', '')
            
            if asistio is None: continue # No se marcó nada
            
            asistencia = Asistencia.query.filter_by(
                alumno_id=alumno_id,
                horario_id=horario_id,
                fecha_clase=fecha_date
            ).first()
            
            if asistencia:
                asistencia.presente = asistio
                asistencia.observaciones = observaciones
            else:
                asistencia = Asistencia(
                    alumno_id=alumno_id,
                    horario_id=horario_id,
                    fecha_clase=fecha_date,
                    presente=asistio,
                    observaciones=observaciones
                )
                db.session.add(asistencia)
                
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/<int:horario_id>')
@login_required
def api_get_horario(horario_id):
    """API para obtener detalles de un horario semanal"""
    try:
        h = HorarioSemanal.query.get_or_404(horario_id)
        return jsonify({
            'success': True,
            'horario': {
                'id': h.id,
                'clase_id': h.clase_id,
                'dia_semana': h.dia_semana,
                'hora_inicio': h.hora_inicio.strftime('%H:%M'),
                'hora_fin': h.hora_fin.strftime('%H:%M'),
                'instructor': h.instructor,
                'capacidad_maxima': h.capacidad_maxima,
                'observaciones': h.observaciones
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/crear', methods=['POST'])
@login_required
def api_crear_horario():
    """API para crear un nuevo horario semanal"""
    try:
        data = request.get_json()
        horario = HorarioSemanal(
            clase_id=data['clase_id'],
            dia_semana=int(data['dias_semana'].split(',')[0]), # Simplificación: toma el primer día
            hora_inicio=datetime.strptime(data['hora_inicio'], '%H:%M').time(),
            hora_fin=datetime.strptime(data['hora_fin'], '%H:%M').time(),
            instructor=data.get('instructor', 'Minouche'),
            capacidad_maxima=int(data.get('capacidad_maxima', 15)),
            observaciones=data.get('observaciones', '')
        )
        db.session.add(horario)
        db.session.commit()
        return jsonify({'success': True, 'id': horario.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/actualizar', methods=['POST'])
@login_required
def api_actualizar_horario():
    """API para actualizar un horario semanal"""
    try:
        data = request.get_json()
        horario = HorarioSemanal.query.get_or_404(data['horario_id'])
        
        horario.clase_id = data['clase_id']
        horario.dia_semana = int(data['dias_semana'].split(',')[0])
        horario.hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        horario.hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        horario.instructor = data.get('instructor', 'Minouche')
        horario.capacidad_maxima = int(data.get('capacidad_maxima', 15))
        horario.observaciones = data.get('observaciones', '')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/<int:horario_id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def api_eliminar_horario(horario_id):
    """API para eliminar un horario semanal"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        horario.activo = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/<int:horario_id>/alumnos')
@login_required
def api_get_roster_horario(horario_id):
    """API para obtener el roster de alumnos de un horario"""
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        # Asumiendo relación alumnos en HorarioSemanal
        return jsonify({
            'success': True,
            'alumnos': [{
                'id': a.id,
                'nombre': a.nombre,
                'apellido': a.apellido
            } for a in horario.alumnos]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/agregar-alumno', methods=['POST'])
@login_required
def api_agregar_alumno_roster():
    """API para añadir un alumno al roster permanente de un horario"""
    try:
        data = request.get_json()
        horario = HorarioSemanal.query.get_or_404(data['horario_id'])
        alumno = Alumno.query.get_or_404(data['alumno_id'])
        
        if alumno not in horario.alumnos:
            horario.alumnos.append(alumno)
            db.session.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/horario/quitar-alumno', methods=['POST'])
@login_required
def api_quitar_alumno_roster():
    """API para quitar un alumno del roster permanente de un horario"""
    try:
        data = request.get_json()
        horario = HorarioSemanal.query.get_or_404(data['horario_id'])
        alumno = Alumno.query.get_or_404(data['alumno_id'])
        
        if alumno in horario.alumnos:
            horario.alumnos.remove(alumno)
            db.session.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@class_bp.route('/api/clases')
@login_required
def api_get_clases():
    """API para obtener lista de tipos de clases"""
    try:
        clases = Clase.query.filter_by(activa=True).all()
        return jsonify({
            'success': True,
            'clases': [{
                'id': c.id,
                'nombre': c.nombre,
                'precio': c.precio,
                'color': c.color
            } for c in clases]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
