"""
Migración: Añadir campo proveedor_id a tabla GastoFijo
"""
from app import app, db

def migrate():
    """Añade el campo proveedor_id a la tabla gasto_fijo"""
    with app.app_context():
        print("=" * 60)
        print("MIGRACION: Añadir proveedor_id a GastoFijo")
        print("=" * 60)
        print()

        try:
            # Verificar si la columna ya existe
            conn = db.engine.connect()
            result = conn.execute(db.text("PRAGMA table_info(gasto_fijo)"))
            columns = [row[1] for row in result]

            if 'proveedor_id' in columns:
                print("La columna 'proveedor_id' ya existe en la tabla gasto_fijo")
                print("No es necesario migrar")
                conn.close()
                return

            print("Añadiendo columna 'proveedor_id' a la tabla gasto_fijo...")

            # SQLite no permite ADD COLUMN con FOREIGN KEY directamente
            # Tenemos que hacerlo en dos pasos
            conn.execute(db.text("""
                ALTER TABLE gasto_fijo
                ADD COLUMN proveedor_id INTEGER
            """))

            conn.commit()
            conn.close()

            print("Columna añadida exitosamente")
            print()
            print("=" * 60)
            print("MIGRACION COMPLETADA")
            print("=" * 60)

        except Exception as e:
            print(f"Error durante la migración: {str(e)}")
            conn.rollback()
            conn.close()
            raise

if __name__ == "__main__":
    migrate()
