from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models import db, Usuario, Alumno
from utils.auth_utils import login_required, admin_required

user_routes_bp = Blueprint('users', __name__)

@user_routes_bp.route('/usuarios')
@admin_required
def usuarios():
    """Listado de usuarios del sistema"""
    # Solo administradores pueden ver esta página
    if session.get('rol') != 'admin':
        flash('No tienes permiso para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
        
    usuarios_list = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return render_template('usuarios.html', usuarios=usuarios_list)

@user_routes_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    """Crear nuevo usuario"""
    if session.get('rol') != 'admin':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        rol = request.form['rol']
        nombre = request.form['nombre']
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('users.nuevo_usuario'))
            
        hashed_password = generate_password_hash(password)
        nuevo_user = Usuario(
            username=username,
            password_hash=hashed_password,
            email=email,
            rol=rol,
            nombre=nombre
        )
        
        try:
            db.session.add(nuevo_user)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('users.usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
            
    return render_template('nuevo_usuario.html')

@user_routes_bp.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    """Editar usuario existente"""
    user = Usuario.query.get_or_404(usuario_id)
    
    # Solo el propio usuario o un admin pueden editar
    if session.get('rol') != 'admin' and session.get('user_id') != usuario_id:
        flash('No tienes permiso para editar este perfil', 'error')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        user.email = request.form['email']
        user.nombre = request.form['nombre']
        user.apellido = request.form.get('apellido', user.apellido)
        
        # Sincronizar datos si es un alumno
        if user.rol == 'alumno':
            alumno_rec = Alumno.query.filter_by(email=user.email).first()
            if alumno_rec:
                dni_val = request.form.get('dni')
                alumno_rec.dni = dni_val.strip() if dni_val and dni_val.strip() and dni_val.strip() != "None" else None
                
                tel_val = request.form.get('telefono')
                alumno_rec.telefono = tel_val.strip() if tel_val and tel_val.strip() and tel_val.strip() != "None" else None
                
                alumno_rec.nombre = user.nombre
                alumno_rec.apellido = user.apellido
        
        # Solo admin puede cambiar el rol
        if session.get('rol') == 'admin':
            user.rol = request.form['rol']
            user.activo = 'activo' in request.form
            
        # Cambiar contraseña si se proporciona
        new_password = request.form.get('password')
        if new_password:
            user.password_hash = generate_password_hash(new_password)
            
        try:
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('users.usuarios') if session.get('rol') == 'admin' else url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            
    # Si es un alumno, intentamos buscar sus datos adicionales
    alumno_data = None
    if user.rol == 'alumno':
        alumno_data = Alumno.query.filter_by(email=user.email).first()
            
    return render_template('editar_usuario.html', usuario=user, alumno=alumno_data)

@user_routes_bp.route('/perfil')
@login_required
def propio_perfil():
    """Redirige al detalle del usuario actual (mismo template que admin)."""
    user_id = session.get('user_id')
    return redirect(url_for('users.ver_usuario', usuario_id=user_id))

@user_routes_bp.route('/usuarios/<int:usuario_id>')
@login_required
def ver_usuario(usuario_id):
    """Ver detalles de un usuario"""
    if session.get('rol') != 'admin' and session.get('user_id') != usuario_id:
        flash('No tienes permiso para ver este perfil', 'error')
        return redirect(url_for('main.index'))
        
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Si es un alumno, buscamos sus datos adicionales
    alumno_data = None
    if usuario.rol == 'alumno':
        alumno_data = Alumno.query.filter_by(email=usuario.email).first()
        
    return render_template('ver_usuario.html', usuario=usuario, alumno=alumno_data)

@user_routes_bp.route('/usuarios/<int:usuario_id>/reset-link')
@login_required
def generar_reset_link(usuario_id):
    """Admin genera un enlace de reset de contraseña para un alumno."""
    if session.get('rol') != 'admin':
        flash('Acceso restringido a administradores.', 'error')
        return redirect(url_for('users.usuarios'))
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.rol != 'alumno':
        flash('Solo disponible para alumnos del portal.', 'error')
        return redirect(url_for('users.ver_usuario', usuario_id=usuario_id))
    from utils.email_utils import generate_reset_token, enviar_email, smtp_configurado
    from models import Configuracion
    token = generate_reset_token(usuario.email)
    from flask import url_for as _uf
    reset_url = _uf('student_portal.reset_password', token=token, _external=True)
    if smtp_configurado():
        cfg = {c.clave: c.valor for c in Configuracion.query.all()}
        nombre_escuela = cfg.get('nombre_escuela', 'DarmaSala')
        html = f"""<p>Hola {usuario.nombre},</p>
        <p>El administrador de {nombre_escuela} ha generado un enlace para restablecer tu contraseña.</p>
        <p><a href="{reset_url}" style="background:#1E3A2F;color:white;padding:12px 24px;
           border-radius:6px;text-decoration:none;display:inline-block;">Restablecer contraseña</a></p>
        <p>El enlace caduca en 30 minutos.</p>"""
        enviado = enviar_email(usuario.email, f'Restablece tu contraseña — {nombre_escuela}', html)
        if enviado:
            flash(f'Email de reset enviado a {usuario.email}.', 'success')
        else:
            flash(f'No se pudo enviar el email. Enlace manual (30 min): {reset_url}', 'warning')
    else:
        flash(f'SMTP no configurado. Enlace manual (válido 30 min): {reset_url}', 'info')
    return redirect(url_for('users.ver_usuario', usuario_id=usuario_id))


@user_routes_bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    """Desactivar usuario"""
    if session.get('rol') != 'admin':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('users.usuarios'))
        
    usuario = Usuario.query.get_or_404(usuario_id)
    try:
        usuario.activo = False
        db.session.commit()
        flash('Usuario desactivado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desactivar usuario: {str(e)}', 'error')
        
    return redirect(url_for('users.usuarios'))

@user_routes_bp.route('/usuarios/<int:usuario_id>/reactivar', methods=['POST'])
@login_required
def reactivar_usuario(usuario_id):
    """Reactivar usuario"""
    if session.get('rol') != 'admin':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('users.usuarios'))
        
    usuario = Usuario.query.get_or_404(usuario_id)
    try:
        usuario.activo = True
        db.session.commit()
        flash('Usuario reactivado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al reactivar usuario: {str(e)}', 'error')
        
    return redirect(url_for('users.usuarios'))
