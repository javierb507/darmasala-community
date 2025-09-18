#!/usr/bin/env python3
"""
Script para inicializar la aplicación desde cero
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🧘‍♀️ INICIALIZANDO ATMA SUDDHI")
    print("=" * 50)
    
    # Eliminar base de datos existente
    if os.path.exists('yoga_school.db'):
        os.remove('yoga_school.db')
        print("🗑️ Base de datos anterior eliminada")
    
    # Importar la aplicación
    from app import app, db, Alumno, Pago, Clase, HorarioSemanal, Asistencia, GastoMensual, CategoriaGasto
    from datetime import date, datetime, time, timedelta
    import random
    
    with app.app_context():
        print("🏗️ Creando todas las tablas...")
        db.create_all()
        
        print("📂 Inicializando categorías de gastos...")
        # Crear categorías de gastos básicas
        categorias = [
            {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'color': '#dc3545'},
            {'nombre': 'Suministros', 'descripcion': 'Luz, agua, gas, internet', 'color': '#ffc107'},
            {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, etc.', 'color': '#28a745'},
            {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción', 'color': '#007bff'},
            {'nombre': 'Formación', 'descripcion': 'Cursos y formación', 'color': '#6f42c1'},
            {'nombre': 'Seguros', 'descripcion': 'Seguros varios', 'color': '#fd7e14'},
            {'nombre': 'Mantenimiento', 'descripcion': 'Reparaciones y mantenimiento', 'color': '#20c997'},
            {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'color': '#6c757d'}
        ]
        
        for cat_data in categorias:
            # Verificar si ya existe
            categoria_existente = CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria_existente:
                categoria = CategoriaGasto(**cat_data)
                db.session.add(categoria)
        
        print("📚 Creando clases básicas...")
        # Crear clases básicas
        clases_data = [
            {
                'nombre': 'Yoga integral',
                'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación',
                'precio_clase_suelta': 15.00,
                'precio_1_semanal': 40.00,
                'precio_2_semanal': 70.00,
                'precio_plana': 90.00,
                'precio_1_bimensual': 75.00,
                'precio_2_bimensual': 135.00,
                'color': '#007bff',
                'nivel': 'todos',
                'duracion_minutos': 75,
                'capacidad_maxima': 15
            },
            {
                'nombre': 'Yoga menopausia',
                'descripcion': 'Clase especializada para mujeres en etapa de menopausia',
                'precio_clase_suelta': 15.00,
                'precio_1_semanal': 40.00,
                'precio_2_semanal': 70.00,
                'precio_plana': 90.00,
                'precio_1_bimensual': 75.00,
                'precio_2_bimensual': 135.00,
                'color': '#e91e63',
                'nivel': 'todos',
                'duracion_minutos': 75,
                'capacidad_maxima': 12
            },
            {
                'nombre': 'Yoga embarazadas',
                'descripcion': 'Yoga adaptado para mujeres embarazadas',
                'precio_clase_suelta': 15.00,
                'precio_1_semanal': 40.00,
                'precio_2_semanal': 70.00,
                'precio_plana': 90.00,
                'precio_1_bimensual': 75.00,
                'precio_2_bimensual': 135.00,
                'color': '#ff9800',
                'nivel': 'principiante',
                'duracion_minutos': 60,
                'capacidad_maxima': 8
            },
            {
                'nombre': 'Meditación',
                'descripcion': 'Práctica de meditación y mindfulness',
                'precio_clase_suelta': 12.00,
                'precio_1_semanal': 35.00,
                'precio_2_semanal': 60.00,
                'precio_plana': 80.00,
                'precio_1_bimensual': 65.00,
                'precio_2_bimensual': 115.00,
                'color': '#9c27b0',
                'nivel': 'todos',
                'duracion_minutos': 45,
                'capacidad_maxima': 20
            }
        ]
        
        for clase_data in clases_data:
            # Verificar si ya existe
            clase_existente = Clase.query.filter_by(nombre=clase_data['nombre']).first()
            if not clase_existente:
                clase = Clase(**clase_data)
                db.session.add(clase)
        
        db.session.commit()
        
        print("👥 Creando alumnos de ejemplo...")
        # Crear algunos alumnos
        alumnos_data = [
            {
                'nombre': 'Ana', 'apellido': 'García', 'email': 'ana.garcia@email.com',
                'telefono': '666111222', 'tipo_cuota': '1_clase_semanal',
                'matricula_pagada': True, 'fecha_matricula': date.today()
            },
            {
                'nombre': 'María', 'apellido': 'López', 'email': 'maria.lopez@email.com',
                'telefono': '666333444', 'tipo_cuota': '2_clases_semanal',
                'matricula_pagada': True, 'fecha_matricula': date.today()
            },
            {
                'nombre': 'Carmen', 'apellido': 'Martín', 'email': 'carmen.martin@email.com',
                'telefono': '666555666', 'tipo_cuota': 'plana',
                'matricula_pagada': False
            },
            {
                'nombre': 'Isabel', 'apellido': 'Ruiz', 'email': 'isabel.ruiz@email.com',
                'telefono': '666777888', 'tipo_cuota': '1_clase_bimensual',
                'matricula_pagada': True, 'fecha_matricula': date.today()
            },
            {
                'nombre': 'Laura', 'apellido': 'Sánchez', 'email': 'laura.sanchez@email.com',
                'telefono': '666999000', 'tipo_cuota': '2_clases_bimensual',
                'matricula_pagada': True, 'fecha_matricula': date.today()
            }
        ]
        
        for alumno_data in alumnos_data:
            alumno = Alumno(**alumno_data)
            db.session.add(alumno)
            db.session.flush()
            
            # Crear pago de matrícula si está pagada
            if alumno.matricula_pagada:
                pago_matricula = Pago(
                    alumno_id=alumno.id,
                    año=2025,
                    monto=25.00,
                    tipo_pago='matricula',
                    descripcion='Matrícula 25/26',
                    metodo_pago='transferencia'
                )
                db.session.add(pago_matricula)
            
            # Crear algunos pagos mensuales
            for mes in [7, 8, 9]:
                if random.random() < 0.8:  # 80% probabilidad
                    pago = Pago(
                        alumno_id=alumno.id,
                        mes=f"2025-{mes:02d}",
                        monto=alumno.get_precio_cuota(),
                        tipo_pago='cuota',
                        descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                        metodo_pago=random.choice(['efectivo', 'transferencia', 'bizum'])
                    )
                    db.session.add(pago)
        
        print("🕐 Creando horarios...")
        # Crear horarios
        clases = Clase.query.all()
        horarios_data = [
            # Lunes
            {'clase': clases[0], 'dia': 0, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': clases[1], 'dia': 0, 'hora_inicio': time(18, 0), 'hora_fin': time(19, 15)},
            
            # Miércoles
            {'clase': clases[0], 'dia': 2, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': clases[2], 'dia': 2, 'hora_inicio': time(17, 0), 'hora_fin': time(18, 15)},
            
            # Viernes
            {'clase': clases[0], 'dia': 4, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': clases[3], 'dia': 4, 'hora_inicio': time(19, 0), 'hora_fin': time(19, 45)},
        ]
        
        for horario_data in horarios_data:
            horario = HorarioSemanal(
                clase_id=horario_data['clase'].id,
                dia_semana=horario_data['dia'],
                hora_inicio=horario_data['hora_inicio'],
                hora_fin=horario_data['hora_fin'],
                instructor='Minouche'
            )
            db.session.add(horario)
        
        print("📅 Creando asistencias de ejemplo...")
        # Crear algunas asistencias
        alumnos = Alumno.query.all()
        horarios = HorarioSemanal.query.all()
        
        # Generar asistencias para los últimos 30 días
        fecha_inicio = date.today() - timedelta(days=30)
        
        for i in range(30):
            fecha_clase = fecha_inicio + timedelta(days=i)
            dia_semana = fecha_clase.weekday()
            
            # Buscar horarios para este día
            horarios_dia = [h for h in horarios if h.dia_semana == dia_semana]
            
            for horario in horarios_dia:
                # Algunos alumnos asisten
                for alumno in random.sample(alumnos, random.randint(2, 4)):
                    if random.random() < 0.7:  # 70% probabilidad de asistir
                        asistencia = Asistencia(
                            alumno_id=alumno.id,
                            horario_id=horario.id,
                            fecha_clase=fecha_clase,
                            presente=random.random() < 0.9,  # 90% presente si se registra
                            observaciones=random.choice([None, None, 'Muy bien', 'Llegó tarde']) if random.random() < 0.2 else None
                        )
                        db.session.add(asistencia)
        
        print("💰 Creando gastos de ejemplo...")
        # Crear algunos gastos
        gastos = [
            {
                'fecha': date(2025, 9, 1),
                'concepto': 'Alquiler del local',
                'categoria': 'Alquiler',
                'importe': 950.00,
                'pagado': True,
                'metodo_pago': 'transferencia'
            },
            {
                'fecha': date(2025, 9, 5),
                'concepto': 'Factura de luz',
                'categoria': 'Suministros',
                'importe': 110.75,
                'pagado': False
            },
            {
                'fecha': date(2025, 9, 10),
                'concepto': 'Internet y teléfono',
                'categoria': 'Suministros',
                'importe': 65.00,
                'pagado': True,
                'metodo_pago': 'domiciliacion'
            }
        ]
        
        for gasto_data in gastos:
            gasto = GastoMensual(**gasto_data)
            db.session.add(gasto)
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("✅ APLICACIÓN INICIALIZADA CORRECTAMENTE")
        print(f"📊 Alumnos creados: {Alumno.query.count()}")
        print(f"📚 Clases creadas: {Clase.query.count()}")
        print(f"💰 Pagos registrados: {Pago.query.count()}")
        print(f"🕐 Horarios creados: {HorarioSemanal.query.count()}")
        print(f"📅 Asistencias creadas: {Asistencia.query.count()}")
        print(f"💸 Gastos creados: {GastoMensual.query.count()}")
        print("\n🚀 ¡Listo! Ejecuta 'python app.py' para iniciar la aplicación")

if __name__ == "__main__":
    main()