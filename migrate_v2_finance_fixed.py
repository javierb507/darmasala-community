import os
import sqlite3
from app import app, db

def migrate():
    """Migración CORRECTA para refactorizar la tabla factura_proveedor
    - Ya renombramos a old_factura_proveedor con columna nombre_proveedor añadida.
    - Ahora recreamos factura_proveedor con el esquema correcto y copiamos.
    """
    with app.app_context():
        print("=" * 60)
        print("MIGRACION (REINTENTO): Refactorizar factura_proveedor")
        print("=" * 60)
        
        db_path = os.path.join(app.instance_path, 'yoga_school.db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. Asegurarnos que factura_proveedor no existe (si falló antes y se creó parcial)
            cursor.execute("DROP TABLE IF EXISTS factura_proveedor")
            
            # 2. Crear tabla con esquema sincronizado con models.py y proveedor_id nullable
            cursor.execute("""
            CREATE TABLE factura_proveedor (
                id INTEGER NOT NULL, 
                numero_factura VARCHAR(50) NOT NULL, 
                proveedor_id INTEGER, 
                nombre_proveedor VARCHAR(100),
                categoria_id INTEGER NOT NULL, 
                fecha_factura DATE NOT NULL, 
                fecha_vencimiento DATE, 
                importe_sin_iva FLOAT NOT NULL, 
                iva FLOAT, 
                importe_total FLOAT NOT NULL, 
                descripcion TEXT, 
                estado VARCHAR(20), 
                metodo_pago VARCHAR(50), 
                notas TEXT, 
                archivo_factura VARCHAR(200), 
                fecha_registro DATETIME, 
                PRIMARY KEY (id), 
                FOREIGN KEY(proveedor_id) REFERENCES proveedor (id), 
                FOREIGN KEY(categoria_id) REFERENCES categoria_gasto (id)
            )
            """)
            
            # 3. Copiar datos desde old_factura_proveedor
            # Identificar columnas que existen en old_factura_proveedor
            cursor.execute("PRAGMA table_info(old_factura_proveedor)")
            old_cols = [c[1] for c in cursor.fetchall()]
            
            # Columnas del nuevo esquema (en el mismo orden que pusimos arriba para estar seguros o especificar)
            target_cols = ['id', 'numero_factura', 'proveedor_id', 'nombre_proveedor', 'categoria_id', 'fecha_factura', 
                           'fecha_vencimiento', 'importe_sin_iva', 'iva', 'importe_total', 'descripcion', 
                           'estado', 'metodo_pago', 'notas', 'archivo_factura', 'fecha_registro']
            
            # Solo copiamos las que existan en la vieja
            copy_cols = [c for c in target_cols if c in old_cols]
            cols_str = ", ".join(copy_cols)
            
            print(f"Copiando columnas: {cols_str}")
            cursor.execute(f"INSERT INTO factura_proveedor ({cols_str}) SELECT {cols_str} FROM old_factura_proveedor")
            
            # 4. Limpieza
            cursor.execute("DROP TABLE old_factura_proveedor")
            
            conn.commit()
            conn.close()
            
            print()
            print("=" * 60)
            print("MIGRACION COMPLETADA CON ÉXITO")
            print("=" * 60)
            
        except Exception as e:
            print(f"Error crítico en migración: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

if __name__ == "__main__":
    migrate()
