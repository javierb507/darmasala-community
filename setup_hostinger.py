#!/usr/bin/env python3
"""
SETUP HOSTINGER - Script rápido para configurar la aplicación en Hostinger
Script simplificado que configura todo lo necesario para producción
"""

import os
import sys

def main():
    print("🌐 CONFIGURACIÓN RÁPIDA PARA HOSTINGER")
    print("🧘‍♀️ Atma Suddhi - Gestión de Escuela de Yoga")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py")
        print("   Asegúrate de estar en el directorio correcto")
        return 1
    
    # Verificar que las dependencias están instaladas
    try:
        import flask
        import flask_sqlalchemy
        print("✅ Dependencias verificadas")
    except ImportError as e:
        print(f"❌ Error: Falta instalar dependencias")
        print(f"   Ejecuta: pip3 install -r requirements.txt")
        return 1
    
    # Ejecutar el script de testing
    print("\n🚀 Cargando datos de prueba...")
    try:
        # Importar y ejecutar testing_app
        import testing_app
        result = testing_app.main()
        
        if result == 0:
            print("\n" + "=" * 50)
            print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
            print("=" * 50)
            print("🔗 Tu aplicación está lista en tu dominio de Hostinger")
            print("🔑 Credenciales:")
            print("   👤 Usuario: admin")
            print("   🔒 Contraseña: AtmaSuddhi74")
            print("\n📱 Funcionalidades incluidas:")
            print("   ✅ 20 alumnos con estados diversos")
            print("   ✅ 8 tipos de clases configuradas")
            print("   ✅ 3 instructores registrados")
            print("   ✅ 26 horarios semanales")
            print("   ✅ 138 pagos de ejemplo")
            print("   ✅ 22 sesiones de yogaterapia")
            print("   ✅ 181 asistencias simuladas")
            print("   ✅ Módulo de contabilidad completo")
            print("   ✅ 106 sutras de Patanjali")
            print("\n🚀 ¡Listo para usar!")
            return 0
        else:
            print("❌ Error en la configuración")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
