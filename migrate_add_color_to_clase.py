"""
Script para agregar la columna color a la tabla clase
"""
from app import app, db
import sqlite3

def add_color_column():
    """Agrega la columna color a la tabla clase"""
    with app.app_context():
        print("=" * 60)
        print("MIGRACION: Agregar columna color a tabla clase")
        print("=" * 60)
        print()

        # Obtener la ruta de la base de datos
        db_path = 'yoga_school.db'

        # Conectar directamente con sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Verificar si la columna ya existe
            cursor.execute("PRAGMA table_info(clase)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'color' in columns:
                print("La columna 'color' ya existe en la tabla clase.")
            else:
                # Agregar la columna color
                cursor.execute("ALTER TABLE clase ADD COLUMN color VARCHAR(7) DEFAULT '#4ECDC4'")
                conn.commit()
                print("OK - Columna 'color' agregada exitosamente a la tabla clase")

            conn.close()
            print()
            print("=" * 60)
            print("MIGRACION COMPLETADA")
            print("=" * 60)

        except Exception as e:
            print(f"Error durante la migracion: {str(e)}")
            conn.rollback()
            conn.close()
            raise

if __name__ == "__main__":
    add_color_column()
