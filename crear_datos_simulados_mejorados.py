#!/usr/bin/env python3
"""
Script para crear datos simulados mejorados para la escuela de yoga
Incluye alumnos al corriente y alumnos con pagos pendientes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alumno, Pago, Clase, HorarioSemanal, Asistencia
from datetime import date, datetime, timedelta
import random

def limpiar_datos():
    """Limpiar todos los datos existentes"""
    print("🧹 Limpiando datos existentes...")
    
    # Eliminar en orden correcto para evitar problemas de claves foráneas
    Asistencia.query.delete()
    Pago.query.delete()
    HorarioSemanal.query.delete()
    Clase.query.delete()
    Alumno.query.delete()
    
    db.session.commit()
    print("✅ Datos limpiados")

def crear_clases_basicas():
    """Crear las clases básicas de yoga"""
    print("📚 Creando clases básicas...")
    
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
        clase = Clase(**clase_data)
        db.session.add(clase)
    
    db.session.commit()
    print("✅ Clases creadas")

def crear_alumnos_simulados():
    """Crear alumnos con diferentes estados de pago"""
    print("👥 Creando alumnos simulados...")
    
    # Datos para generar alumnos realistas
    nombres_f = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Sofia', 'Patricia', 'Rosa', 'Mónica', 'Cristina', 'Pilar']
    nombres_m = ['Carlos', 'Miguel', 'Antonio', 'José', 'Francisco', 'David', 'Juan', 'Pedro', 'Luis', 'Alejandro']
    apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz']
    
    current_year = date.today().year
    current_month = date.today().month
    
    alumnos_creados = []
    
    # 1. Crear 5 alumnos AL CORRIENTE (con todos los pagos al día)
    print("  📈 Creando alumnos al corriente...")
    for i in range(5):
        nombre = random.choice(nombres_f + nombres_m)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_semanal', '2_clases_semanal', 'plana'])
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1960 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja', 'Principal'])} {random.randint(1, 100)}",
            condiciones_medicas=random.choice(['Ninguna', 'Hipertensión leve', 'Problemas de espalda', '']),
            tipo_cuota=tipo_cuota,
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)),
            activo=True
        )
        db.session.add(alumno)
        db.session.flush()
        
        # Pago de matrícula
        pago_matricula = Pago(
            alumno_id=alumno.id,
            año=current_year,
            monto=25.00,
            tipo_pago='matricula',
            descripcion=f'Matrícula anual {current_year}',
            metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta']),
            fecha_creacion=datetime(current_year, 1, random.randint(1, 28))
        )
        db.session.add(pago_matricula)
        
        # Pagos mensuales hasta el mes actual
        for mes in range(1, current_month + 1):
            pago_cuota = Pago(
                alumno_id=alumno.id,
                mes=f"{current_year}-{mes:02d}",
                monto=alumno.get_precio_cuota(),
                tipo_pago='cuota',
                descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta', 'bizum']),
                fecha_creacion=datetime(current_year, mes, random.randint(1, 28))
            )
            db.session.add(pago_cuota)
        
        alumnos_creados.append(f"✅ {nombre} {apellido} - AL CORRIENTE")
    
    # 2. Crear 3 alumnos con PAGOS BIMENSUALES al corriente
    print("  📊 Creando alumnos bimensuales al corriente...")
    for i in range(3):
        nombre = random.choice(nombres_f)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_bimensual', '2_clases_bimensual'])
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+10}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1965 + random.randint(0, 35), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Avenida {random.choice(['Constitución', 'España', 'Libertad'])} {random.randint(1, 50)}",
            tipo_cuota=tipo_cuota,
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)),
            activo=True
        )
        db.session.add(alumno)
        db.session.flush()
        
        # Pago de matrícula
        pago_matricula = Pago(
            alumno_id=alumno.id,
            año=current_year,
            monto=25.00,
            tipo_pago='matricula',
            descripcion=f'Matrícula anual {current_year}',
            metodo_pago='transferencia',
            fecha_creacion=datetime(current_year, 1, 15)
        )
        db.session.add(pago_matricula)
        
        # Pagos bimensuales (cada 2 meses)
        bimestres_pagados = []
        if current_month >= 2:
            bimestres_pagados.append((1, 2))  # Enero-Febrero
        if current_month >= 4:
            bimestres_pagados.append((3, 4))  # Marzo-Abril
        if current_month >= 6:
            bimestres_pagados.append((5, 6))  # Mayo-Junio
        if current_month >= 8:
            bimestres_pagados.append((7, 8))  # Julio-Agosto
        if current_month >= 10:
            bimestres_pagados.append((9, 10))  # Septiembre-Octubre
        
        for mes1, mes2 in bimestres_pagados:
            pago_bimestre = Pago(
                alumno_id=alumno.id,
                mes=f"{current_year}-{mes1:02d}",  # Registrar en el primer mes del bimestre
                monto=alumno.get_precio_cuota(),
                tipo_pago='cuota',
                descripcion=f'Cuota bimensual {mes1:02d}-{mes2:02d}/{current_year}',
                metodo_pago=random.choice(['transferencia', 'efectivo']),
                fecha_creacion=datetime(current_year, mes1, 15)
            )
            db.session.add(pago_bimestre)
        
        alumnos_creados.append(f"✅ {nombre} {apellido} - BIMENSUAL AL CORRIENTE")
    
    # 3. Crear 4 alumnos CON PAGOS PENDIENTES (algunos meses sin pagar)
    print("  ⚠️ Creando alumnos con pagos pendientes...")
    for i in range(4):
        nombre = random.choice(nombres_f + nombres_m)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_semanal', '2_clases_semanal'])
        
        # Algunos sin matrícula pagada
        matricula_pagada = random.choice([True, False])
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+20}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1970 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Plaza {random.choice(['Mayor', 'España', 'Constitución'])} {random.randint(1, 20)}",
            tipo_cuota=tipo_cuota,
            matricula_pagada=matricula_pagada,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)) if matricula_pagada else None,
            activo=True
        )
        db.session.add(alumno)
        db.session.flush()
        
        # Pago de matrícula solo si está pagada
        if matricula_pagada:
            pago_matricula = Pago(
                alumno_id=alumno.id,
                año=current_year,
                monto=25.00,
                tipo_pago='matricula',
                descripcion=f'Matrícula anual {current_year}',
                metodo_pago='efectivo',
                fecha_creacion=datetime(current_year, 1, random.randint(1, 28))
            )
            db.session.add(pago_matricula)
        
        # Pagos parciales (solo algunos meses)
        meses_pagados = random.sample(range(1, current_month), random.randint(1, max(1, current_month - 3)))
        
        for mes in meses_pagados:
            pago_cuota = Pago(
                alumno_id=alumno.id,
                mes=f"{current_year}-{mes:02d}",
                monto=alumno.get_precio_cuota(),
                tipo_pago='cuota',
                descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                metodo_pago=random.choice(['efectivo', 'transferencia']),
                fecha_creacion=datetime(current_year, mes, random.randint(1, 28))
            )
            db.session.add(pago_cuota)
        
        meses_pendientes = current_month - len(meses_pagados)
        estado_matricula = "CON matrícula" if matricula_pagada else "SIN matrícula"
        alumnos_creados.append(f"⚠️ {nombre} {apellido} - {meses_pendientes} meses pendientes, {estado_matricula}")
    
    # 4. Crear 2 alumnos INACTIVOS (sin pagos ni asistencias en 2+ meses)
    print("  😴 Creando alumnos inactivos...")
    for i in range(2):
        nombre = random.choice(nombres_f)
        apellido = random.choice(apellidos)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+30}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1975 + random.randint(0, 25), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Olmo', 'Roble', 'Pino'])} {random.randint(1, 30)}",
            tipo_cuota=random.choice(['1_clase_semanal', '2_clases_semanal']),
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, 15),
            activo=True
        )
        db.session.add(alumno)
        db.session.flush()
        
        # Pago de matrícula
        pago_matricula = Pago(
            alumno_id=alumno.id,
            año=current_year,
            monto=25.00,
            tipo_pago='matricula',
            descripcion=f'Matrícula anual {current_year}',
            metodo_pago='efectivo',
            fecha_creacion=datetime(current_year, 1, 15)
        )
        db.session.add(pago_matricula)
        
        # Solo pagos de los primeros meses (hace más de 2 meses)
        meses_antiguos = min(3, max(1, current_month - 3))
        for mes in range(1, meses_antiguos + 1):
            pago_cuota = Pago(
                alumno_id=alumno.id,
                mes=f"{current_year}-{mes:02d}",
                monto=alumno.get_precio_cuota(),
                tipo_pago='cuota',
                descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                metodo_pago='efectivo',
                fecha_creacion=datetime(current_year, mes, 15)
            )
            db.session.add(pago_cuota)
        
        alumnos_creados.append(f"😴 {nombre} {apellido} - INACTIVO (sin actividad +2 meses)")
    
    # 5. Crear 1 alumno DESACTIVADO
    print("  🚫 Creando alumno desactivado...")
    alumno_desactivado = Alumno(
        nombre="Alumno",
        apellido="Desactivado",
        email="desactivado@email.com",
        telefono="600000000",
        fecha_nacimiento=date(1980, 5, 15),
        direccion="Calle Desactivada 1",
        tipo_cuota='1_clase_semanal',
        matricula_pagada=False,
        activo=False
    )
    db.session.add(alumno_desactivado)
    alumnos_creados.append("🚫 Alumno Desactivado - DESACTIVADO")
    
    db.session.commit()
    
    print("\n📋 RESUMEN DE ALUMNOS CREADOS:")
    for alumno_info in alumnos_creados:
        print(f"  {alumno_info}")
    
    return len(alumnos_creados)

def crear_horarios_ejemplo():
    """Crear algunos horarios de ejemplo"""
    print("🕐 Creando horarios de ejemplo...")
    
    clases = Clase.query.all()
    if not clases:
        print("❌ No hay clases disponibles")
        return
    
    horarios_data = [
        # Lunes
        {'clase_id': clases[0].id, 'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '10:15'},
        {'clase_id': clases[1].id, 'dia_semana': 0, 'hora_inicio': '18:00', 'hora_fin': '19:15'},
        
        # Miércoles
        {'clase_id': clases[0].id, 'dia_semana': 2, 'hora_inicio': '09:00', 'hora_fin': '10:15'},
        {'clase_id': clases[2].id, 'dia_semana': 2, 'hora_inicio': '17:00', 'hora_fin': '18:15'},
        
        # Viernes
        {'clase_id': clases[0].id, 'dia_semana': 4, 'hora_inicio': '09:00', 'hora_fin': '10:15'},
        {'clase_id': clases[3].id, 'dia_semana': 4, 'hora_inicio': '19:00', 'hora_fin': '20:00'},
    ]
    
    for horario_data in horarios_data:
        horario = HorarioSemanal(
            clase_id=horario_data['clase_id'],
            dia_semana=horario_data['dia_semana'],
            hora_inicio=datetime.strptime(horario_data['hora_inicio'], '%H:%M').time(),
            hora_fin=datetime.strptime(horario_data['hora_fin'], '%H:%M').time(),
            instructor='Minouche'
        )
        db.session.add(horario)
    
    db.session.commit()
    print("✅ Horarios creados")

def crear_asistencias_simuladas():
    """Crear asistencias simuladas para los últimos 2 meses"""
    print("📅 Creando asistencias simuladas...")
    
    alumnos = Alumno.query.filter_by(activo=True).all()
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    
    if not alumnos or not horarios:
        print("❌ No hay alumnos u horarios disponibles")
        return
    
    # Generar asistencias para los últimos 60 días
    fecha_inicio = date.today() - timedelta(days=60)
    fecha_fin = date.today()
    
    asistencias_creadas = 0
    
    # Para cada alumno activo
    for alumno in alumnos[:12]:  # Solo los primeros 12 alumnos para no sobrecargar
        # Determinar patrón de asistencia según el tipo de cuota
        if alumno.tipo_cuota == '1_clase_semanal':
            clases_por_semana = 1
        elif alumno.tipo_cuota == '2_clases_semanal':
            clases_por_semana = 2
        elif alumno.tipo_cuota == 'plana':
            clases_por_semana = random.randint(2, 4)
        else:
            clases_por_semana = 1
        
        # Probabilidad de asistencia (algunos alumnos más constantes que otros)
        probabilidad_asistencia = random.uniform(0.6, 0.95)
        
        # Generar asistencias día por día
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            dia_semana = fecha_actual.weekday()  # 0=Lunes, 6=Domingo
            
            # Buscar horarios para este día
            horarios_dia = [h for h in horarios if h.dia_semana == dia_semana]
            
            if horarios_dia and random.random() < (clases_por_semana / 7):  # Probabilidad diaria
                # Seleccionar un horario al azar
                horario = random.choice(horarios_dia)
                
                # Decidir si asiste o no
                presente = random.random() < probabilidad_asistencia
                
                # Crear asistencia
                asistencia = Asistencia(
                    alumno_id=alumno.id,
                    horario_id=horario.id,
                    fecha_clase=fecha_actual,
                    presente=presente,
                    observaciones=random.choice([
                        None, None, None,  # Mayoría sin observaciones
                        'Muy bien hoy',
                        'Le costó un poco',
                        'Excelente práctica',
                        'Llegó tarde',
                        'Se fue antes'
                    ]) if presente else random.choice([
                        'Avisó por WhatsApp',
                        'No avisó',
                        'Enfermo/a',
                        'Trabajo',
                        None
                    ])
                )
                db.session.add(asistencia)
                asistencias_creadas += 1
            
            fecha_actual += timedelta(days=1)
    
    db.session.commit()
    print(f"✅ {asistencias_creadas} asistencias creadas")

def main():
    """Función principal"""
    print("🧘‍♀️ CREANDO DATOS SIMULADOS MEJORADOS PARA ATMA SUDDHI")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Limpiar datos existentes
            limpiar_datos()
            
            # Crear datos básicos
            crear_clases_basicas()
            crear_horarios_ejemplo()
            
            # Crear alumnos con diferentes estados
            total_alumnos = crear_alumnos_simulados()
            
            # Crear asistencias simuladas
            crear_asistencias_simuladas()
            
            print("\n" + "=" * 60)
            print(f"✅ DATOS CREADOS EXITOSAMENTE")
            print(f"📊 Total de alumnos: {total_alumnos}")
            print(f"📚 Clases creadas: {Clase.query.count()}")
            print(f"💰 Pagos registrados: {Pago.query.count()}")
            print(f"🕐 Horarios creados: {HorarioSemanal.query.count()}")
            print(f"📅 Asistencias creadas: {Asistencia.query.count()}")
            print("\n🚀 ¡Listo para probar la aplicación!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())