#!/usr/bin/env python3
"""
Script para actualizar el esquema de la base de datos sin borrar los datos existentes.
Añade las columnas faltantes en la tabla 'clase'.
"""
import sqlite3
import os
from app import app

def actualizar_esquema():
    # Intentar localizar la base de datos
    db_paths = [
        os.path.join(app.root_path, 'instance', 'yoga_school.db'),
        os.path.join(app.root_path, 'yoga_school.db'),
        'yoga_school.db',
        'instance/yoga_school.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
            
    if not db_path:
        print("❌ No se encontró el archivo de base de datos.")
        return

    print(f"📦 Usando base de datos: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Columnas a añadir a la tabla 'clase'
    nuevas_columnas = [
        ('instructor', 'TEXT DEFAULT "Minouche"'),
        ('periodicidad', 'TEXT DEFAULT "semanal"'),
        ('duracion_minutos', 'INTEGER DEFAULT 75'),
        ('nivel', 'TEXT DEFAULT "todos"'),
        ('capacidad_maxima', 'INTEGER DEFAULT 15')
    ]

    for col_nombre, col_tipo in nuevas_columnas:
        try:
            print(f" tentando añadir columna '{col_nombre}' a 'clase'...")
            cursor.execute(f"ALTER TABLE clase ADD COLUMN {col_nombre} {col_tipo}")
            print(f"✅ Columna '{col_nombre}' añadida.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"ℹ️ La columna '{col_nombre}' ya existe.")
            else:
                print(f"⚠️ Error al añadir '{col_nombre}': {e}")

    # Verificar si necesitamos crear la tabla 'instructor' (que es nueva)
    try:
        cursor.execute("SELECT id FROM instructor LIMIT 1")
        print("ℹ️ La tabla 'instructor' ya existe.")
    except sqlite3.OperationalError:
        print("🔨 La tabla 'instructor' no existe. Ejecutando inicialización completa...")
        conn.close()
        from app import db
        with app.app_context():
            db.create_all()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

    conn.commit()
    conn.close()
    print("✨ Proceso de actualización de esquema finalizado.")

if __name__ == "__main__":
    actualizar_esquema()
