#!/usr/bin/env python3
"""
Script simple para resetear y crear datos básicos
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Eliminar base de datos existente
    if os.path.exists('yoga_school.db'):
        os.remove('yoga_school.db')
        print("🗑️ Base de datos eliminada")
    
    # Importar después de eliminar la BD
    from app import app, db, Alumno, Pago, Clase, HorarioSemanal, GastoMensual
    from datetime import date, datetime, time
    import random
    
    with app.app_context():
        print("🏗️ Creando tablas...")
        db.create_all()
        
        # Inicializar categorías
        from app import inicializar_categorias_gastos
        inicializar_categorias_gastos()
        # inicializar_clases()  # Comentado temporalmente
        
        print("👥 Creando 5 alumnos...")
        # Crear 5 alumnos simples
        alumnos_data = [
            {'nombre': 'Ana', 'apellido': 'García', 'email': 'ana@test.com', 'tipo_cuota': '1_clase_semanal'},
            {'nombre': 'María', 'apellido': 'López', 'email': 'maria@test.com', 'tipo_cuota': '2_clases_semanal'},
            {'nombre': 'Carmen', 'apellido': 'Martín', 'email': 'carmen@test.com', 'tipo_cuota': 'plana'},
            {'nombre': 'Isabel', 'apellido': 'Ruiz', 'email': 'isabel@test.com', 'tipo_cuota': '1_clase_bimensual'},
            {'nombre': 'Laura', 'apellido': 'Sánchez', 'email': 'laura@test.com', 'tipo_cuota': '2_clases_bimensual'},
        ]
        
        for i, data in enumerate(alumnos_data):
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
            db.session.flush()
            
            # Crear pago de matrícula
            pago_matricula = Pago(
                alumno_id=alumno.id,
                año=2025,
                monto=25.00,
                tipo_pago='matricula',
                descripcion='Matrícula anual 2025',
                metodo_pago='transferencia'
            )
            db.session.add(pago_matricula)
            
            # Crear algunos pagos mensuales
            for mes in [7, 8, 9]:
                if random.random() < 0.7:  # 70% probabilidad
                    pago = Pago(
                        alumno_id=alumno.id,
                        mes=f"2025-{mes:02d}",
                        monto=alumno.get_precio_cuota(),
                        tipo_pago='cuota',
                        descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                        metodo_pago=random.choice(['efectivo', 'transferencia'])
                    )
                    db.session.add(pago)
        
        print("📅 Creando horarios...")
        # Crear horarios completos
        yoga_integral = Clase.query.filter_by(nombre='Yoga integral').first()
        yoga_menopausia = Clase.query.filter_by(nombre='Yoga menopausia').first()
        yoga_embarazadas = Clase.query.filter_by(nombre='Yoga embarazadas').first()
        meditacion = Clase.query.filter_by(nombre='Meditación').first()
        
        horarios = [
            # Lunes
            {'clase': yoga_integral, 'dia': 0, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': yoga_menopausia, 'dia': 0, 'hora_inicio': time(18, 0), 'hora_fin': time(19, 15)},
            
            # Martes
            {'clase': yoga_embarazadas, 'dia': 1, 'hora_inicio': time(10, 0), 'hora_fin': time(11, 15)},
            {'clase': yoga_integral, 'dia': 1, 'hora_inicio': time(19, 0), 'hora_fin': time(20, 15)},
            
            # Miércoles
            {'clase': meditacion, 'dia': 2, 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45)},
            {'clase': yoga_integral, 'dia': 2, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': yoga_menopausia, 'dia': 2, 'hora_inicio': time(18, 30), 'hora_fin': time(19, 45)},
            
            # Jueves
            {'clase': yoga_embarazadas, 'dia': 3, 'hora_inicio': time(10, 0), 'hora_fin': time(11, 15)},
            {'clase': yoga_integral, 'dia': 3, 'hora_inicio': time(19, 0), 'hora_fin': time(20, 15)},
            
            # Viernes
            {'clase': yoga_integral, 'dia': 4, 'hora_inicio': time(9, 30), 'hora_fin': time(10, 45)},
            {'clase': meditacion, 'dia': 4, 'hora_inicio': time(20, 0), 'hora_fin': time(20, 45)},
            
            # Sábado
            {'clase': yoga_integral, 'dia': 5, 'hora_inicio': time(10, 0), 'hora_fin': time(11, 15)},
            {'clase': yoga_menopausia, 'dia': 5, 'hora_inicio': time(11, 30), 'hora_fin': time(12, 45)},
        ]
        
        for horario_data in horarios:
            if horario_data['clase']:
                horario = HorarioSemanal(
                    clase_id=horario_data['clase'].id,
                    dia_semana=horario_data['dia'],
                    hora_inicio=horario_data['hora_inicio'],
                    hora_fin=horario_data['hora_fin'],
                    instructor='Minouche'
                )
                db.session.add(horario)
        
        print("💰 Creando gastos...")
        # Crear algunos gastos
        gastos = [
            {'fecha': date(2025, 9, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True, 'metodo_pago': 'transferencia'},
            {'fecha': date(2025, 9, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 110.75, 'pagado': False},
            {'fecha': date(2025, 9, 10), 'concepto': 'Internet', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True, 'metodo_pago': 'domiciliacion'},
        ]
        
        for gasto_data in gastos:
            gasto = GastoMensual(**gasto_data)
            db.session.add(gasto)
        
        db.session.commit()
        print("✅ ¡Base de datos creada exitosamente!")
        print("   - 5 alumnos con pagos")
        print("   - 13 horarios semanales")
        print("   - 3 gastos de ejemplo")

if __name__ == "__main__":
    main()