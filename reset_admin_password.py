#!/usr/bin/env python3
"""
Script para resetear la contraseña del administrador
Ejecutar en Hostinger para forzar el reset de credenciales
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario

def reset_admin_password():
    """Resetear la contraseña del administrador"""
    
    with app.app_context():
        try:
            # Buscar usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if admin:
                # Actualizar contraseña
                admin.password_hash = generate_password_hash('AtmaSuddhi74')
                db.session.commit()
                print("✅ Contraseña del administrador actualizada")
                print("Usuario: admin")
                print("Contraseña: AtmaSuddhi74")
            else:
                # Crear usuario admin si no existe
                admin = Usuario(
                    username='admin',
                    email='admin@atmasuddhi.es',
                    password_hash=generate_password_hash('AtmaSuddhi74'),
                    nombre='Administrador',
                    apellido='Sistema',
                    rol='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario administrador creado")
                print("Usuario: admin")
                print("Contraseña: AtmaSuddhi74")
            
            # Verificar que funciona
            if check_password_hash(admin.password_hash, 'AtmaSuddhi74'):
                print("✅ Verificación exitosa - La contraseña funciona")
            else:
                print("❌ Error - La contraseña no funciona")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_admin_password()
