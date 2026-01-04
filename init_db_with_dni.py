"""
Script para inicializar/actualizar la base de datos con el campo DNI
"""
from app import app, db
import os

def init_database():
    """Inicializa o actualiza la base de datos"""
    with app.app_context():
        # Verificar si el archivo de base de datos existe
        db_exists = os.path.exists('atma_suddhi.db')

        if db_exists:
            print("Base de datos existente detectada")
            print("Creando todas las tablas (se añadirán columnas faltantes)...")
        else:
            print("Creando nueva base de datos...")

        # Crear todas las tablas (incluyendo el campo DNI)
        db.create_all()

        print("OK - Base de datos inicializada/actualizada correctamente")
        print(f"Archivo: atma_suddhi.db")

if __name__ == "__main__":
    print("=" * 60)
    print("INICIALIZACION/ACTUALIZACION DE BASE DE DATOS")
    print("=" * 60)
    print()

    init_database()

    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
