#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de gestión de escuela de yoga
"""

from app import app, db, inicializar_clases

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando Atma Suddhi - Gestión de Escuela de Yoga")
    print("=" * 50)
    
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        
        # Inicializar clases básicas
        inicializar_clases()
        
        print("✅ Base de datos inicializada")
        print("✅ Clases básicas creadas")
        print("🚀 Aplicación lista en: http://localhost:5000")
        print("=" * 50)
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)