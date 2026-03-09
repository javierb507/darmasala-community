import os
import sqlite3
from app import app, db

def migrate():
    """Migración para refactorizar la tabla factura_proveedor
    - Añadir columna nombre_proveedor
    - Hacer proveedor_id nullable
    """
    with app.app_context():
        print("=" * 60)
        print("MIGRACION: Refactorizar factura_proveedor (Añadir nombre y quitar NOT NULL)")
        print("=" * 60)
        
        # Path local a la base de datos
        db_path = os.path.join(app.instance_path, 'yoga_school.db')
        
        try:
            # Conexión directa con sqlite3 para manejar la migración compleja
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. Verificar si la columna nombre_proveedor ya existe
            cursor.execute("PRAGMA table_info(factura_proveedor)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'nombre_proveedor' not in columns:
                print("Añadiendo columna 'nombre_proveedor' a 'factura_proveedor'...")
                cursor.execute("ALTER TABLE factura_proveedor ADD COLUMN nombre_proveedor VARCHAR(100)")
            else:
                print("La columna 'nombre_proveedor' ya existe.")
            
            # 2. Hacer proveedor_id nullable (SQLite requiere recrear la tabla)
            # Primero comprobamos si es ya nullable
            cursor.execute("PRAGMA table_info(factura_proveedor)")
            col_info = cursor.fetchall()
            target_col = [c for c in col_info if c[1] == 'proveedor_id'][0]
            is_nullable = (target_col[3] == 0) # 3 is not_null flag
            
            if not is_nullable:
                print("Transformando 'proveedor_id' en nullable (recreando tabla)...")
                
                # Obtener definición actual
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='factura_proveedor'")
                old_create_sql = cursor.fetchone()[0]
                
                # Crear tabla temporal con el nuevo esquema
                # Simplemente quitamos "NOT NULL" del campo proveedor_id en el SQL original si es posible,
                # pero es más seguro definirla bien.
                
                cursor.execute("ALTER TABLE factura_proveedor RENAME TO old_factura_proveedor")
                
                # El nuevo esquema basado en los modelos actuales
                cursor.execute("""
                CREATE TABLE factura_proveedor (
                    id INTEGER NOT NULL, 
                    numero_factura VARCHAR(50), 
                    proveedor_id INTEGER, 
                    categoria_id INTEGER, 
                    fecha_emision DATE NOT NULL, 
                    base_imponible FLOAT NOT NULL, 
                    iva FLOAT, 
                    importe_total FLOAT NOT NULL, 
                    descripcion TEXT, 
                    estado VARCHAR(20), 
                    metodo_pago VARCHAR(50), 
                    notas TEXT, 
                    archivo_factura VARCHAR(200), 
                    fecha_registro DATETIME, 
                    nombre_proveedor VARCHAR(100),
                    PRIMARY KEY (id), 
                    FOREIGN KEY(proveedor_id) REFERENCES proveedor (id), 
                    FOREIGN KEY(categoria_id) REFERENCES categoria_gasto (id)
                )
                """)
                
                # Copiar datos
                # Mapeamos las columnas existentes
                cursor.execute("PRAGMA table_info(old_factura_proveedor)")
                old_cols = [c[1] for c in cursor.fetchall()]
                common_cols = [c for c in old_cols if c in ['id', 'numero_factura', 'proveedor_id', 'categoria_id', 'fecha_emision', 'base_imponible', 'iva', 'importe_total', 'descripcion', 'estado', 'metodo_pago', 'notas', 'archivo_factura', 'fecha_registro', 'nombre_proveedor']]
                cols_str = ", ".join(common_cols)
                
                cursor.execute(f"INSERT INTO factura_proveedor ({cols_str}) SELECT {cols_str} FROM old_factura_proveedor")
                
                cursor.execute("DROP TABLE old_factura_proveedor")
                print("Tabla recreada exitosamente.")
            else:
                print("'proveedor_id' ya es nullable.")

            conn.commit()
            conn.close()
            
            print()
            print("=" * 60)
            print("MIGRACION COMPLETADA")
            print("=" * 60)
            
        except Exception as e:
            print(f"Error crítico en migración: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

if __name__ == "__main__":
    migrate()
