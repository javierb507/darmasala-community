#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de gestión de escuela de yoga
"""

from app import app
from models import db
from utils.app_utils import inicializar_clases, inicializar_categorias_gastos

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando Atma Suddhi - Gestión de Escuela de Yoga")
    print("=" * 50)
    
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        
        # Inicializar datos básicos
        inicializar_clases()
        inicializar_categorias_gastos()
        
        print("✅ Base de datos inicializada")
        print("🚀 Aplicación lista en: http://localhost:5000")
        print("=" * 50)
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)