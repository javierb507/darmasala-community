import sqlite3
import os

db_path = 'instance/yoga_school.db'

if not os.path.exists(db_path):
    print(f"Error: No se encontró la base de datos en {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("🚀 Iniciando migración de ClaseOnline...")
    
    # 1. Leer datos existentes de la tabla antigua si existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clase_online'")
    if cursor.fetchone():
        print("📦 Backup de datos existentes...")
        cursor.execute("SELECT id, fecha, url_youtube, titulo, descripcion, activo, fecha_registro FROM clase_online")
        rows = cursor.fetchall()
        
        # 2. Renombrar tabla antigua
        cursor.execute("ALTER TABLE clase_online RENAME TO clase_online_old")
    else:
        rows = []
        print("ℹ️ La tabla clase_online no existe, se creará de cero.")

    # 3. Crear nueva tabla con el nuevo esquema
    cursor.execute("""
    CREATE TABLE clase_online (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE,
        url_youtube VARCHAR(500) NOT NULL,
        titulo VARCHAR(200),
        descripcion TEXT,
        activo BOOLEAN DEFAULT 1,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("✅ Nueva tabla clase_online creada.")

    # 4. Insertar datos antiguos si los hay
    if rows:
        print(f"🔄 Migrando {len(rows)} registros...")
        for row in rows:
            # Mapeamos 'fecha' antigua a 'fecha_inicio'
            cursor.execute("""
            INSERT INTO clase_online (id, fecha_inicio, url_youtube, titulo, descripcion, activo, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row)
        
        # 5. Eliminar tabla temporal
        cursor.execute("DROP TABLE clase_online_old")
        print("✅ Datos migrados correctamente.")

    conn.commit()
    print("🎉 Migración completada con éxito.")

except Exception as e:
    conn.rollback()
    print(f"❌ Error durante la migración: {e}")
finally:
    conn.close()
