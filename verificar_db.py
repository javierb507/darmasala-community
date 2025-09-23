#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario

def verificar_base_datos():
    """Verificar el estado de la base de datos"""
    
    with app.app_context():
        try:
            print("🔍 Verificando base de datos...")
            print(f"URL de conexión: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Verificar conexión
            db.engine.execute('SELECT 1')
            print("✅ Conexión a base de datos exitosa")
            
            # Verificar tablas
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"📋 Tablas encontradas: {len(tablas)}")
            for tabla in tablas:
                print(f"  - {tabla}")
            
            # Verificar usuarios
            usuarios = Usuario.query.all()
            print(f"👥 Usuarios en la base de datos: {len(usuarios)}")
            
            for usuario in usuarios:
                print(f"  - {usuario.username} ({usuario.email}) - Rol: {usuario.rol}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    verificar_base_datos()
