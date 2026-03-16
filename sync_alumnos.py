from app import app, db
from models import Alumno, Usuario
from werkzeug.security import generate_password_hash
import sys

def sync_students_to_users():
    with app.app_context():
        print("🔄 Sincronizando Alumnos con Usuarios del Sistema...")
        
        alumnos = Alumno.query.all()
        created_count = 0
        updated_count = 0
        
        for alumno in alumnos:
            # Buscar si ya existe un usuario con este email
            usuario = Usuario.query.filter_by(email=alumno.email).first()
            
            # Determinar contraseña inicial (DNI o Teléfono)
            password_inicial = alumno.dni if alumno.dni else alumno.telefono
            if not password_inicial:
                password_inicial = "Yoga2026" # Fallback muy básico si no hay nada
            
            if not usuario:
                # Crear nuevo usuario para el alumno
                nuevo_usuario = Usuario(
                    username=alumno.email,
                    email=alumno.email,
                    password_hash=generate_password_hash(password_inicial),
                    nombre=alumno.nombre,
                    apellido=alumno.apellido,
                    rol='alumno',
                    activo=alumno.activo
                )
                db.session.add(nuevo_usuario)
                created_count += 1
                print(f"✅ Usuario creado para: {alumno.nombre} {alumno.apellido} ({alumno.email})")
            else:
                # Actualizar estado de activación y datos básicos
                # Solo actualizamos el rol si no es ya un admin/instructor (por si acaso)
                if usuario.rol not in ['admin', 'instructor']:
                    usuario.rol = 'alumno'
                
                usuario.activo = alumno.activo
                usuario.nombre = alumno.nombre
                usuario.apellido = alumno.apellido
                updated_count += 1
                # print(f"ℹ️ Usuario actualizado para: {alumno.nombre} {alumno.apellido}")

        try:
            db.session.commit()
            print("\n" + "="*50)
            print(f"📊 Resumen de sincronización:")
            print(f"   - Usuarios creados: {created_count}")
            print(f"   - Usuarios actualizados: {updated_count}")
            print("="*50)
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la sincronización: {e}")

if __name__ == "__main__":
    sync_students_to_users()
