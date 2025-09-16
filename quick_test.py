#!/usr/bin/env python3
"""
Quick test to verify the yoga school management app
"""
import webbrowser
import time
import subprocess
import sys
import os

def main():
    print("🧘 Gestión de Escuela de Yoga - Prueba Rápida")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: ¡No se encontró app.py!")
        print("Por favor ejecuta este script desde el directorio yoga-school-management")
        print("Directorio actual:", os.getcwd())
        return False
    
    print("✅ Se encontró app.py - iniciando la aplicación...")
    print("🌐 La aplicación se abrirá en tu navegador automáticamente")
    print("📱 También puedes ir manualmente a: http://localhost:5000")
    print("\n⏳ Iniciando servidor en 3 segundos...")
    
    # Wait a moment
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ ¡Navegador abierto exitosamente!")
    except:
        print("⚠️  No se pudo abrir el navegador automáticamente")
        print("   Por favor abre manualmente: http://localhost:5000")
    
    print("\n🚀 Iniciando aplicación Flask...")
    print("   Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    # Start the Flask app
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido. ¡Gracias por probar!")
    
    return True

if __name__ == "__main__":
    main()
