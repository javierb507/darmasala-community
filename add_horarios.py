"""
Script para añadir horarios recurrentes de clases
"""
from app import app, db, HorarioSemanal, Clase
from datetime import time

def add_horarios():
    """Añade los horarios recurrentes de clases"""
    with app.app_context():
        # Obtener las clases (los nombres están en minúsculas en la BD)
        yoga_integral = Clase.query.filter_by(nombre='Yoga integral').first()
        meditacion = Clase.query.filter_by(nombre='Meditación').first()
        yoga_menopausia = Clase.query.filter_by(nombre='Yoga menopausia').first()

        if not yoga_integral or not meditacion or not yoga_menopausia:
            print("ERROR: No se encontraron las clases necesarias")
            return

        # Limpiar horarios existentes
        HorarioSemanal.query.delete()
        db.session.commit()
        print("Horarios anteriores eliminados")

        horarios_creados = 0

        # Lunes a Viernes: Yoga Integral 10:00 - 11:30
        for dia in range(0, 5):  # 0=Lunes, 4=Viernes
            horario = HorarioSemanal(
                clase_id=yoga_integral.id,
                dia_semana=dia,
                hora_inicio=time(10, 0),
                hora_fin=time(11, 30),
                instructor='Minouche',
                activo=True
            )
            db.session.add(horario)
            horarios_creados += 1

        # Lunes a Viernes: Meditación 18:30 - 19:15
        for dia in range(0, 5):  # 0=Lunes, 4=Viernes
            horario = HorarioSemanal(
                clase_id=meditacion.id,
                dia_semana=dia,
                hora_inicio=time(18, 30),
                hora_fin=time(19, 15),
                instructor='Minouche',
                activo=True
            )
            db.session.add(horario)
            horarios_creados += 1

        # Lunes a Viernes: Yoga Integral 19:30 - 20:45
        for dia in range(0, 5):  # 0=Lunes, 4=Viernes
            horario = HorarioSemanal(
                clase_id=yoga_integral.id,
                dia_semana=dia,
                hora_inicio=time(19, 30),
                hora_fin=time(20, 45),
                instructor='Minouche',
                activo=True
            )
            db.session.add(horario)
            horarios_creados += 1

        # Lunes: Yoga Menopausia 17:00 - 18:15
        horario = HorarioSemanal(
            clase_id=yoga_menopausia.id,
            dia_semana=0,  # Lunes
            hora_inicio=time(17, 0),
            hora_fin=time(18, 15),
            instructor='Minouche',
            activo=True
        )
        db.session.add(horario)
        horarios_creados += 1

        db.session.commit()
        print(f"\nOK - {horarios_creados} horarios creados exitosamente:")
        print("\nLunes a Viernes:")
        print("  - Yoga Integral: 10:00 - 11:30")
        print("  - Meditacion: 18:30 - 19:15")
        print("  - Yoga Integral: 19:30 - 20:45")
        print("\nLunes:")
        print("  - Yoga Menopausia: 17:00 - 18:15")

if __name__ == "__main__":
    print("=" * 60)
    print("AÑADIENDO HORARIOS RECURRENTES")
    print("=" * 60)
    print()

    add_horarios()

    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
