from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import os
from models import db, Alumno, SesionYogaterapia, ArchivoYogaterapia, Pago, HorarioSemanal
from utils.auth_utils import login_required
from utils.app_utils import verificar_conflicto_horario

yogatherapia_bp = Blueprint('yogatherapia', __name__)

@yogatherapia_bp.route('/yogaterapia')
@login_required
def yogaterapia():
    """Página principal de yogaterapia (sesiones de yogaterapia)"""
    sesiones = SesionYogaterapia.query.order_by(SesionYogaterapia.fecha_sesion.desc()).all()
    return render_template('yogaterapia.html', sesiones=sesiones)

@yogatherapia_bp.route('/yogaterapia/nueva')
@login_required
def nueva_yogaterapia():
    """Formulario para nueva sesión de yogaterapia"""
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    return render_template('nueva_yogaterapia.html', alumnos=alumnos)

@yogatherapia_bp.route('/yogaterapia/procesar', methods=['POST'])
@login_required
def procesar_yogaterapia_general():
    """Procesar nueva sesión de yogaterapia general"""
    try:
        alumno_id = request.form['alumno_id']
        alumno = Alumno.query.get_or_404(alumno_id)
        
        # Procesar horas
        hora_inicio = None
        hora_fin = None
        if request.form.get('hora_inicio'):
            hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
        if request.form.get('hora_fin'):
            hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
        
        # Verificar conflicto de horarios
        fecha_sesion = datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date()
        if hora_inicio and hora_fin:
            conflicto, info_conflicto = verificar_conflicto_horario(fecha_sesion, hora_inicio, hora_fin)
            if conflicto:
                flash(f'⚠️ {info_conflicto["mensaje"]}', 'warning')
                return redirect(url_for('yogatherapia.nueva_yogaterapia'))
        
        sesion = SesionYogaterapia(
            alumno_id=alumno_id,
            fecha_sesion=fecha_sesion,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_minutos=int(request.form.get('duracion_minutos', 60)),
            tipo_sesion=request.form.get('tipo_sesion', 'individual'),
            motivo_consulta=request.form.get('motivo_consulta'),
            objetivos_terapeuticos=request.form.get('objetivos_terapeuticos'),
            tecnicas_aplicadas=request.form.get('tecnicas_aplicadas'),
            posturas_trabajadas=request.form.get('posturas_trabajadas'),
            respiracion_pranayama=request.form.get('respiracion_pranayama'),
            meditacion_relajacion=request.form.get('meditacion_relajacion'),
            estado_inicial=request.form.get('estado_inicial'),
            respuesta_sesion=request.form.get('respuesta_sesion'),
            estado_final=request.form.get('estado_final'),
            observaciones_terapeuta=request.form.get('observaciones_terapeuta'),
            recomendaciones_casa=request.form.get('recomendaciones_casa'),
            proxima_sesion=request.form.get('proxima_sesion'),
            instructor=request.form.get('instructor', 'Minouche'),
            precio=float(request.form.get('precio', 50.00)),
            pagado='pagado' in request.form,
            metodo_pago=request.form.get('metodo_pago')
        )
        
        db.session.add(sesion)
        db.session.flush()
        
        # Manejar archivos subidos
        archivos = request.files.getlist('archivos')
        for archivo in archivos:
            if archivo and archivo.filename:
                # Crear directorio para archivos de yogaterapia
                upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{archivo.filename}"
                filepath = os.path.join(upload_dir, filename)
                
                # Guardar archivo
                archivo.save(filepath)
                
                # Crear registro en base de datos
                archivo_db = ArchivoYogaterapia(
                    sesion_yogaterapia_id=sesion.id,
                    nombre_archivo=archivo.filename,
                    ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                    tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                    tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                )
                db.session.add(archivo_db)
        
        # Si está pagado, crear registro de pago
        if sesion.pagado:
            pago = Pago(
                alumno_id=alumno_id,
                fecha_clase=sesion.fecha_sesion,
                monto=sesion.precio,
                tipo_pago='yogaterapia',
                descripcion=f'Yogaterapia - {sesion.tipo_sesion}',
                metodo_pago=sesion.metodo_pago
            )
            db.session.add(pago)
        
        db.session.commit()
        flash(f'¡Sesión de yogaterapia registrada exitosamente para {alumno.nombre} {alumno.apellido}!', 'success')
        return redirect(url_for('yogatherapia.yogaterapia'))
        
    except Exception as e:
        flash(f'Error al registrar sesión: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('yogatherapia.nueva_yogaterapia'))

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>')
@login_required
def ver_sesion_yogaterapia(sesion_id):
    """Ver detalles de una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    archivos = ArchivoYogaterapia.query.filter_by(sesion_yogaterapia_id=sesion_id).all()
    return render_template('ver_sesion_yogaterapia.html', sesion=sesion, archivos=archivos)

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_sesion_yogaterapia(sesion_id):
    """Editar una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos de la sesión
            fecha_sesion_nueva = datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date()
            sesion.fecha_sesion = fecha_sesion_nueva
            
            # Procesar horas
            hora_inicio_nueva = None
            hora_fin_nueva = None
            if request.form.get('hora_inicio'):
                hora_inicio_nueva = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            if request.form.get('hora_fin'):
                hora_fin_nueva = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            
            # Verificar conflicto de horarios
            if hora_inicio_nueva and hora_fin_nueva:
                conflicto, info_conflicto = verificar_conflicto_horario(fecha_sesion_nueva, hora_inicio_nueva, hora_fin_nueva, sesion_id)
                if conflicto:
                    flash(f'⚠️ {info_conflicto["mensaje"]}', 'warning')
                    return redirect(url_for('yogatherapia.editar_sesion_yogaterapia', sesion_id=sesion_id))
            
            sesion.hora_inicio = hora_inicio_nueva
            sesion.hora_fin = hora_fin_nueva
            
            sesion.duracion_minutos = int(request.form.get('duracion_minutos', 75))
            sesion.tipo_sesion = request.form.get('tipo_sesion', 'individual')
            sesion.motivo_consulta = request.form.get('motivo_consulta')
            sesion.objetivos_terapeuticos = request.form.get('objetivos_terapeuticos')
            sesion.tecnicas_aplicadas = request.form.get('tecnicas_aplicadas')
            sesion.posturas_trabajadas = request.form.get('posturas_trabajadas')
            sesion.respiracion_pranayama = request.form.get('respiracion_pranayama')
            sesion.meditacion_relajacion = request.form.get('meditacion_relajacion')
            sesion.estado_inicial = request.form.get('estado_inicial')
            sesion.respuesta_sesion = request.form.get('respuesta_sesion')
            sesion.estado_final = request.form.get('estado_final')
            sesion.observaciones_terapeuta = request.form.get('observaciones_terapeuta')
            sesion.recomendaciones_casa = request.form.get('recomendaciones_casa')
            sesion.proxima_sesion = request.form.get('proxima_sesion')
            sesion.instructor = request.form.get('instructor', 'Minouche')
            sesion.precio = float(request.form.get('precio', 50.00))
            sesion.pagado = 'pagado' in request.form
            sesion.metodo_pago = request.form.get('metodo_pago')
            
            # Manejar archivos adicionales
            archivos = request.files.getlist('archivos')
            for archivo in archivos:
                if archivo and archivo.filename:
                    upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{archivo.filename}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    archivo.save(filepath)
                    
                    archivo_db = ArchivoYogaterapia(
                        sesion_yogaterapia_id=sesion.id,
                        nombre_archivo=archivo.filename,
                        ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                        tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                        tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    )
                    db.session.add(archivo_db)
            
            db.session.commit()
            flash('¡Sesión de yogaterapia actualizada exitosamente!', 'success')
            return redirect(url_for('yogatherapia.ver_sesion_yogaterapia', sesion_id=sesion_id))
            
        except Exception as e:
            flash(f'Error al actualizar sesión: {str(e)}', 'error')
            db.session.rollback()
    
    archivos = ArchivoYogaterapia.query.filter_by(sesion_yogaterapia_id=sesion_id).all()
    return render_template('editar_sesion_yogaterapia.html', sesion=sesion, archivos=archivos)

@yogatherapia_bp.route('/api/citas/<fecha>')
@login_required
def obtener_citas_fecha(fecha):
    """API para obtener citas de una fecha específica (para el calendario)"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        dia_semana = fecha_obj.weekday()
        
        # Obtener sesiones de yogaterapia
        citas = SesionYogaterapia.query.filter(
            SesionYogaterapia.fecha_sesion == fecha_obj,
            SesionYogaterapia.hora_inicio.isnot(None)
        ).order_by(SesionYogaterapia.hora_inicio).all()
        
        # Obtener horarios semanales para ese día
        horarios_semanal = HorarioSemanal.query.filter(
            HorarioSemanal.dia_semana == dia_semana,
            HorarioSemanal.activo == True
        ).all()
        
        citas_data = []
        
        # Agregar sesiones de yogaterapia
        for cita in citas:
            citas_data.append({
                'id': cita.id,
                'alumno': f"{cita.alumno.nombre} {cita.alumno.apellido}",
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_fin': cita.hora_fin.strftime('%H:%M') if cita.hora_fin else None,
                'duracion': cita.duracion_minutos,
                'precio': cita.precio,
                'pagado': cita.pagado,
                'tipo': 'yogaterapia',
                'color': '#8B5FBF'
            })
        
        # Agregar clases grupales
        for horario in horarios_semanal:
            citas_data.append({
                'id': f"grupal_{horario.id}",
                'alumno': horario.clase.nombre,
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
                'duracion': horario.clase.duracion_minutos,
                'precio': horario.clase.precio,
                'pagado': True,
                'tipo': 'clase_grupal',
                'color': '#28a745'
            })
        
        # Ordenar por hora de inicio
        citas_data.sort(key=lambda x: x['hora_inicio'])
        
        return jsonify(citas_data)
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400

@yogatherapia_bp.route('/api/verificar-conflicto', methods=['POST'])
@login_required
def verificar_conflicto_api():
    """API para verificar conflictos de horario en tiempo real"""
    try:
        data = request.get_json()
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        sesion_id = data.get('sesion_id')
        
        conflicto, info_conflicto = verificar_conflicto_horario(fecha, hora_inicio, hora_fin, sesion_id)
        
        return jsonify({
            'conflicto': conflicto,
            'mensaje': info_conflicto['mensaje'] if conflicto else None,
            'tipo': info_conflicto['tipo'] if conflicto else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>/archivos/eliminar/<int:archivo_id>', methods=['POST'])
@login_required
def eliminar_archivo_yogaterapia(sesion_id, archivo_id):
    """Eliminar un archivo de yogaterapia"""
    try:
        archivo = ArchivoYogaterapia.query.filter_by(
            id=archivo_id, 
            sesion_yogaterapia_id=sesion_id
        ).first_or_404()
        
        # Eliminar archivo físico
        if os.path.exists(archivo.ruta_archivo):
            os.remove(archivo.ruta_archivo)
        
        # Eliminar registro de base de datos
        db.session.delete(archivo)
        db.session.commit()
        
        flash('Archivo eliminado correctamente', 'success')
        return redirect(url_for('yogatherapia.ver_sesion_yogaterapia', sesion_id=sesion_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar archivo: {str(e)}', 'error')
        return redirect(url_for('yogatherapia.ver_sesion_yogaterapia', sesion_id=sesion_id))

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>/archivos/agregar', methods=['POST'])
@login_required
def agregar_archivo_yogaterapia(sesion_id):
    """Agregar archivos a una sesión de yogaterapia"""
    try:
        sesion = SesionYogaterapia.query.get_or_404(sesion_id)
        
        archivos = request.files.getlist('archivos')
        archivos_agregados = 0
        
        for archivo in archivos:
            if archivo and archivo.filename:
                # Crear directorio para archivos de yogaterapia
                upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{archivo.filename}"
                filepath = os.path.join(upload_dir, filename)
                
                # Guardar archivo
                archivo.save(filepath)
                
                # Crear registro en base de datos
                archivo_db = ArchivoYogaterapia(
                    sesion_yogaterapia_id=sesion.id,
                    nombre_archivo=archivo.filename,
                    ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                    tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                    tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                )
                db.session.add(archivo_db)
                archivos_agregados += 1
        
        db.session.commit()
        flash(f'{archivos_agregados} archivo(s) agregado(s) correctamente', 'success')
        return redirect(url_for('yogatherapia.ver_sesion_yogaterapia', sesion_id=sesion_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar archivos: {str(e)}', 'error')
        return redirect(url_for('yogatherapia.ver_sesion_yogaterapia', sesion_id=sesion_id))

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_sesion_yogaterapia(sesion_id):
    """Eliminar una sesión de yogaterapia"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    try:
        # Eliminar archivos asociados
        for archivo in sesion.archivos:
            try:
                if os.path.exists(archivo.ruta_archivo):
                    os.remove(archivo.ruta_archivo)
            except Exception as e:
                print(f"Error eliminando archivo {archivo.ruta_archivo}: {e}")
        
        # Eliminar la sesión
        db.session.delete(sesion)
        db.session.commit()
        
        flash(f'✅ Sesión de {sesion.alumno.nombre} {sesion.alumno.apellido} eliminada exitosamente', 'success')
        return redirect(url_for('yogatherapia.yogaterapia'))
        
    except Exception as e:
        flash(f'Error al eliminar sesión: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('yogatherapia.yogaterapia'))

@yogatherapia_bp.route('/yogaterapia/<int:sesion_id>/marcar_pagado', methods=['POST'])
@login_required
def marcar_sesion_pagada(sesion_id):
    """Marcar una sesión como pagada"""
    sesion = SesionYogaterapia.query.get_or_404(sesion_id)
    
    try:
        sesion.pagado = True
        sesion.metodo_pago = request.form.get('metodo_pago', 'efectivo')
        
        db.session.commit()
        flash('¡Sesión marcada como pagada!', 'success')
        
    except Exception as e:
        flash(f'Error al marcar como pagada: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('yogatherapia.yogaterapia'))

@yogatherapia_bp.route('/alumnos/<int:alumno_id>/yogaterapia/nueva', methods=['GET', 'POST'])
@login_required
def nueva_yogaterapia_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            # Procesar horas
            hora_inicio = None
            hora_fin = None
            if request.form.get('hora_inicio'):
                hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            if request.form.get('hora_fin'):
                hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
            
            sesion = SesionYogaterapia(
                alumno_id=alumno_id,
                fecha_sesion=datetime.strptime(request.form['fecha_sesion'], '%Y-%m-%d').date(),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                duracion_minutos=int(request.form.get('duracion_minutos', 60)),
                tipo_sesion=request.form.get('tipo_sesion', 'individual'),
                motivo_consulta=request.form.get('motivo_consulta'),
                objetivos_terapeuticos=request.form.get('objetivos_terapeuticos'),
                tecnicas_aplicadas=request.form.get('tecnicas_aplicadas'),
                posturas_trabajadas=request.form.get('posturas_trabajadas'),
                respiracion_pranayama=request.form.get('respiracion_pranayama'),
                meditacion_relajacion=request.form.get('meditacion_relajacion'),
                estado_inicial=request.form.get('estado_inicial'),
                respuesta_sesion=request.form.get('respuesta_sesion'),
                estado_final=request.form.get('estado_final'),
                observaciones_terapeuta=request.form.get('observaciones_terapeuta'),
                recomendaciones_casa=request.form.get('recomendaciones_casa'),
                proxima_sesion=request.form.get('proxima_sesion'),
                instructor=request.form.get('instructor', 'Minouche'),
                precio=float(request.form.get('precio', 45.00)),
                pagado='pagado' in request.form,
                metodo_pago=request.form.get('metodo_pago')
            )
            
            db.session.add(sesion)
            db.session.flush()
            
            # Manejar archivos subidos
            archivos = request.files.getlist('archivos')
            for archivo in archivos:
                if archivo and archivo.filename:
                    # Crear directorio para archivos de yogaterapia
                    upload_dir = os.path.join('uploads', 'yogaterapia', str(sesion.id))
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generar nombre único para el archivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{archivo.filename}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    # Guardar archivo
                    archivo.save(filepath)
                    
                    # Crear registro en base de datos
                    archivo_db = ArchivoYogaterapia(
                        sesion_yogaterapia_id=sesion.id,
                        nombre_archivo=archivo.filename,
                        ruta_archivo=f'yogaterapia/{sesion.id}/{filename}',
                        tipo_archivo=filename.split('.')[-1].lower() if '.' in filename else 'unknown',
                        tamaño_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    )
                    db.session.add(archivo_db)
            
            # Si está pagado, crear registro de pago
            if sesion.pagado:
                pago = Pago(
                    alumno_id=alumno_id,
                    fecha_clase=sesion.fecha_sesion,
                    monto=sesion.precio,
                    tipo_pago='yogaterapia',
                    descripcion=f'Yogaterapia - {sesion.tipo_sesion}',
                    metodo_pago=sesion.metodo_pago
                )
                db.session.add(pago)
            
            db.session.commit()
            flash(f'¡Sesión de yogaterapia registrada exitosamente para {alumno.nombre} {alumno.apellido}!', 'success')
            return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))
            
        except Exception as e:
            flash(f'Error al registrar sesión: {str(e)}', 'error')
            db.session.rollback()
    
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre, Alumno.apellido).all()
    return render_template('nueva_yogaterapia.html', alumno=alumno, alumnos=alumnos, from_student=True)
