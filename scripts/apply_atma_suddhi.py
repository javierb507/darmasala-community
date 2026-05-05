import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = 'yoga_school.db'

def setup_atma_suddhi():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró {DB_PATH}. Ejecuta la app al menos una vez para crear la DB.")
        return

    configs = [
        ('nombre_escuela', 'ATMA SUDDHI', 'Nombre de la escuela'),
        ('web_escuela', 'http://atmasuddhi.es', 'Página web'),
        ('nombre_instructora', 'Minouche', 'Nombre de la instructora principal'),
        ('precio_clase_suelta', '15.00', 'Precio por clase suelta'),
        ('precio_1_clase_semanal', '40.00', 'Precio 1 clase por semana'),
        ('precio_2_clases_semanal', '70.00', 'Precio 2 clases por semana'),
        ('precio_tarifa_plana', '90.00', 'Precio tarifa plana'),
        ('precio_matricula', '25.00', 'Precio de matrícula anual'),
        ('precio_yogaterapia_individual', '50.00', 'Precio yogaterapia individual')
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for clave, valor, desc in configs:
            cursor.execute("SELECT id FROM configuracion WHERE clave = ?", (clave,))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE configuracion SET valor = ?, descripcion = ?, fecha_actualizacion = ? WHERE clave = ?",
                    (valor, desc, datetime.utcnow().isoformat(), clave)
                )
            else:
                cursor.execute(
                    "INSERT INTO configuracion (clave, valor, descripcion, fecha_actualizacion) VALUES (?, ?, ?, ?)",
                    (clave, valor, desc, datetime.utcnow().isoformat())
                )
        
        conn.commit()
        print("✅ Personalización de DarmaSala aplicada correctamente.")
    except Exception as e:
        print(f"❌ Error al aplicar personalización: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_atma_suddhi()
