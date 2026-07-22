from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
import io
import pandas as pd
from datetime import datetime, date, timedelta
from models import db, Alumno, Pago, Asistencia, Bono, Configuracion
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
            # Verificar si ya existe un alumno con ese DNI o Email para dar un mensaje más claro
            dni = request.form.get('dni')
            email = request.form.get('email')
            
            if dni and Alumno.query.filter_by(dni=dni).first():
                flash(f'Ya existe un alumno con el DNI {dni}.', 'error')
                return render_template('nuevo_alumno.html')
            
            if email and Alumno.query.filter_by(email=email).first():
                flash(f'Ya existe un alumno con el email {email}.', 'error')
                return render_template('nuevo_alumno.html')

            matricula_pagada = 'matricula_pagada' in request.form
            fecha_matricula = date.today() if matricula_pagada else None
            
            # Formatear fecha de nacimiento si viene
            fecha_nac_str = request.form.get('fecha_nacimiento')
            fecha_nacimiento = None
            if fecha_nac_str:
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                except ValueError:
                    pass # O manejar error si el formato es inválido

            alumno = Alumno(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=dni,
                email=email,
                telefono=request.form.get('telefono'),
                fecha_nacimiento=fecha_nacimiento,
                direccion=request.form.get('direccion'),
                condiciones_medicas=request.form.get('condiciones_medicas'),
                tipo_cuota=request.form.get('tipo_cuota', '1_clase_semanal'),
                matricula_pagada=matricula_pagada,
                fecha_matricula=fecha_matricula
            )
            db.session.add(alumno)
            db.session.commit()

            flash('¡Alumno registrado!', 'success')
            return redirect(url_for('students.alumnos'))
        except Exception as e:
            flash(f'Error al registrar alumno: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('nuevo_alumno.html')

@student_bp.route('/alumnos/<int:alumno_id>')
@login_required
def ver_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    datos = _datos_ficha(alumno)

    return render_template('ver_alumno.html',
                         alumno=alumno,
                         **datos)


def _datos_ficha(alumno):
    """Datos calculados de la ficha del alumno (compartidos por la vista y el PDF)."""
    pagos = Pago.query.filter_by(alumno_id=alumno.id).order_by(Pago.mes.desc()).all()

    # Obtener asistencias del alumno (últimos 90 días)
    fecha_inicio = date.today() - timedelta(days=90)
    asistencias = Asistencia.query.filter(
        Asistencia.alumno_id == alumno.id,
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

    # Morosidad: periodos de cuota pendientes del año en curso (solo alumnos activos)
    from utils.finance_utils import periodos_pendientes
    pendientes = periodos_pendientes(alumno) if alumno.activo else []
    deuda = alumno.get_precio_cuota() * len(pendientes)

    # Bonos del alumno (más recientes primero)
    bonos = Bono.query.filter_by(alumno_id=alumno.id).order_by(Bono.fecha_compra.desc()).all()

    return {
        'pagos': pagos,
        'bonos': bonos,
        'asistencias': asistencias,
        'total_asistencias': total_asistencias,
        'asistencias_presente': asistencias_presente,
        'asistencias_ausente': asistencias_ausente,
        'porcentaje_asistencia': porcentaje_asistencia,
        'asistencias_por_mes': asistencias_por_mes,
        'pendientes': pendientes,
        'deuda': deuda,
    }


@student_bp.route('/alumnos/<int:alumno_id>/pdf')
@login_required
def descargar_ficha_pdf(alumno_id):
    """Generar y descargar PDF con la ficha completa del alumno"""
    try:
        alumno = Alumno.query.get_or_404(alumno_id)
        datos = _datos_ficha(alumno)

        config_nombre = Configuracion.query.filter_by(clave='nombre_escuela').first()
        datos['nombre_escuela'] = config_nombre.valor if config_nombre else 'DarmaSala'

        from utils.pdf_generator import generar_pdf_ficha_alumno
        pdf_buffer = generar_pdf_ficha_alumno(alumno, datos)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Ficha_{alumno.nombre}_{alumno.apellido}.pdf'
        )
    except Exception as e:
        flash(f'Error al generar PDF: {str(e)}', 'error')
        return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))

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
            nuevo_activo = 'activo' in request.form
            if not nuevo_activo and alumno.fecha_baja is None:
                alumno.fecha_baja = date.today()
            elif nuevo_activo:
                alumno.fecha_baja = None
            alumno.activo = nuevo_activo

            db.session.commit()

            flash('¡Alumno actualizado!', 'success')
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
        alumno.fecha_baja = date.today()
        db.session.commit()
        flash('¡Alumno desactivado!', 'success')
        return redirect(url_for('students.alumnos'))
    else:
        if request.args.get('confirm') == '1':
            alumno.activo = False
            alumno.fecha_baja = date.today()
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
        alumno.fecha_baja = None
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alumno reactivado'})
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
@student_bp.route('/alumnos/exportar')
@login_required
def exportar_alumnos_excel():
    """Exporta la lista de alumnos a un archivo Excel"""
    try:
        alumnos_list = Alumno.query.all()
        
        # Preparar datos para el DataFrame
        data = []
        for a in alumnos_list:
            data.append({
                'ID': a.id,
                'Nombre': a.nombre,
                'Apellido': a.apellido,
                'DNI/NIE': a.dni,
                'Email': a.email,
                'Teléfono': a.telefono,
                'Fecha Nacimiento': a.fecha_nacimiento.strftime('%d/%m/%Y') if a.fecha_nacimiento else '',
                'Dirección': a.direccion,
                'Condiciones Médicas': a.condiciones_medicas,
                'Cuota': a.get_tipo_cuota_display(),
                'Precio Cuota (€)': a.get_precio_cuota(),
                'Matrícula Pagada': 'Sí' if a.matricula_pagada else 'No',
                'Fecha Matrícula': a.fecha_matricula.strftime('%d/%m/%Y') if a.fecha_matricula else '',
                'Estado': 'Activo' if a.activo else 'Inactivo',
                'Fecha Registro': a.fecha_registro.strftime('%d/%m/%Y %H:%M')
            })
        
        df = pd.DataFrame(data)
        
        # Crear un buffer en memoria para el archivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Alumnos')
            
            # Ajustar el ancho de las columnas (opcional pero profesional)
            worksheet = writer.sheets['Alumnos']
            for i, col in enumerate(df.columns):
                # Asegurar que convertimos a string y manejamos posibles valores nulos
                max_len = df[col].astype(str).apply(len).max()
                column_len = max(max_len, len(col)) + 2
                worksheet.column_dimensions[chr(65 + i)].width = column_len
                
        output.seek(0)
        
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-disposition": f"attachment; filename=Alumnos_DarmaSala_{datetime.now().strftime('%Y%m%d')}.xlsx"}
        )
    except Exception as e:
        flash(f'Error al exportar Excel: {str(e)}', 'error')
        return redirect(url_for('students.alumnos'))
