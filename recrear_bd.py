#!/usr/bin/env python3
"""
Script para recrear la base de datos con datos de prueba
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from datetime import date, datetime, timedelta
import random

def recrear_base_datos():
    with app.app_context():
        print("🗑️ Eliminando base de datos existente...")
        
        # Eliminar archivo de base de datos si existe
        if os.path.exists('yoga_school.db'):
            os.remove('yoga_school.db')
        
        print("🏗️ Creando nuevas tablas...")
        db.create_all()
        
        # Inicializar categorías de gastos
        from app import inicializar_categorias_gastos
        inicializar_categorias_gastos()
        
        # Crear clases básicas
        from app import inicializar_clases
        inicializar_clases()
        
        print("👥 Creando alumnos de prueba...")
        crear_alumnos_prueba()
        
        print("📅 Creando horarios...")
        crear_horarios_prueba()
        
        print("💰 Creando pagos...")
        crear_pagos_prueba()
        
        print("🏢 Creando gastos...")
        crear_gastos_prueba()
        
        print("✅ Base de datos recreada exitosamente!")

def crear_alumnos_prueba():
    from app import Alumno
    
    alumnos_data = [
        {'nombre': 'Ana', 'apellido': 'García', 'email': 'ana.garcia@email.com', 'tipo_cuota': '1_clase_semanal'},
        {'nombre': 'María', 'apellido': 'López', 'email': 'maria.lopez@email.com', 'tipo_cuota': '2_clases_semanal'},
        {'nombre': 'Carmen', 'apellido': 'Martín', 'email': 'carmen.martin@email.com', 'tipo_cuota': 'plana'},
        {'nombre': 'Isabel', 'apellido': 'Ruiz', 'email': 'isabel.ruiz@email.com', 'tipo_cuota': '1_clase_bimensual'},
        {'nombre': 'Laura', 'apellido': 'Sánchez', 'email': 'laura.sanchez@email.com', 'tipo_cuota': '2_clases_bimensual'},
    ]
    
    for data in alumnos_data:
        alumno = Alumno(
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data['email'],
            telefono=f"6{random.randint(10000000, 99999999)}",
            tipo_cuota=data['tipo_cuota'],
            matricula_pagada=True,
            fecha_matricula=date.today(),
            fecha_registro=datetime.now()
        )
        db.session.add(alumno)
    
    db.session.commit()

def crear_horarios_prueba():
    from app import Clase, HorarioSemanal
    from datetime import time
    
    # Obtener clases
    yoga_integral = Clase.query.filter_by(nombre='Yoga integral').first()
    yoga_menopausia = Clase.query.filter_by(nombre='Yoga menopausia').first()
    
    if yoga_integral:
        # Lunes 9:30
        horario1 = HorarioSemanal(
            clase_id=yoga_integral.id,
            dia_semana=0,  # Lunes
            hora_inicio=time(9, 30),
            hora_fin=time(10, 45),
            instructor='Minouche'
        )
        db.session.add(horario1)
        
        # Miércoles 19:00
        horario2 = HorarioSemanal(
            clase_id=yoga_integral.id,
            dia_semana=2,  # Miércoles
            hora_inicio=time(19, 0),
            hora_fin=time(20, 15),
            instructor='Minouche'
        )
        db.session.add(horario2)
    
    if yoga_menopausia:
        # Martes 18:00
        horario3 = HorarioSemanal(
            clase_id=yoga_menopausia.id,
            dia_semana=1,  # Martes
            hora_inicio=time(18, 0),
            hora_fin=time(19, 15),
            instructor='Minouche'
        )
        db.session.add(horario3)
    
    db.session.commit()

def crear_pagos_prueba():
    from app import Alumno, Pago
    
    alumnos = Alumno.query.all()
    current_year = date.today().year
    
    for alumno in alumnos:
        # Matrícula
        pago_matricula = Pago(
            alumno_id=alumno.id,
            año=current_year,
            monto=25.00,
            tipo_pago='matricula',
            descripcion=f'Matrícula anual {current_year}',
            metodo_pago='transferencia'
        )
        db.session.add(pago_matricula)
        
        # Pagos mensuales (julio, agosto, septiembre)
        for mes in [7, 8, 9]:
            if random.random() < 0.8:  # 80% probabilidad
                pago = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                    metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta'])
                )
                db.session.add(pago)
    
    db.session.commit()

def crear_gastos_prueba():
    from app import GastoMensual
    
    gastos = [
        {'fecha': date(2025, 9, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True},
        {'fecha': date(2025, 9, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 110.75, 'pagado': False},
        {'fecha': date(2025, 9, 10), 'concepto': 'Internet', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True},
        {'fecha': date(2025, 9, 15), 'concepto': 'Material yoga', 'categoria': 'Material', 'importe': 120.00, 'pagado': True},
    ]
    
    for gasto_data in gastos:
        gasto = GastoMensual(**gasto_data)
        if gasto.pagado:
            gasto.metodo_pago = 'transferencia'
        db.session.add(gasto)
    
    db.session.commit()

if __name__ == "__main__":
    recrear_base_datos()