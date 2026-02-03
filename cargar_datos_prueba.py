#!/usr/bin/env python3
"""
Script para cargar datos de prueba en la aplicación
"""

import os
import random
from datetime import datetime, timedelta, date, time
from app import app, db
from app import Alumno, Pago, SesionYogaterapia, HorarioSemanal, Clase, Usuario
from werkzeug.security import generate_password_hash

def cargar_datos_prueba():
    """Cargar datos de prueba completos"""
    print("🔄 Cargando datos de prueba...")
    
    with app.app_context():
        # Limpiar datos existentes
        print("🗑️ Limpiando datos existentes...")
        db.drop_all()
        db.create_all()
        
        # Crear clases
        print("📚 Creando clases...")
        clases_data = [
            {'nombre': 'Yoga menopausia', 'descripcion': 'Clase especializada para mujeres en etapa de menopausia', 'precio': 15.00, 'duracion_minutos': 60, 'color': '#FF6B6B'},
            {'nombre': 'Yoga integral', 'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación', 'precio': 15.00, 'duracion_minutos': 60, 'color': '#4ECDC4'},
            {'nombre': 'Yoga embarazadas', 'descripcion': 'Yoga adaptado para mujeres embarazadas', 'precio': 15.00, 'duracion_minutos': 60, 'color': '#45B7D1'},
            {'nombre': 'Meditación', 'descripcion': 'Práctica de meditación y mindfulness', 'precio': 12.00, 'duracion_minutos': 45, 'color': '#96CEB4'},
            {'nombre': 'Yogaterapia', 'descripcion': 'Sesión individual de yogaterapia personalizada', 'precio': 45.00, 'duracion_minutos': 60, 'color': '#FFEAA7'},
            {'nombre': 'Hatha Yoga', 'descripcion': 'Yoga clásico con posturas estáticas', 'precio': 15.00, 'duracion_minutos': 75, 'color': '#DDA0DD'},
            {'nombre': 'Vinyasa Flow', 'descripcion': 'Yoga dinámico con transiciones fluidas', 'precio': 18.00, 'duracion_minutos': 75, 'color': '#98D8C8'},
            {'nombre': 'Yin Yoga', 'descripcion': 'Yoga restaurativo con posturas largas', 'precio': 16.00, 'duracion_minutos': 90, 'color': '#F7DC6F'}
        ]
        
        clases = []
        for clase_data in clases_data:
            clase = Clase(
                nombre=clase_data['nombre'],
                descripcion=clase_data['descripcion'],
                precio=clase_data['precio'],
                duracion_minutos=clase_data['duracion_minutos'],
                color=clase_data['color'],
                nivel='intermedio',
                capacidad_maxima=15,
                activa=True
            )
            db.session.add(clase)
            clases.append(clase)
        
        # Guardar clases primero
        db.session.commit()
        
        # Crear instructores
        print("👨‍🏫 Creando instructores...")
        instructores_data = [
            {'nombre': 'Minouche', 'especialidad': 'Yoga Integral y Yogaterapia'},
            {'nombre': 'Elena', 'especialidad': 'Hatha Yoga y Meditación'},
            {'nombre': 'Carlos', 'especialidad': 'Vinyasa Flow y Ashtanga'}
        ]
        
        from app import Instructor
        instructores = []
        for inst_data in instructores_data:
            inst = Instructor(
                nombre=inst_data['nombre'],
                especialidad=inst_data['especialidad'],
                email=f"{inst_data['nombre'].lower()}@atmasuddhi.es",
                activo=True
            )
            db.session.add(inst)
            instructores.append(inst)
        
        db.session.commit()
        
        # Crear horarios semanales
        print("⏰ Creando horarios semanales...")
        horarios_data = [
            # Lunes
            {'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '10:15', 'clase': 'Hatha Yoga', 'instructor': 'Elena'},
            {'dia_semana': 0, 'hora_inicio': '10:30', 'hora_fin': '11:45', 'clase': 'Yoga menopausia', 'instructor': 'Minouche'},
            {'dia_semana': 0, 'hora_inicio': '18:00', 'hora_fin': '19:15', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            {'dia_semana': 0, 'hora_inicio': '19:30', 'hora_fin': '20:45', 'clase': 'Vinyasa Flow', 'instructor': 'Carlos'},
            
            # Martes
            {'dia_semana': 1, 'hora_inicio': '09:00', 'hora_fin': '10:00', 'clase': 'Yoga embarazadas', 'instructor': 'Minouche'},
            {'dia_semana': 1, 'hora_inicio': '10:15', 'hora_fin': '11:00', 'clase': 'Meditación', 'instructor': 'Elena'},
            {'dia_semana': 1, 'hora_inicio': '18:00', 'hora_fin': '19:15', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            {'dia_semana': 1, 'hora_inicio': '19:30', 'hora_fin': '21:00', 'clase': 'Yin Yoga', 'instructor': 'Elena'},
            
            # Miércoles
            {'dia_semana': 2, 'hora_inicio': '09:00', 'hora_fin': '10:15', 'clase': 'Hatha Yoga', 'instructor': 'Elena'},
            {'dia_semana': 2, 'hora_inicio': '10:30', 'hora_fin': '11:45', 'clase': 'Yoga menopausia', 'instructor': 'Minouche'},
            {'dia_semana': 2, 'hora_inicio': '18:00', 'hora_fin': '19:15', 'clase': 'Vinyasa Flow', 'instructor': 'Carlos'},
            {'dia_semana': 2, 'hora_inicio': '19:30', 'hora_fin': '20:45', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            
            # Jueves
            {'dia_semana': 3, 'hora_inicio': '09:00', 'hora_fin': '10:00', 'clase': 'Yoga embarazadas', 'instructor': 'Minouche'},
            {'dia_semana': 3, 'hora_inicio': '10:15', 'hora_fin': '11:00', 'clase': 'Meditación', 'instructor': 'Elena'},
            {'dia_semana': 3, 'hora_inicio': '18:00', 'hora_fin': '19:15', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            {'dia_semana': 3, 'hora_inicio': '19:30', 'hora_fin': '21:00', 'clase': 'Yin Yoga', 'instructor': 'Elena'},
            
            # Viernes
            {'dia_semana': 4, 'hora_inicio': '09:00', 'hora_fin': '10:15', 'clase': 'Hatha Yoga', 'instructor': 'Elena'},
            {'dia_semana': 4, 'hora_inicio': '10:30', 'hora_fin': '11:45', 'clase': 'Vinyasa Flow', 'instructor': 'Carlos'},
            {'dia_semana': 4, 'hora_inicio': '18:00', 'hora_fin': '19:15', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            {'dia_semana': 4, 'hora_inicio': '19:30', 'hora_fin': '20:45', 'clase': 'Yoga menopausia', 'instructor': 'Minouche'},
            
            # Sábado
            {'dia_semana': 5, 'hora_inicio': '10:00', 'hora_fin': '11:15', 'clase': 'Yoga integral', 'instructor': 'Minouche'},
            {'dia_semana': 5, 'hora_inicio': '11:30', 'hora_fin': '12:45', 'clase': 'Vinyasa Flow', 'instructor': 'Carlos'},
            {'dia_semana': 5, 'hora_inicio': '17:00', 'hora_fin': '18:30', 'clase': 'Yin Yoga', 'instructor': 'Elena'}
        ]
        
        for horario_data in horarios_data:
            clase = next((c for c in clases if c.nombre == horario_data['clase']), None)
            if clase:
                horario = HorarioSemanal(
                    clase_id=clase.id,
                    dia_semana=horario_data['dia_semana'],
                    hora_inicio=datetime.strptime(horario_data['hora_inicio'], '%H:%M').time(),
                    hora_fin=datetime.strptime(horario_data['hora_fin'], '%H:%M').time(),
                    instructor=horario_data.get('instructor', 'Minouche'),
                    activo=True
                )
                db.session.add(horario)
        
        # Crear alumnos
        print("👥 Creando alumnos...")
        nombres = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Patricia', 'Sofia', 'Elena', 'Cristina', 'Mónica']
        apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín']
        
        alumnos = []
        for i in range(15):
            alumno = Alumno(
                nombre=random.choice(nombres),
                apellido=random.choice(apellidos),
                email=f"alumno{i+1}@email.com",
                telefono=f"6{random.randint(10000000, 99999999)}",
                fecha_nacimiento=date(1970 + random.randint(20, 50), random.randint(1, 12), random.randint(1, 28)),
                tipo_cuota=random.choice(['clase_suelta', '1_semanal', '2_semanal', 'plana']),
                activo=True,
                fecha_matricula=date.today() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(alumno)
            alumnos.append(alumno)
        
        # Guardar alumnos
        db.session.commit()
        
        # Crear pagos
        print("💰 Creando pagos...")
        for alumno in alumnos:
            # Crear pagos de los últimos 3 meses
            for mes_offset in range(3):
                fecha_pago = date.today() - timedelta(days=30 * mes_offset)
                monto = random.choice([15, 40, 70, 90])
                metodo = random.choice(['efectivo', 'tarjeta', 'transferencia', 'bizum'])
                
                pago = Pago(
                    alumno_id=alumno.id,
                    fecha_clase=fecha_pago,
                    monto=monto,
                    metodo_pago=metodo,
                    descripcion=f'Pago {alumno.tipo_cuota}',
                    tipo_pago='cuota'
                )
                db.session.add(pago)
        
        # Crear sesiones de yogaterapia
        print("🧘 Creando sesiones de yogaterapia...")
        nombres_personas = [
            'Ana García', 'María López', 'Carmen Ruiz', 'Isabel Martín', 'Laura Sánchez',
            'Patricia Gómez', 'Sofia Pérez', 'Elena Fernández', 'Cristina Díaz', 'Mónica Torres',
            'Javier Rodríguez', 'Carlos García', 'Miguel López', 'Antonio Ruiz', 'David Martín'
        ]
        
        for i in range(20):
            fecha_sesion = date.today() - timedelta(days=random.randint(0, 60))
            # Seleccionar un alumno aleatorio
            alumno = random.choice(alumnos)
            
            sesion = SesionYogaterapia(
                alumno_id=alumno.id,
                fecha_sesion=fecha_sesion,
                hora_inicio=datetime.strptime(f"{random.randint(9, 18):02d}:{random.choice(['00', '15', '30', '45'])}", '%H:%M').time(),
                hora_fin=datetime.strptime(f"{random.randint(10, 19):02d}:{random.choice(['00', '15', '30', '45'])}", '%H:%M').time(),
                duracion_minutos=random.choice([45, 60, 75, 90]),
                tipo_sesion='individual',
                motivo_consulta=f'Consulta {i+1}: Dolor de espalda, estrés, flexibilidad',
                objetivos_terapeuticos=f'Objetivos {i+1}: Mejorar postura, reducir estrés, aumentar flexibilidad',
                tecnicas_aplicadas=f'Técnicas {i+1}: Asanas, pranayama, relajación',
                posturas_trabajadas=f'Posturas {i+1}: Tadasana, Uttanasana, Adho Mukha Svanasana',
                respiracion_pranayama=f'Respiración {i+1}: Ujjayi, Nadi Shodhana',
                meditacion_relajacion=f'Meditación {i+1}: Mindfulness, relajación progresiva',
                estado_inicial=f'Estado inicial {i+1}: Tensión, rigidez, ansiedad',
                respuesta_sesion=f'Respuesta {i+1}: Relajación, mejora de movilidad',
                estado_final=f'Estado final {i+1}: Más relajado, flexible, centrado',
                observaciones_terapeuta=f'Observaciones {i+1}: Buena respuesta, continuar tratamiento',
                recomendaciones_casa=f'Recomendaciones {i+1}: Practicar 10 min diarios',
                proxima_sesion=f'Próxima sesión {i+1}: En una semana',
                instructor='Minouche',
                precio=45.00,
                pagado=random.choice([True, False]),
                metodo_pago=random.choice(['efectivo', 'tarjeta', 'transferencia']) if random.choice([True, False]) else None
            )
            db.session.add(sesion)
        
        # Crear usuario administrador
        print("👤 Creando usuario administrador...")
        import hashlib
        admin = Usuario(
            username='admin',
            email='admin@atmasuddhi.es',
            password_hash=generate_password_hash('AtmaSuddhi74'),
            nombre='Administrador',
            apellido='Sistema',
            rol='admin'
        )
        db.session.add(admin)
        
        # Guardar todo
        db.session.commit()
        print("✅ Datos de prueba cargados exitosamente!")
        
        # Mostrar estadísticas
        print(f"\n📊 Estadísticas:")
        print(f"   👥 Alumnos: {Alumno.query.count()}")
        print(f"   📚 Clases: {Clase.query.count()}")
        print(f"   ⏰ Horarios: {HorarioSemanal.query.count()}")
        print(f"   🧘 Sesiones de yogaterapia: {SesionYogaterapia.query.count()}")
        print(f"   💰 Pagos: {Pago.query.count()}")
        print(f"   👤 Usuarios: {Usuario.query.count()}")

if __name__ == '__main__':
    cargar_datos_prueba()
