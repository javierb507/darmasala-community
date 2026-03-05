from app import app, Asistencia, Alumno, HorarioSemanal
from datetime import date

with app.app_context():
    # Get any student
    alumno = Alumno.query.first()
    if not alumno:
        print("No pupils found.")
    else:
        print(f"Checking pupil: {alumno.nombre} {alumno.apellido} (ID: {alumno.id})")
        asistencias = Asistencia.query.filter_by(alumno_id=alumno.id).all()
        print(f"Total attendance records found for this student: {len(asistencias)}")
        for a in asistencias:
            clase_nombre = a.horario.clase.nombre if a.horario else (a.evento.titulo if a.evento else "Unknown")
            print(f"- Date: {a.fecha_clase}, Class: {clase_nombre}, Present: {a.presente}")

    print("\nTotal attendance records in DB:")
    all_asistencias = Asistencia.query.all()
    print(f"Total: {len(all_asistencias)}")
    for a in all_asistencias[:10]:
        print(f"- Student ID: {a.alumno_id}, Date: {a.fecha_clase}, Present: {a.presente}")
