#!/usr/bin/env python3
"""
Script para crear la aplicación desde cero sin verificaciones
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🧘‍♀️ CREANDO APLICACIÓN LIMPIA")
    print("=" * 40)
    
    # Asegurar que no existe la BD
    if os.path.exists('yoga_school.db'):
        os.remove('yoga_school.db')
        print("🗑️ BD anterior eliminada")
    
    # Importar la aplicación
    from app import app, db
    
    with app.app_context():
        print("🏗️ Creando tablas...")
        db.create_all()
        
        # Importar modelos después de crear tablas
        from app import Alumno, Pago, Clase, HorarioSemanal, Asistencia, GastoMensual, CategoriaGasto
        from datetime import date, datetime, time
        
        print("📂 Creando categorías...")
        # Crear categorías básicas
        categorias = [
            CategoriaGasto(nombre='Alquiler', descripcion='Alquiler del local', color='#dc3545'),
            CategoriaGasto(nombre='Suministros', descripcion='Luz, agua, gas', color='#ffc107'),
            CategoriaGasto(nombre='Material', descripcion='Esterillas, bloques', color='#28a745'),
            CategoriaGasto(nombre='Otros', descripcion='Gastos varios', color='#6c757d')
        ]
        
        for categoria in categorias:
            db.session.add(categoria)
        
        print("📚 Creando clases...")
        # Crear clases básicas
        clases = [
            Clase(
                nombre='Yoga integral',
                descripcion='Práctica completa de yoga',
                precio_clase_suelta=15.00,
                precio_1_semanal=40.00,
                precio_2_semanal=70.00,
                precio_plana=90.00,
                precio_1_bimensual=75.00,
                precio_2_bimensual=135.00,
                color='#007bff',
                nivel='todos',
                duracion_minutos=75,
                capacidad_maxima=15
            ),
            Clase(
                nombre='Yoga menopausia',
                descripcion='Clase especializada para menopausia',
                precio_clase_suelta=15.00,
                precio_1_semanal=40.00,
                precio_2_semanal=70.00,
                precio_plana=90.00,
                precio_1_bimensual=75.00,
                precio_2_bimensual=135.00,
                color='#e91e63',
                nivel='todos',
                duracion_minutos=75,
                capacidad_maxima=12
            ),
            Clase(
                nombre='Meditación',
                descripcion='Práctica de meditación',
                precio_clase_suelta=12.00,
                precio_1_semanal=35.00,
                precio_2_semanal=60.00,
                precio_plana=80.00,
                precio_1_bimensual=65.00,
                precio_2_bimensual=115.00,
                color='#9c27b0',
                nivel='todos',
                duracion_minutos=45,
                capacidad_maxima=20
            )
        ]
        
        for clase in clases:
            db.session.add(clase)
        
        db.session.commit()
        
        print("👥 Creando alumnos...")
        # Crear alumnos básicos
        alumnos = [
            Alumno(
                nombre='Ana', apellido='García', email='ana@test.com',
                telefono='666111222', tipo_cuota='1_clase_semanal',
                matricula_pagada=True, fecha_matricula=date.today()
            ),
            Alumno(
                nombre='María', apellido='López', email='maria@test.com',
                telefono='666333444', tipo_cuota='2_clases_semanal',
                matricula_pagada=True, fecha_matricula=date.today()
            ),
            Alumno(
                nombre='Carmen', apellido='Martín', email='carmen@test.com',
                telefono='666555666', tipo_cuota='plana',
                matricula_pagada=False
            )
        ]
        
        for alumno in alumnos:
            db.session.add(alumno)
        
        db.session.commit()
        
        # Crear algunos pagos
        print("💰 Creando pagos...")
        alumnos_db = Alumno.query.all()
        for alumno in alumnos_db:
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
            
            # Pago de septiembre
            pago_sept = Pago(
                alumno_id=alumno.id,
                mes='2025-09',
                monto=alumno.get_precio_cuota(),
                tipo_pago='cuota',
                descripcion=f'Cuota septiembre - {alumno.get_tipo_cuota_display()}',
                metodo_pago='efectivo'
            )
            db.session.add(pago_sept)
        
        print("🕐 Creando horarios...")
        # Crear horarios básicos
        clases_db = Clase.query.all()
        horarios = [
            HorarioSemanal(
                clase_id=clases_db[0].id, dia_semana=0,  # Lunes
                hora_inicio=time(9, 30), hora_fin=time(10, 45),
                instructor='Minouche'
            ),
            HorarioSemanal(
                clase_id=clases_db[1].id, dia_semana=0,  # Lunes
                hora_inicio=time(18, 0), hora_fin=time(19, 15),
                instructor='Minouche'
            ),
            HorarioSemanal(
                clase_id=clases_db[0].id, dia_semana=2,  # Miércoles
                hora_inicio=time(9, 30), hora_fin=time(10, 45),
                instructor='Minouche'
            ),
            HorarioSemanal(
                clase_id=clases_db[2].id, dia_semana=4,  # Viernes
                hora_inicio=time(19, 0), hora_fin=time(19, 45),
                instructor='Minouche'
            )
        ]
        
        for horario in horarios:
            db.session.add(horario)
        
        print("💸 Creando gastos...")
        # Crear gastos básicos
        gastos = [
            GastoMensual(
                fecha=date(2025, 9, 1),
                concepto='Alquiler del local',
                categoria='Alquiler',
                importe=950.00,
                pagado=True,
                metodo_pago='transferencia'
            ),
            GastoMensual(
                fecha=date(2025, 9, 5),
                concepto='Factura de luz',
                categoria='Suministros',
                importe=110.75,
                pagado=False
            )
        ]
        
        for gasto in gastos:
            db.session.add(gasto)
        
        db.session.commit()
        
        print("\n" + "=" * 40)
        print("✅ APLICACIÓN CREADA EXITOSAMENTE")
        print(f"📊 Alumnos: {Alumno.query.count()}")
        print(f"📚 Clases: {Clase.query.count()}")
        print(f"💰 Pagos: {Pago.query.count()}")
        print(f"🕐 Horarios: {HorarioSemanal.query.count()}")
        print(f"💸 Gastos: {GastoMensual.query.count()}")
        print("\n🚀 Ejecuta: python app.py")

if __name__ == "__main__":
    main()