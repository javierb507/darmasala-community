#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de gestión de escuela de yoga
"""

import os
import webbrowser
from threading import Timer
from app import app
from models import db

def open_browser():
    """Opens browser automatically after a short delay"""
    webbrowser.open_new("http://127.0.0.1:5001")

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando DarmaSala - Gestión de Escuela de Yoga")
    print("=" * 50)
    
    with app.app_context():
        # Asegurarse de que la base de datos existe
        db.create_all()
        print("✅ Base de datos verificada")
        print("🚀 Aplicación lista en: http://localhost:5001")
        print("=" * 50)
    
    # Abrir navegador automáticamente (solo en modo local/desarrollo)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':  # Evitar doble apertura en reloader
        Timer(1.5, open_browser).start()
    
    # Ejecutar la aplicación
    # Se usa el puerto 5001 para evitar conflictos con otros servicios locales
    app.run(debug=True, host='0.0.0.0', port=5001)