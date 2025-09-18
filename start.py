#!/usr/bin/env python3
"""
Script simple para iniciar la aplicación
"""

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando Atma Suddhi...")
    
    try:
        from app import app, db, inicializar_clases
        
        with app.app_context():
            db.create_all()
            inicializar_clases()
            print("✅ Base de datos lista")
        
        print("🚀 Aplicación disponible en: http://localhost:5000")
        print("📋 Presiona Ctrl+C para detener")
        
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que todos los archivos estén en su lugar")