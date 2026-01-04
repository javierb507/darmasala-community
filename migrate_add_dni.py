"""
Script de migracion para anadir el campo DNI al modelo Alumno
"""
import sqlite3
from datetime import datetime

DB_PATH = 'atma_suddhi.db'

def migrate_add_dni():
    """Anade la columna DNI a la tabla alumno"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(alumno)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'dni' in columns:
            print("OK - La columna 'dni' ya existe en la tabla alumno")
            return

        # Anadir la columna DNI
        cursor.execute("""
            ALTER TABLE alumno
            ADD COLUMN dni VARCHAR(20)
        """)

        conn.commit()
        print("OK - Columna 'dni' anadida exitosamente a la tabla alumno")

        # Verificar la estructura de la tabla
        cursor.execute("PRAGMA table_info(alumno)")
        print("\nOK - Estructura actualizada de la tabla alumno:")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")

    except Exception as e:
        conn.rollback()
        print(f"ERROR durante la migracion: {str(e)}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACION: Anadir campo DNI a la tabla Alumno")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    migrate_add_dni()

    print("\n" + "=" * 60)
    print("MIGRACION COMPLETADA")
    print("=" * 60)
