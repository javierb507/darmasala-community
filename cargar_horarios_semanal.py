#!/usr/bin/env python3
"""
Script para cargar horarios semanales específicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, HorarioSemanal, Clase
from datetime import time

def cargar_horarios_semanal():
    """Cargar horarios semanales específicos"""
    print("🔄 Cargando horarios semanales específicos...")
    
    with app.app_context():
        # Limpiar horarios existentes
        print("🗑️ Limpiando horarios existentes...")
        HorarioSemanal.query.delete()
        db.session.commit()
        
        # Obtener clases
        clases = {clase.nombre: clase for clase in Clase.query.all()}
        
        # Definir horarios por día
        horarios_data = {
            'Lunes': [
                ('08:00', 'Yoga'),
                ('10:00', 'Yoga'),
                ('11:30', 'Yoga'),
                ('12:45', 'Yoga'),
                ('17:00', 'Yoga'),
                ('18:30', 'Yoga Prenatal'),
                ('19:30', 'Meditación'),
                ('20:45', 'Meditación Corta')
            ],
            'Martes': [
                ('10:00', 'Yoga'),
                ('11:30', 'Yoga'),
                ('12:45', 'Meditación'),
                ('17:00', 'Yoga Menopausia'),
                ('18:30', 'Yoga'),
                ('19:30', 'Meditación'),
                ('20:45', 'Meditación Corta')
            ],
            'Miércoles': [
                ('08:00', 'Yoga'),
                ('10:00', 'Yoga'),
                ('11:30', 'Yoga'),
                ('12:45', 'Yoga'),
                ('17:00', 'Yoga'),
                ('18:30', 'Yoga Prenatal'),
                ('19:30', 'Meditación'),
                ('20:45', 'Meditación Corta')
            ],
            'Jueves': [
                ('10:00', 'Yoga'),
                ('11:30', 'Yoga'),
                ('12:45', 'Meditación'),
                ('17:00', 'Yoga Menopausia'),
                ('18:30', 'Yoga'),
                ('19:30', 'Meditación'),
                ('20:45', 'Meditación Corta')
            ],
            'Viernes': [
                ('08:00', 'Yoga'),
                ('10:00', 'Yoga'),
                ('11:30', 'Yoga'),
                ('12:45', 'Yoga'),
                ('17:00', 'Yoga'),
                ('18:30', 'Yoga'),
                ('19:30', 'Meditación'),
                ('20:45', 'Meditación Corta')
            ],
            'Sábado': [
                ('10:00', 'Yoga')
            ]
        }
        
        # Mapeo de días de la semana
        dias_semana = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 
            'Viernes': 4, 'Sábado': 5, 'Domingo': 6
        }
        
        horarios_creados = 0
        
        for dia_nombre, clases_dia in horarios_data.items():
            dia_semana = dias_semana[dia_nombre]
            
            for hora_str, nombre_clase in clases_dia:
                # Buscar la clase
                clase = None
                for clase_nombre, clase_obj in clases.items():
                    if nombre_clase.lower() in clase_nombre.lower() or clase_nombre.lower() in nombre_clase.lower():
                        clase = clase_obj
                        break
                
                if not clase:
                    print(f"⚠️ Clase no encontrada: {nombre_clase}")
                    continue
                
                # Convertir hora string a time object
                hora_parts = hora_str.split(':')
                hora_time = time(int(hora_parts[0]), int(hora_parts[1]))
                
                # Crear horario
                horario = HorarioSemanal(
                    dia_semana=dia_semana,
                    hora_inicio=hora_time,
                    hora_fin=time(hora_time.hour + 1, hora_time.minute),  # 1 hora de duración
                    clase_id=clase.id,
                    activo=True
                )
                
                db.session.add(horario)
                horarios_creados += 1
                print(f"✅ {dia_nombre} {hora_str} - {nombre_clase}")
        
        db.session.commit()
        print(f"🎉 Horarios semanales cargados exitosamente! ({horarios_creados} horarios)")

if __name__ == '__main__':
    cargar_horarios_semanal()
