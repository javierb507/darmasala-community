#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Atma Suddhi
"""

if __name__ == '__main__':
    print("🧘‍♀️ Iniciando Atma Suddhi - Gestión de Escuela de Yoga")
    print("=" * 60)
    
    try:
        # Importar la aplicación principal
        from app import app, db, inicializar_clases
        
        # Inicializar base de datos
        with app.app_context():
            db.create_all()
            inicializar_clases()
            print("✅ Base de datos inicializada")
            print("✅ Clases básicas creadas")
        
        print("🚀 Aplicación disponible en: http://localhost:5000")
        print("📋 Usa Ctrl+C para detener la aplicación")
        print("=" * 60)
        
        # Ejecutar la aplicación
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verifica que app.py esté presente y sea correcto")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Revisa la configuración de la aplicación")