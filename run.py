#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de gestión de escuela de yoga
"""

import os
from app import app
from models import db

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando Atma Suddhi - Gestión de Escuela de Yoga")
    print("=" * 50)
    
    with app.app_context():
        # Asegurarse de que la base de datos existe
        db.create_all()
        print("✅ Base de datos verificada")
        print("🚀 Aplicación lista en: http://localhost:5001")
        print("=" * 50)
    
    # Ejecutar la aplicación
    # Se usa el puerto 5001 para evitar conflictos con otros servicios locales
    app.run(debug=True, host='0.0.0.0', port=5001)