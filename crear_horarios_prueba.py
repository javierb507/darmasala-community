"""
Script para crear horarios de prueba en el sistema
"""
from app import app, db, HorarioSemanal, Clase
from datetime import time

def crear_horarios_prueba():
    """Crea horarios de prueba para la semana"""
    with app.app_context():
        print("=" * 60)
        print("CREACION DE HORARIOS DE PRUEBA")
        print("=" * 60)
        print()

        # Verificar si ya existen horarios
        if HorarioSemanal.query.count() > 0:
            print(f"Ya existen {HorarioSemanal.query.count()} horarios en la base de datos.")
            respuesta = input("¿Deseas eliminar todos los horarios y crear nuevos? (s/n): ")
            if respuesta.lower() != 's':
                print("Operación cancelada.")
                return

            # Eliminar horarios existentes
            print("Eliminando horarios existentes...")
            HorarioSemanal.query.delete()
            db.session.commit()
            print("Horarios eliminados.")
            print()

        # Obtener las clases existentes
        yoga_integral = Clase.query.filter_by(nombre='Yoga integral').first()
        meditacion = Clase.query.filter_by(nombre='Meditación').first()
        yoga_menopausia = Clase.query.filter_by(nombre='Yoga menopausia').first()

        if not yoga_integral or not meditacion or not yoga_menopausia:
            print("ERROR: No se encontraron las clases necesarias.")
            print("Asegúrate de que existen las clases: Yoga integral, Meditación, Yoga menopausia")
            return

        horarios_creados = []

        # Lunes a Viernes: 10:00 - 11:15 Yoga Integral
        print("Creando horarios de Yoga Integral (10:00-11:15)...")
        for dia in range(5):  # 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes
            horario = HorarioSemanal(
                clase_id=yoga_integral.id,
                dia_semana=dia,
                hora_inicio=time(10, 0),
                hora_fin=time(11, 15),
                instructor='Minouche'
            )
            db.session.add(horario)
            horarios_creados.append(horario)

        # Lunes a Viernes: 18:30 - 19:15 Meditación
        print("Creando horarios de Meditación (18:30-19:15)...")
        for dia in range(5):
            horario = HorarioSemanal(
                clase_id=meditacion.id,
                dia_semana=dia,
                hora_inicio=time(18, 30),
                hora_fin=time(19, 15),
                instructor='Minouche'
            )
            db.session.add(horario)
            horarios_creados.append(horario)

        # Lunes a Viernes: 19:30 - 20:45 Yoga Integral
        print("Creando horarios de Yoga Integral (19:30-20:45)...")
        for dia in range(5):
            horario = HorarioSemanal(
                clase_id=yoga_integral.id,
                dia_semana=dia,
                hora_inicio=time(19, 30),
                hora_fin=time(20, 45),
                instructor='Minouche'
            )
            db.session.add(horario)
            horarios_creados.append(horario)

        # Lunes: 17:00 - 18:15 Yoga Menopausia
        print("Creando horario de Yoga Menopausia (Lunes 17:00-18:15)...")
        horario = HorarioSemanal(
            clase_id=yoga_menopausia.id,
            dia_semana=0,  # Lunes
            hora_inicio=time(17, 0),
            hora_fin=time(18, 15),
            instructor='Minouche'
        )
        db.session.add(horario)
        horarios_creados.append(horario)

        # Guardar todos los horarios
        db.session.commit()

        print()
        print("=" * 60)
        print("HORARIOS CREADOS EXITOSAMENTE")
        print("=" * 60)
        print()
        print(f"Total de horarios creados: {len(horarios_creados)}")
        print()
        print("RESUMEN POR DÍA:")
        print()

        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

        for dia_num in range(7):
            horarios_dia = HorarioSemanal.query.filter_by(dia_semana=dia_num).order_by(HorarioSemanal.hora_inicio).all()
            if horarios_dia:
                print(f"{dias_semana[dia_num]}:")
                for h in horarios_dia:
                    print(f"  - {h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}: {h.clase.nombre} ({h.instructor})")
                print()

        print("Accede a http://localhost:5000/horarios para ver el calendario")
        print()

if __name__ == "__main__":
    crear_horarios_prueba()
