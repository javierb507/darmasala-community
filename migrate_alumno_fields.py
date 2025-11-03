#!/usr/bin/env python3
"""
Script de migración para agregar nuevos campos al modelo Alumno
"""

import os
import sys
from sqlalchemy import text

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrar_campos_alumno():
    """Agregar nuevos campos a la tabla alumno"""
    print("🔄 Migrando campos del modelo Alumno...")
    
    with app.app_context():
        try:
            # Lista de nuevos campos a agregar
            nuevos_campos = [
                "ALTER TABLE alumno ADD COLUMN ciudad VARCHAR(100)",
                "ALTER TABLE alumno ADD COLUMN codigo_postal VARCHAR(10)",
                "ALTER TABLE alumno ADD COLUMN pais VARCHAR(50) DEFAULT 'España'",
                "ALTER TABLE alumno ADD COLUMN numero_cuenta VARCHAR(34)",
                "ALTER TABLE alumno ADD COLUMN medicamentos TEXT",
                "ALTER TABLE alumno ADD COLUMN alergias TEXT", 
                "ALTER TABLE alumno ADD COLUMN estado_fisico TEXT",
                "ALTER TABLE alumno ADD COLUMN motivacion TEXT"
            ]
            
            for campo in nuevos_campos:
                try:
                    db.session.execute(text(campo))
                    print(f"✅ Campo agregado: {campo.split('ADD COLUMN')[1].split()[0]}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"⚠️ Campo ya existe: {campo.split('ADD COLUMN')[1].split()[0]}")
                    else:
                        print(f"❌ Error agregando campo: {e}")
            
            db.session.commit()
            print("✅ Migración completada")
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    if migrar_campos_alumno():
        print("🎉 ¡Migración exitosa! Ahora puedes ejecutar testing_app.py")
    else:
        print("❌ Error en la migración")
