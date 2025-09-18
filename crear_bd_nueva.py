#!/usr/bin/env python3
"""
Script para crear una nueva base de datos con el esquema actualizado
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Eliminar base de datos existente
    if os.path.exists('yoga_school.db'):
        os.remove('yoga_school.db')
        print("🗑️ Base de datos eliminada")
    
    # Importar después de eliminar la BD
    from app import app, db
    
    with app.app_context():
        print("🏗️ Creando tablas con esquema actualizado...")
        db.create_all()
        
        # Inicializar categorías
        from app import inicializar_categorias_gastos
        inicializar_categorias_gastos()
        
        print("✅ Base de datos creada con esquema actualizado")
        print("🚀 Ahora puedes ejecutar crear_datos_simulados_mejorados.py")

if __name__ == "__main__":
    main()