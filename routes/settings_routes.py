from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from datetime import datetime, date
import os
import shutil
import json
from models import db, CategoriaGasto, Sutra, Configuracion, Tarifa, Instructor, Clase, HorarioSemanal, Alumno, Pago, Asistencia, FacturaEmitida, FacturaProveedor, Cliente, Proveedor, GastoFijo
from utils.auth_utils import login_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/configuracion')
@login_required
def configuracion():
    # Obtener todas las configuraciones
    configuraciones = Configuracion.query.all()
    config_dict = {c.clave: c.valor for c in configuraciones}
    
    # Obtener categorías y sutras (ya existían en la ruta anterior)
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    sutras = Sutra.query.all()
    
    # Obtener datos para las nuevas pestañas
    clases = Clase.query.all()
    tarifas = Tarifa.query.all()
    instructores = Instructor.query.all()
    horarios = HorarioSemanal.query.all()
    
    # Backups (lógica simplificada)
    backups = []
    if os.path.exists('backups'):
        for f in os.listdir('backups'):
            if f.endswith('.db'):
                stats = os.stat(os.path.join('backups', f))
                backups.append({
                    'nombre': f,
                    'fecha': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'tamaño': f"{stats.st_size / 1024:.2f} KB"
                })
        # Ordenar por fecha descendente
        backups.sort(key=lambda x: x['fecha'], reverse=True)

    return render_template('configuracion.html', 
                          config=config_dict, 
                          clases=clases, 
                          tarifas=tarifas, 
                          instructores=instructores,
                          horarios=horarios,
                          categorias=categorias, 
                          sutras=sutras, 
                          backups=backups)

@settings_bp.route('/categorias-gasto/nueva', methods=['POST'])
@login_required
def nueva_categoria_gasto():
    """Crear nueva categoría de gasto"""
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion', '')
    
    if not nombre:
        flash('El nombre es obligatorio', 'error')
        return redirect(url_for('settings.configuracion'))
    
    try:
        categoria = CategoriaGasto(nombre=nombre, descripcion=descripcion)
        db.session.add(categoria)
        db.session.commit()
        flash('Categoría creada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear categoría: {str(e)}', 'error')
    
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/categorias-gasto/<int:categoria_id>/editar', methods=['POST'])
@login_required
def editar_categoria_gasto(categoria_id):
    """Editar categoría de gasto"""
    categoria = CategoriaGasto.query.get_or_404(categoria_id)
    categoria.nombre = request.form.get('nombre')
    categoria.descripcion = request.form.get('descripcion', '')
    categoria.activo = 'activo' in request.form
    
    try:
        db.session.commit()
        flash('Categoría actualizada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar categoría: {str(e)}', 'error')
    
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/backup/crear', methods=['POST'])
@login_required
def crear_backup():
    """Crear backup de la base de datos"""
    try:
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_path = 'yoga_escuela.db'
        backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            flash(f'Backup creado exitosamente: {os.path.basename(backup_path)}', 'success')
        else:
            flash('Error: No se encontró el archivo de base de datos', 'error')
            
    except Exception as e:
        flash(f'Error al crear backup: {str(e)}', 'error')
        
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/backup/restaurar', methods=['POST'])
@login_required
def restaurar_backup():
    """Restaurar backup de la base de datos"""
    try:
        if 'backup_file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('settings.configuracion'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('settings.configuracion'))
        
        if file and file.filename.endswith('.db'):
            # Crear backup del archivo actual antes de restaurar
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_actual = f'yoga_school_backup_before_restore_{timestamp}.db'
            db_path = 'yoga_escuela.db'
            
            if os.path.exists(db_path):
                backup_dir = 'backups'
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copy2(db_path, os.path.join(backup_dir, backup_actual))
            
            # Restaurar el archivo subido
            file.save(db_path)
            flash('Backup restaurado exitosamente. Se creó un backup del estado anterior.', 'success')
        else:
            flash('Formato de archivo no válido. Solo se permiten archivos .db', 'error')
            
    except Exception as e:
        flash(f'Error al restaurar backup: {str(e)}', 'error')
    
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/backup/eliminar/<nombre>', methods=['POST'])
@login_required
def eliminar_backup(nombre):
    """Eliminar un archivo de backup"""
    try:
        backup_path = os.path.join('backups', nombre)
        if os.path.exists(backup_path) and nombre.endswith('.db'):
            os.remove(backup_path)
            flash('Backup eliminado correctamente', 'success')
        else:
            flash('Error: No se pudo encontrar el archivo', 'error')
    except Exception as e:
        flash(f'Error al eliminar backup: {str(e)}', 'error')
        
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/exportar-datos/<tipo>')
@login_required
def export_data(tipo):
    """Exportar datos (alumnos, asistencias, etc.) a CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    output = StringIO()
    writer = csv.writer(output)
    
    if tipo == 'alumnos':
        alumnos = Alumno.query.all()
        writer.writerow(['Nombre', 'Apellido', 'Email', 'Teléfono', 'Fecha Registro', 'Activo'])
        for a in alumnos:
            writer.writerow([a.nombre, a.apellido, a.email, a.telefono, a.fecha_registro.strftime('%Y-%m-%d') if a.fecha_registro else '', 'Sí' if a.activo else 'No'])
            
    elif tipo == 'asistencias':
        asistencias = Asistencia.query.all()
        writer.writerow(['Alumno', 'Clase', 'Fecha', 'Presente', 'Notas'])
        for a in asistencias:
            alumno_nom = f"{a.alumno.nombre} {a.alumno.apellido}" if a.alumno else "N/A"
            clase_nom = a.horario.clase.nombre if a.horario and a.horario.clase else "N/A"
            writer.writerow([alumno_nom, clase_nom, a.fecha_clase.strftime('%Y-%m-%d') if a.fecha_clase else '', 'Sí' if a.presente else 'No', a.observaciones or ''])
    
    # ... handle other types if needed from app_recovered
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=export_{tipo}_{datetime.now().strftime('%Y%m%d')}.csv"
    response.headers["Content-type"] = "text/csv"
    return response
@settings_bp.route('/sutras/nuevo', methods=['POST'])
@login_required
def nuevo_sutra():
    """Agregar un nuevo sutra"""
    numero = request.form.get('numero')
    contenido_sanscrito = request.form.get('contenido_sanscrito')
    contenido_espanol = request.form.get('contenido_espanol', '')
    significado = request.form.get('significado', '')
    libro = request.form.get('libro', 'Yoga Sutras de Patanjali')
    
    if not numero or not contenido_sanscrito:
        flash('Número y contenido sánscrito son obligatorios', 'error')
        return redirect(url_for('settings.configuracion'))
    
    try:
        sutra = Sutra(
            numero=numero,
            contenido_sanscrito=contenido_sanscrito,
            contenido_espanol=contenido_espanol,
            significado=significado,
            libro=libro
        )
        db.session.add(sutra)
        db.session.commit()
        flash('Sutra agregado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar sutra: {str(e)}', 'error')
    
    return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/guardar', methods=['POST'])
@login_required
def guardar_configuracion():
    try:
        # Manejar subida de logo
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                logo_dir = os.path.join('static', 'images')
                os.makedirs(logo_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"logo_{timestamp}.{logo_file.filename.split('.')[-1]}"
                filepath = os.path.join(logo_dir, filename)
                
                logo_file.save(filepath)
                
                config_logo = Configuracion.query.filter_by(clave='logo_escuela').first()
                if config_logo:
                    config_logo.valor = f"images/{filename}"
                else:
                    config_logo = Configuracion(
                        clave='logo_escuela',
                        valor=f"images/{filename}",
                        descripcion='Logo de la escuela'
                    )
                    db.session.add(config_logo)

        # Manejar subida de fondo login admin
        if 'fondo_login_admin' in request.files:
            fondo_file = request.files['fondo_login_admin']
            if fondo_file and fondo_file.filename:
                img_dir = os.path.join('static', 'images')
                os.makedirs(img_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"bg_admin_{timestamp}.{fondo_file.filename.split('.')[-1]}"
                fondo_file.save(os.path.join(img_dir, filename))
                
                config_fondo = Configuracion.query.filter_by(clave='fondo_login_admin').first()
                if not config_fondo:
                    config_fondo = Configuracion(clave='fondo_login_admin', descripcion='Fondo login admin')
                    db.session.add(config_fondo)
                config_fondo.valor = f"images/{filename}"

        configuraciones = [
            ('precio_clase_suelta', request.form.get('precio_clase_suelta', '15.00'), 'Precio por clase suelta'),
            ('precio_1_clase_semanal', request.form.get('precio_1_clase_semanal', '40.00'), 'Precio 1 clase por semana'),
            ('precio_2_clases_semanal', request.form.get('precio_2_clases_semanal', '70.00'), 'Precio 2 clases por semana'),
            ('precio_tarifa_plana', request.form.get('precio_tarifa_plana', '90.00'), 'Precio tarifa plana'),
            ('precio_1_clase_bimensual', request.form.get('precio_1_clase_bimensual', '75.00'), 'Precio 1 clase bimensual'),
            ('precio_2_clases_bimensual', request.form.get('precio_2_clases_bimensual', '135.00'), 'Precio 2 clases bimensual'),
            ('precio_matricula', request.form.get('precio_matricula', '25.00'), 'Precio de matrícula anual'),
            ('precio_yogaterapia_individual', request.form.get('precio_yogaterapia_individual', '50.00'), 'Precio yogaterapia individual'),
            ('precio_yogaterapia_pareja', request.form.get('precio_yogaterapia_pareja', '70.00'), 'Precio yogaterapia en pareja'),
            ('nombre_escuela', request.form.get('nombre_escuela', 'DARMASALA'), 'Nombre de la escuela'),
            ('direccion_escuela', request.form.get('direccion_escuela', ''), 'Dirección de la escuela'),
            ('telefono_escuela', request.form.get('telefono_escuela', ''), 'Teléfono de contacto'),
            ('email_escuela', request.form.get('email_escuela', ''), 'Email de contacto'),
            ('web_escuela', request.form.get('web_escuela', 'https://darmasala.cloud'), 'Página web'),
            ('nombre_instructora', request.form.get('nombre_instructora', 'Minouche'), 'Nombre de la instructora principal'),
            ('email_instructora', request.form.get('email_instructora', ''), 'Email de la instructora'),
            ('telefono_instructora', request.form.get('telefono_instructora', ''), 'Teléfono de la instructora'),
            ('numero_cuenta', request.form.get('numero_cuenta', ''), 'Número de cuenta bancaria'),
            ('cif_escuela', request.form.get('cif_escuela', ''), 'CIF de la escuela'),
            ('session_timeout_admin', request.form.get('session_timeout_admin', '60'), 'Timeout sesión (minutos)'),
        ]
        
        for clave, valor, descripcion in configuraciones:
            config_existente = Configuracion.query.filter_by(clave=clave).first()
            if config_existente:
                config_existente.valor = valor
                config_existente.descripcion = descripcion
                config_existente.fecha_actualizacion = datetime.utcnow()
            else:
                nueva_config = Configuracion(
                    clave=clave,
                    valor=valor,
                    descripcion=descripcion
                )
                db.session.add(nueva_config)
        
        db.session.commit()
        flash('¡Configuración guardada exitosamente!', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al guardar configuración: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/clases/nueva', methods=['POST'])
@login_required
def nueva_clase():
    try:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        color = request.form.get('color', '#6c757d')

        if not nombre:
            flash('El nombre de la clase es obligatorio', 'error')
            return redirect(url_for('settings.configuracion'))

        clase_existente = Clase.query.filter_by(nombre=nombre).first()
        if clase_existente:
            flash(f'Ya existe una clase con el nombre "{nombre}"', 'error')
            return redirect(url_for('settings.configuracion'))

        duracion_minutos = request.form.get('duracion_minutos', 75, type=int)
        periodicidad = request.form.get('periodicidad', 'semanal')

        clase = Clase(
            nombre=nombre,
            descripcion=descripcion,
            color=color,
            duracion_minutos=duracion_minutos,
            periodicidad=periodicidad,
            activa=True
        )
        db.session.add(clase)
        db.session.commit()

        flash(f'Clase "{nombre}" creada exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al crear la clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/tarifas/nueva', methods=['POST'])
@login_required
def nueva_tarifa():
    try:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = request.form.get('precio')

        if not nombre or not precio:
            flash('El nombre y el precio son obligatorios', 'error')
            return redirect(url_for('settings.configuracion'))

        tarifa_existente = Tarifa.query.filter_by(nombre=nombre).first()
        if tarifa_existente:
            flash(f'Ya existe una tarifa con el nombre "{nombre}"', 'error')
            return redirect(url_for('settings.configuracion'))

        tarifa = Tarifa(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            activa=True
        )
        db.session.add(tarifa)
        db.session.commit()

        flash(f'Tarifa "{nombre}" creada exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al crear la tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/instructores/nuevo', methods=['POST'])
@login_required
def nuevo_instructor():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email', '')
        telefono = request.form.get('telefono', '')
        especialidad = request.form.get('especialidad', '')

        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return redirect(url_for('settings.configuracion'))

        instructor = Instructor(
            nombre=nombre,
            email=email,
            telefono=telefono,
            especialidad=especialidad,
            activo=True
        )
        db.session.add(instructor)
        db.session.commit()

        flash(f'Instructor "{nombre}" creado exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al crear instructor: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/instructores/<int:instructor_id>/eliminar', methods=['POST'])
@login_required
def eliminar_instructor(instructor_id):
    try:
        instructor = Instructor.query.get_or_404(instructor_id)
        nombre = instructor.nombre
        db.session.delete(instructor)
        db.session.commit()
        flash(f'Instructor "{nombre}" eliminado exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al eliminar instructor: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/tarifas/<int:tarifa_id>/toggle', methods=['POST'])
@login_required
def toggle_tarifa(tarifa_id):
    try:
        tarifa = Tarifa.query.get_or_404(tarifa_id)
        tarifa.activa = not tarifa.activa
        db.session.commit()
        estado = 'activada' if tarifa.activa else 'desactivada'
        flash(f'Tarifa "{tarifa.nombre}" {estado} exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al cambiar estado de tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/tarifas/<int:tarifa_id>/eliminar', methods=['POST'])
@login_required
def eliminar_tarifa(tarifa_id):
    try:
        tarifa = Tarifa.query.get_or_404(tarifa_id)
        nombre = tarifa.nombre
        db.session.delete(tarifa)
        db.session.commit()
        flash(f'Tarifa "{nombre}" eliminada exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al eliminar tarifa: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/clases/<int:clase_id>/eliminar', methods=['POST'])
@login_required
def eliminar_clase(clase_id):
    try:
        clase = Clase.query.get_or_404(clase_id)
        if clase.horarios:
            flash(f'No se puede eliminar la clase "{clase.nombre}" porque tiene horarios asociados', 'error')
            return redirect(url_for('settings.configuracion'))
        nombre = clase.nombre
        db.session.delete(clase)
        db.session.commit()
        flash(f'Clase "{nombre}" eliminada exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al eliminar clase: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/horarios/nuevo', methods=['POST'])
@login_required
def configuracion_nuevo_horario():
    try:
        from datetime import datetime, time
        clase_id = request.form.get('clase_id')
        dia_semana = request.form.get('dia_semana', type=int)
        
        # Parse hours
        hora_inicio_str = request.form.get('hora_inicio')
        hora_fin_str = request.form.get('hora_fin')
        
        h_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        h_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
        
        horario = HorarioSemanal(
            clase_id=clase_id,
            dia_semana=dia_semana,
            hora_inicio=h_inicio,
            hora_fin=h_fin,
            instructor=request.form.get('instructor', 'Minouche'),
            activo=True
        )
        db.session.add(horario)
        db.session.commit()
        flash('Horario añadido exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al añadir horario: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/horarios/<int:horario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_horario_config(horario_id):
    try:
        horario = HorarioSemanal.query.get_or_404(horario_id)
        db.session.delete(horario)
        db.session.commit()
        flash('Horario eliminado exitosamente', 'success')
        return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al eliminar horario: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/configuracion/clases/<int:clase_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_clase_config(clase_id):
    """Editar clase existente"""
    clase = Clase.query.get_or_404(clase_id)
    
    if request.method == 'POST':
        try:
            clase.nombre = request.form['nombre']
            clase.descripcion = request.form.get('descripcion')
            clase.color = request.form.get('color', '#007bff')
            clase.duracion_minutos = request.form.get('duracion_minutos', 75, type=int)
            clase.capacidad_maxima = request.form.get('capacidad_maxima', 15, type=int)
            clase.nivel = request.form.get('nivel', 'todos')
            
            # Si el modelo Clase tiene campos de precio específicos, los actualizamos aquí
            # De lo contrario, se manejan en la configuración general
            if hasattr(clase, 'precio_clase_suelta'):
                clase.precio_clase_suelta = float(request.form.get('precio_clase_suelta', 0))
                clase.precio_1_semanal = float(request.form.get('precio_1_semanal', 0))
                clase.precio_2_semanal = float(request.form.get('precio_2_semanal', 0))
                clase.precio_plana = float(request.form.get('precio_plana', 0))
                clase.precio_1_bimensual = float(request.form.get('precio_1_bimensual', 0))
                clase.precio_2_bimensual = float(request.form.get('precio_2_bimensual', 0))

            db.session.commit()
            flash('¡Clase actualizada exitosamente!', 'success')
            return redirect(url_for('settings.configuracion'))
        except Exception as e:
            flash(f'Error al actualizar clase: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('configuracion/editar_clase.html', clase=clase)

@settings_bp.route('/descargar-db')
@login_required
def descargar_db():
    try:
        db_path = 'yoga_escuela.db'
        if os.path.exists(db_path):
            return send_file(db_path, as_attachment=True)
        else:
            flash('Error: Archivo de base de datos no encontrado', 'error')
            return redirect(url_for('settings.configuracion'))
    except Exception as e:
        flash(f'Error al descargar base de datos: {str(e)}', 'error')
        return redirect(url_for('settings.configuracion'))

@settings_bp.route('/modo-pruebas')
@login_required
def modo_pruebas():
    stats = {
        'alumnos': Alumno.query.count(),
        'horarios': HorarioSemanal.query.count(),
        'asistencias': Asistencia.query.count(),
        'facturas_emitidas': FacturaEmitida.query.count(),
        'facturas_proveedores': FacturaProveedor.query.count(),
        'clientes': Cliente.query.count(),
        'proveedores': Proveedor.query.count(),
        'gastos_fijos': GastoFijo.query.count()
    }
    return render_template('modo_pruebas.html', stats=stats)

@settings_bp.route('/cargar-datos-prueba', methods=['POST'])
@login_required
def cargar_datos_prueba():
    try:
        from cargar_datos_prueba_completos import cargar_datos_completos
        resumen = cargar_datos_completos(modo_web=True)
        flash(
            '¡Datos de prueba cargados! '
            f"Alumnos: {resumen['alumnos']}, horarios: {resumen['horarios']}, "
            f"asistencias: {resumen['asistencias']}, pagos: {resumen['pagos']}, "
            f"facturas emitidas: {resumen['facturas_emitidas']}, "
            f"facturas proveedores: {resumen['facturas_proveedores']}.",
            'success'
        )
    except Exception as e:
        flash(f'Error al cargar datos de prueba: {str(e)}', 'error')
        db.session.rollback()
    return redirect(url_for('settings.modo_pruebas'))

@settings_bp.route('/resetear-sistema', methods=['POST'])
@login_required
def resetear_sistema():
    try:
        # Eliminar en orden para respetar foreign keys
        Asistencia.query.delete()
        # Agregar otros modelos según sea necesario
        db.session.commit()
        flash('Sistema reseteado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al resetear sistema: {str(e)}', 'error')
        db.session.rollback()
    return redirect(url_for('settings.modo_pruebas'))
