"""
Migración: Añadir campos de periodicidad a tabla Clase
"""
from app import app, db

def migrate():
    """Añade los campos duracion_minutos y periodicidad a la tabla clase"""
    with app.app_context():
        print("=" * 60)
        print("MIGRACIÓN: Añadir periodicidad a Clase")
        print("=" * 60)
        print()

        try:
            conn = db.engine.connect()
            result = conn.execute(db.text("PRAGMA table_info(clase)"))
            columns = [row[1] for row in result]

            changes_made = False

            # Añadir duracion_minutos si no existe
            if 'duracion_minutos' not in columns:
                print("Añadiendo columna 'duracion_minutos' a la tabla clase...")
                conn.execute(db.text("""
                    ALTER TABLE clase
                    ADD COLUMN duracion_minutos INTEGER DEFAULT 75
                """))
                changes_made = True
                print("  - Columna duracion_minutos añadida")

            # Añadir periodicidad si no existe
            if 'periodicidad' not in columns:
                print("Añadiendo columna 'periodicidad' a la tabla clase...")
                conn.execute(db.text("""
                    ALTER TABLE clase
                    ADD COLUMN periodicidad VARCHAR(50) DEFAULT 'semanal'
                """))
                changes_made = True
                print("  - Columna periodicidad añadida")

            if changes_made:
                conn.commit()
                print()
                print("=" * 60)
                print("MIGRACIÓN COMPLETADA")
                print("=" * 60)
            else:
                print("Las columnas ya existen. No es necesario migrar.")
                print()

            conn.close()

        except Exception as e:
            print(f"Error durante la migración: {str(e)}")
            conn.rollback()
            conn.close()
            raise

if __name__ == "__main__":
    migrate()
