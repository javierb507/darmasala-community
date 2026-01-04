"""
Script para resetear completamente la base de datos y cargar datos de prueba
ESTE SCRIPT ELIMINA TODOS LOS DATOS EXISTENTES
"""
import os
from app import app, db
from migrate_add_dni import migrate as migrate_dni
from migrate_add_facturacion import migrate as migrate_facturacion
from migrate_add_periodicidad_clases import migrate as migrate_periodicidad
from cargar_datos_prueba_completos import cargar_datos_completos

def reset_database():
    """Elimina y recrea la base de datos desde cero"""
    print("=" * 70)
    print("RESETEO COMPLETO DE BASE DE DATOS")
    print("=" * 70)
    print()

    db_path = 'yoga_school.db'

    # Paso 1: Eliminar base de datos existente
    if os.path.exists(db_path):
        print(f"1. Eliminando base de datos existente: {db_path}")
        os.remove(db_path)
        print("   ✓ Base de datos eliminada")
    else:
        print(f"1. No existe base de datos previa")

    print()

    # Paso 2: Crear todas las tablas
    print("2. Creando estructura de base de datos...")
    with app.app_context():
        db.create_all()
        print("   ✓ Todas las tablas creadas")

    print()

    # Paso 3: Ejecutar migraciones
    print("3. Ejecutando migraciones...")

    try:
        print("\n   3.1. Migración: Añadir DNI a alumnos")
        migrate_dni()
        print("   ✓ Migración DNI completada")
    except Exception as e:
        print(f"   ! Migración DNI: {str(e)} (puede ser que ya exista)")

    try:
        print("\n   3.2. Migración: Sistema de facturación")
        migrate_facturacion()
        print("   ✓ Migración facturación completada")
    except Exception as e:
        print(f"   ! Migración facturación: {str(e)} (puede ser que ya exista)")

    try:
        print("\n   3.3. Migración: Periodicidad y duración de clases")
        migrate_periodicidad()
        print("   ✓ Migración periodicidad completada")
    except Exception as e:
        print(f"   ! Migración periodicidad: {str(e)} (puede ser que ya exista)")

    print()

    # Paso 4: Cargar datos de prueba
    print("4. Cargando datos de prueba completos...")
    cargar_datos_completos(modo_web=False)

    print()
    print("=" * 70)
    print("RESETEO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print("La base de datos ha sido reseteada con:")
    print("  - Estructura completa de tablas")
    print("  - Todas las migraciones aplicadas")
    print("  - Datos de prueba cargados:")
    print("    * 4 tipos de clase con periodicidad y duración")
    print("    * 11 horarios semanales")
    print("    * 10 alumnos con DNI válido")
    print("    * Asistencias de las últimas 4 semanas")
    print("    * Configuración fiscal")
    print()
    print("Puedes iniciar la aplicación con: python app.py")
    print()

if __name__ == "__main__":
    import sys

    print()
    print("⚠️  ADVERTENCIA: Este script eliminará TODOS los datos existentes")
    print()

    respuesta = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")

    if respuesta.upper() == 'SI':
        reset_database()
    else:
        print("\nOperación cancelada. No se han realizado cambios.")
        sys.exit(0)
