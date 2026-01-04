"""
Script para generar datos de prueba de asistencias desde octubre 2025
"""
from app import app, db, Alumno, HorarioSemanal, Asistencia
from datetime import date, timedelta
import random

def generate_test_asistencias():
    """Genera asistencias de prueba desde octubre 2025 hasta hoy"""
    with app.app_context():
        # Obtener todos los alumnos activos
        alumnos = Alumno.query.filter_by(activo=True).all()
        if not alumnos:
            print("ERROR: No hay alumnos activos en la base de datos")
            return

        # Obtener todos los horarios recurrentes
        horarios = HorarioSemanal.query.filter_by(activo=True).all()
        if not horarios:
            print("ERROR: No hay horarios configurados")
            return

        print(f"Generando asistencias para {len(alumnos)} alumnos")
        print(f"Horarios disponibles: {len(horarios)}")

        # Limpiar asistencias existentes
        Asistencia.query.delete()
        db.session.commit()
        print("Asistencias anteriores eliminadas")

        # Fecha de inicio: 1 de octubre de 2025
        fecha_inicio = date(2025, 10, 1)
        fecha_fin = date.today()

        asistencias_creadas = 0
        current_date = fecha_inicio

        # Asignar a cada alumno sus horarios preferidos (1-3 clases por semana)
        alumnos_horarios = {}
        for alumno in alumnos:
            # Cada alumno asiste a 1-3 horarios diferentes de forma recurrente
            num_horarios = random.randint(1, min(3, len(horarios)))
            horarios_alumno = random.sample(horarios, num_horarios)
            alumnos_horarios[alumno.id] = horarios_alumno

        # Generar asistencias día por día
        while current_date <= fecha_fin:
            dia_semana = current_date.weekday()

            # Obtener horarios de este día de la semana
            horarios_del_dia = [h for h in horarios if h.dia_semana == dia_semana]

            for horario in horarios_del_dia:
                # Obtener alumnos que asisten a este horario
                alumnos_horario = [
                    alumno for alumno in alumnos
                    if horario in alumnos_horarios.get(alumno.id, [])
                ]

                for alumno in alumnos_horario:
                    # 85% de probabilidad de asistir (realista)
                    presente = random.random() < 0.85

                    # Crear asistencia
                    asistencia = Asistencia(
                        alumno_id=alumno.id,
                        horario_id=horario.id,
                        fecha_clase=current_date,
                        presente=presente,
                        observaciones=None if presente else random.choice([
                            None, None, None,  # La mayoría sin observaciones
                            'Enfermedad',
                            'Trabajo',
                            'Viaje',
                            'Asuntos personales'
                        ])
                    )
                    db.session.add(asistencia)
                    asistencias_creadas += 1

                    # Commit cada 100 registros para mejor rendimiento
                    if asistencias_creadas % 100 == 0:
                        db.session.commit()
                        print(f"  Procesadas {asistencias_creadas} asistencias...")

            current_date += timedelta(days=1)

        # Commit final
        db.session.commit()

        # Estadísticas
        total_dias = (fecha_fin - fecha_inicio).days + 1
        print(f"\n{'='*60}")
        print(f"OK - {asistencias_creadas} asistencias creadas exitosamente")
        print(f"{'='*60}")
        print(f"\nPeríodo: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
        print(f"Total días: {total_dias}")
        print(f"Alumnos: {len(alumnos)}")
        print(f"Horarios: {len(horarios)}")

        # Calcular estadísticas de asistencia
        total_asistencias = Asistencia.query.count()
        presentes = Asistencia.query.filter_by(presente=True).count()
        porcentaje = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0

        print(f"\nEstadísticas:")
        print(f"  Total registros: {total_asistencias}")
        print(f"  Presentes: {presentes}")
        print(f"  Ausentes: {total_asistencias - presentes}")
        print(f"  Tasa de asistencia: {porcentaje:.1f}%")

if __name__ == "__main__":
    print("=" * 60)
    print("GENERACIÓN DE DATOS DE PRUEBA - ASISTENCIAS")
    print("=" * 60)
    print()

    generate_test_asistencias()

    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
