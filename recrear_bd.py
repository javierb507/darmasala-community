#!/usr/bin/env python3
"""
Script para recrear la base de datos con el nuevo esquema
"""

import os
from app import app, db
from werkzeug.security import generate_password_hash

def recrear_base_datos():
    """Recrear la base de datos con el nuevo esquema"""
    print("🗑️ Eliminando base de datos existente...")
    
    # Eliminar archivo de base de datos si existe
    if os.path.exists('yoga_school.db'):
        os.remove('yoga_school.db')
        print("✅ Base de datos eliminada")
    else:
        print("ℹ️ No había base de datos existente")
    
    print("🔨 Creando nueva base de datos...")
    
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        print("🗑️ Tablas existentes eliminadas")
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Inicializar datos básicos
        from app import inicializar_clases, inicializar_categorias_gastos
        
        print("📚 Inicializando clases...")
        inicializar_clases()
        
        print("💰 Inicializando categorías de gastos...")
        inicializar_categorias_gastos()
        
        # Crear usuario administrador
        from app import Usuario
        import hashlib
        
        admin_existente = Usuario.query.filter_by(username='admin').first()
        if not admin_existente:
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
            print("👤 Usuario administrador creado: admin / admin123")
        
        print("🎉 Base de datos recreada exitosamente!")

if __name__ == '__main__':
    recrear_base_datos()