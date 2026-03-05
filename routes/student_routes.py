from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from models import db, Alumno, Pago, Asistencia
from utils.auth_utils import login_required

student_bp = Blueprint('students', __name__)

@student_bp.route('/alumnos')
@login_required
def alumnos():
    # Mostrar solo alumnos activos
    alumnos_activos = Alumno.query.filter_by(activo=True).all()
    return render_template('alumnos.html', alumnos=alumnos_activos)

@student_bp.route('/alumnos/desactivados')
@login_required
def alumnos_desactivados():
    # Mostrar solo alumnos desactivados
    alumnos_inactivos = Alumno.query.filter_by(activo=False).all()
    current_year = date.today().year
    return render_template('alumnos_desactivados.html', 
                         alumnos=alumnos_inactivos,
                         current_year=current_year)

@student_bp.route('/alumnos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_alumno():
    if request.method == 'POST':
        try:
            matricula_pagada = 'matricula_pagada' in request.form
            fecha_matricula = date.today() if matricula_pagada else None
            
            alumno = Alumno(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form.get('dni'),
                email=request.form['email'],
                telefono=request.form.get('telefono'),
                fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None,
                direccion=request.form.get('direccion'),
                condiciones_medicas=request.form.get('condiciones_medicas'),
                tipo_cuota=request.form.get('tipo_cuota', '1_clase_semanal'),
                matricula_pagada=matricula_pagada,
                fecha_matricula=fecha_matricula
            )
            db.session.add(alumno)
            db.session.commit()
            flash('¡Alumno registrado exitosamente!', 'success')
            return redirect(url_for('students.alumnos'))
        except Exception as e:
            flash(f'Error al registrar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('nuevo_alumno.html')

@student_bp.route('/alumnos/<int:alumno_id>')
@login_required
def ver_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    pagos = Pago.query.filter_by(alumno_id=alumno_id).order_by(Pago.mes.desc()).all()

    # Obtener asistencias del alumno (últimos 90 días)
    fecha_inicio = date.today() - timedelta(days=90)
    asistencias = Asistencia.query.filter(
        Asistencia.alumno_id == alumno_id,
        Asistencia.fecha_clase >= fecha_inicio
    ).order_by(Asistencia.fecha_clase.desc()).all()

    # Calcular estadísticas de asistencia
    total_asistencias = len(asistencias)
    asistencias_presente = sum(1 for a in asistencias if a.presente)
    asistencias_ausente = total_asistencias - asistencias_presente
    porcentaje_asistencia = (asistencias_presente / total_asistencias * 100) if total_asistencias > 0 else 0

    # Asistencias por mes (últimos 3 meses)
    asistencias_por_mes = {}
    for asistencia in asistencias:
        mes_key = asistencia.fecha_clase.strftime('%Y-%m')
        if mes_key not in asistencias_por_mes:
            asistencias_por_mes[mes_key] = {'total': 0, 'presente': 0}
        asistencias_por_mes[mes_key]['total'] += 1
        if asistencia.presente:
            asistencias_por_mes[mes_key]['presente'] += 1

    return render_template('ver_alumno.html',
                         alumno=alumno,
                         pagos=pagos,
                         asistencias=asistencias,
                         total_asistencias=total_asistencias,
                         asistencias_presente=asistencias_presente,
                         asistencias_ausente=asistencias_ausente,
                         porcentaje_asistencia=porcentaje_asistencia,
                         asistencias_por_mes=asistencias_por_mes)

@student_bp.route('/alumnos/<int:alumno_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
            alumno.dni = request.form.get('dni')
            alumno.email = request.form['email']
            alumno.telefono = request.form.get('telefono')
            alumno.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None
            alumno.direccion = request.form.get('direccion')
            alumno.condiciones_medicas = request.form.get('condiciones_medicas')
            alumno.tipo_cuota = request.form.get('tipo_cuota', '1_clase_semanal')
            
            db.session.commit()
            flash('¡Alumno actualizado exitosamente!', 'success')
            return redirect(url_for('students.ver_alumno', alumno_id=alumno.id))
        except Exception as e:
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_alumno.html', alumno=alumno)

@student_bp.route('/alumnos/<int:alumno_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if request.method == 'POST':
        alumno.activo = False
        db.session.commit()
        flash('¡Alumno desactivado exitosamente!', 'success')
        return redirect(url_for('students.alumnos'))
    else:
        if request.args.get('confirm') == '1':
            alumno.activo = False
            db.session.commit()
            flash('¡Alumno desactivado exitosamente!', 'success')
            return redirect(url_for('students.alumnos'))
        else:
            flash('Confirma la desactivación del alumno.', 'warning')
            return redirect(url_for('students.alumnos'))


@student_bp.route('/alumnos/<int:alumno_id>/reactivar', methods=['POST'])
@login_required
def reactivar_alumno(alumno_id):
    try:
        alumno = Alumno.query.get_or_404(alumno_id)
        alumno.activo = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alumno reactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@student_bp.route('/api/alumno/<int:alumno_id>/asistencias')
@login_required
def get_asistencias_alumno_api(alumno_id):
    """API para obtener el historial de asistencias de un alumno con estadísticas"""
    try:
        # Obtener asistencias del alumno (últimos 12 meses)
        fecha_inicio = date.today() - timedelta(days=365)
        asistencias = Asistencia.query.filter(
            Asistencia.alumno_id == alumno_id,
            Asistencia.fecha_clase >= fecha_inicio
        ).order_by(Asistencia.fecha_clase.desc()).all()

        # Calcular estadísticas
        presentes = sum(1 for a in asistencias if a.presente)
        ausentes = sum(1 for a in asistencias if not a.presente)
        total = len(asistencias)
        porcentaje = round((presentes / total * 100), 1) if total > 0 else 0

        return jsonify({
            'success': True,
            'asistencias': [asistencia.to_dict() for asistencia in asistencias],
            'estadisticas': {
                'presentes': presentes,
                'ausentes': ausentes,
                'pendientes': 0,
                'total': total,
                'porcentaje_asistencia': porcentaje
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
@student_bp.route('/api/alumnos-disponibles')
@login_required
def api_alumnos_disponibles():
    """API para obtener lista de alumnos activos"""
    try:
        alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
        return jsonify({
            'success': True,
            'alumnos': [{
                'id': a.id,
                'nombre': a.nombre,
                'apellido': a.apellido
            } for a in alumnos]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
