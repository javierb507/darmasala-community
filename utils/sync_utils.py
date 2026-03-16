from models import db, Usuario
from werkzeug.security import generate_password_hash

def sync_alumno_to_usuario(alumno):
    """
    Sincroniza los datos de un Alumno con su cuenta de Usuario para el portal.
    Se utiliza el email como nombre de usuario y el DNI (o teléfono) como contraseña inicial.
    """
    if not alumno.email:
        return # No podemos crear usuario sin email
        
    usuario = Usuario.query.filter_by(email=alumno.email).first()
    
    # Determinar contraseña inicial
    password_inicial = alumno.dni if alumno.dni else alumno.telefono
    if not password_inicial:
        password_inicial = "Yoga2026"
    
    if not usuario:
        # Crear nuevo usuario
        usuario = Usuario(
            username=alumno.email,
            email=alumno.email,
            password_hash=generate_password_hash(password_inicial),
            nombre=alumno.nombre,
            apellido=alumno.apellido,
            rol='alumno',
            activo=alumno.activo
        )
        db.session.add(usuario)
    else:
        # Actualizar usuario existente
        # No sobreescribimos el password si ya existe el usuario (podría haberlo cambiado)
        # Tampoco sobreescribimos el rol si es admin/instructor
        if usuario.rol not in ['admin', 'instructor']:
            usuario.rol = 'alumno'
            
        usuario.activo = alumno.activo
        usuario.nombre = alumno.nombre
        usuario.apellido = alumno.apellido
        usuario.username = alumno.email
        
    # El commit se suele hacer en la ruta, pero lo hacemos aquí para asegurar el sync
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
