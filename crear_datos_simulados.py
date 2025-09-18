#!/usr/bin/env python3
"""
Script para crear datos simulados de 3 meses de funcionamiento
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alumno, Pago, Proveedor, FacturaProveedor, CategoriaGasto, GastoFijo, SesionYogaterapia, Clase
from datetime import date, timedelta, datetime
import random

def crear_datos_simulados():
    with app.app_context():
        print("🧘 Creando datos simulados para 3 meses de funcionamiento...")
        
        # Limpiar datos existentes si los hay
        db.drop_all()
        db.create_all()
        
        # Inicializar categorías
        from app import inicializar_categorias_gastos
        inicializar_categorias_gastos()
        
        # Crear 15 alumnos de prueba
        nombres = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Sofia', 'Patricia', 'Rosa', 'Mónica', 
                   'Cristina', 'Pilar', 'Beatriz', 'Amparo', 'Dolores']
        apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín',
                    'Ruiz', 'Jiménez', 'Hernández', 'Díaz', 'Moreno']
        
        current_year = date.today().year
        
        # Crear alumnos
        alumnos_creados = []
        for i in range(20):  # Aumentamos a 20 alumnos
            matricula_pagada = random.choice([True, True, True, False])  # 75% tienen matrícula
            fecha_registro = date.today() - timedelta(days=random.randint(30, 120))  # Registrados en últimos 4 meses
            
            alumno = Alumno(
                nombre=random.choice(nombres),
                apellido=random.choice(apellidos),
                email=f"alumno{i+1}@atmasuddhi.com",
                telefono=f"6{random.randint(10000000, 99999999)}",
                fecha_nacimiento=date(1960 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)),
                direccion=f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja', 'Sol', 'Luna'])} {random.randint(1, 100)}, Madrid",
                condiciones_medicas=random.choice(['Ninguna', 'Hipertensión leve', 'Problemas de espalda', 'Artritis', 'Estrés', '']),
                tipo_cuota=random.choice(['1_clase_semanal', '2_clases_semanal', 'plana', '1_clase_bimensual', '2_clases_bimensual']),
                matricula_pagada=matricula_pagada,
                fecha_matricula=fecha_registro if matricula_pagada else None,
                fecha_registro=datetime.combine(fecha_registro, datetime.min.time())
            )
            db.session.add(alumno)
            db.session.flush()
            alumnos_creados.append(alumno)
            
            # Crear pagos realistas de los últimos 4 meses (junio, julio, agosto, septiembre)
            meses_funcionamiento = [6, 7, 8, 9]  # Junio, Julio, Agosto, Septiembre
            
            for mes in meses_funcionamiento:
                # Probabilidad variable: más reciente = más probable
                probabilidad = 0.9 if mes >= 8 else 0.7 if mes == 7 else 0.5
                
                if random.random() < probabilidad:
                    fecha_pago = date(current_year, mes, random.randint(1, 28))
                    pago = Pago(
                        alumno_id=alumno.id,
                        mes=f"{current_year}-{mes:02d}",
                        monto=alumno.get_precio_cuota(),
                        tipo_pago='cuota',
                        descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                        metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta']),
                        fecha_creacion=datetime.combine(fecha_pago, datetime.min.time())
                    )
                    db.session.add(pago)
            
            # Matrícula si está pagada
            if matricula_pagada:
                pago_matricula = Pago(
                    alumno_id=alumno.id,
                    año=current_year,
                    monto=25.00,
                    tipo_pago='matricula',
                    descripcion=f'Matrícula anual {current_year}',
                    metodo_pago=random.choice(['efectivo', 'transferencia']),
                    fecha_creacion=datetime.combine(fecha_registro, datetime.min.time())
                )
                db.session.add(pago_matricula)
            
            # Crear algunas clases sueltas
            if random.random() < 0.4:  # 40% han tomado clases sueltas
                for _ in range(random.randint(1, 3)):
                    fecha_clase = date.today() - timedelta(days=random.randint(1, 60))
                    pago_clase_suelta = Pago(
                        alumno_id=alumno.id,
                        fecha_clase=fecha_clase,
                        monto=15.00,
                        tipo_pago='clase_suelta',
                        descripcion='Clase suelta',
                        metodo_pago=random.choice(['efectivo', 'tarjeta']),
                        fecha_creacion=datetime.combine(fecha_clase, datetime.min.time())
                    )
                    db.session.add(pago_clase_suelta)
        
        # Crear proveedores realistas
        proveedores_data = [
            {'nombre': 'Iberdrola Energía', 'cif_nif': 'A95758389', 'telefono': '900225235', 'email': 'atencion.cliente@iberdrola.es'},
            {'nombre': 'Canal de Isabel II', 'cif_nif': 'A28003119', 'telefono': '901512345', 'email': 'info@canaldeisabelsegunda.es'},
            {'nombre': 'Movistar', 'cif_nif': 'A82018474', 'telefono': '1004', 'email': 'atencion.cliente@movistar.es'},
            {'nombre': 'Inmobiliaria Centro Madrid', 'cif_nif': 'B87654321', 'telefono': '915551234', 'email': 'info@centromadrid.es'},
            {'nombre': 'Yoga Props España', 'cif_nif': 'B12345678', 'telefono': '913334455', 'email': 'ventas@yogaprops.es'},
            {'nombre': 'Seguros Mapfre', 'cif_nif': 'A08055636', 'telefono': '902102110', 'email': 'info@mapfre.com'},
            {'nombre': 'Limpiezas Profesionales SL', 'cif_nif': 'B98765432', 'telefono': '916667788', 'email': 'contacto@limpiezaspro.es'}
        ]
        
        for prov_data in proveedores_data:
            proveedor = Proveedor(
                nombre=prov_data['nombre'],
                cif_nif=prov_data['cif_nif'],
                telefono=prov_data['telefono'],
                email=prov_data['email'],
                direccion=f"Calle {random.choice(['Alcalá', 'Gran Vía', 'Serrano'])} {random.randint(1, 200)}, Madrid",
                contacto_principal=f"Departamento de {random.choice(['Ventas', 'Atención al Cliente', 'Facturación'])}",
                fecha_registro=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            db.session.add(proveedor)
            db.session.flush()
            
            # Crear facturas para cada proveedor
            for mes in [7, 8, 9]:  # Últimos 3 meses
                if random.random() < 0.8:  # 80% probabilidad de factura por mes
                    fecha_factura = date(current_year, mes, random.randint(1, 28))
                    
                    # Asignar categoría según el proveedor
                    if 'Iberdrola' in prov_data['nombre']:
                        categoria_nombre = 'Suministros'
                        importe = random.uniform(80, 150)
                    elif 'Canal' in prov_data['nombre']:
                        categoria_nombre = 'Suministros'
                        importe = random.uniform(30, 60)
                    elif 'Movistar' in prov_data['nombre']:
                        categoria_nombre = 'Suministros'
                        importe = random.uniform(40, 80)
                    elif 'Inmobiliaria' in prov_data['nombre']:
                        categoria_nombre = 'Alquiler'
                        importe = random.uniform(800, 1200)
                    elif 'Yoga Props' in prov_data['nombre']:
                        categoria_nombre = 'Material'
                        importe = random.uniform(100, 300)
                    elif 'Mapfre' in prov_data['nombre']:
                        categoria_nombre = 'Seguros'
                        importe = random.uniform(50, 100)
                    else:
                        categoria_nombre = 'Mantenimiento'
                        importe = random.uniform(80, 200)
                    
                    categoria = CategoriaGasto.query.filter_by(nombre=categoria_nombre).first()
                    
                    factura = FacturaProveedor(
                        numero_factura=f"F{current_year}{mes:02d}{random.randint(1000, 9999)}",
                        proveedor_id=proveedor.id,
                        categoria_id=categoria.id if categoria else 1,
                        fecha_factura=fecha_factura,
                        fecha_vencimiento=fecha_factura + timedelta(days=30),
                        importe_sin_iva=importe,
                        iva=21.0,
                        importe_total=importe * 1.21,
                        descripcion=f"Servicios de {prov_data['nombre']} - {mes:02d}/{current_year}",
                        estado=random.choice(['pagada', 'pagada', 'pendiente']),  # 66% pagadas
                        fecha_pago=fecha_factura + timedelta(days=random.randint(1, 25)) if random.random() < 0.66 else None,
                        metodo_pago=random.choice(['transferencia', 'domiciliacion']) if random.random() < 0.66 else None
                    )
                    db.session.add(factura)
        
        # Crear horarios semanales completos
        from app import HorarioSemanal
        from datetime import time
        
        horarios_data = [
            # Lunes
            {'clase': 'Yoga integral', 'dia': 0, 'hora_inicio': '09:30', 'hora_fin': '10:45'},
            {'clase': 'Yoga menopausia', 'dia': 0, 'hora_inicio': '11:00', 'hora_fin': '12:15'},
            {'clase': 'Yoga integral', 'dia': 0, 'hora_inicio': '18:00', 'hora_fin': '19:15'},
            {'clase': 'Yoga embarazadas', 'dia': 0, 'hora_inicio': '19:30', 'hora_fin': '20:45'},
            
            # Martes  
            {'clase': 'Meditación', 'dia': 1, 'hora_inicio': '08:00', 'hora_fin': '08:45'},
            {'clase': 'Yoga embarazadas', 'dia': 1, 'hora_inicio': '10:00', 'hora_fin': '11:15'},
            {'clase': 'Yoga integral', 'dia': 1, 'hora_inicio': '11:30', 'hora_fin': '12:45'},
            {'clase': 'Yoga menopausia', 'dia': 1, 'hora_inicio': '18:30', 'hora_fin': '19:45'},
            {'clase': 'Yoga integral', 'dia': 1, 'hora_inicio': '20:00', 'hora_fin': '21:15'},
            
            # Miércoles
            {'clase': 'Yoga integral', 'dia': 2, 'hora_inicio': '09:30', 'hora_fin': '10:45'},
            {'clase': 'Yoga embarazadas', 'dia': 2, 'hora_inicio': '11:00', 'hora_fin': '12:15'},
            {'clase': 'Meditación', 'dia': 2, 'hora_inicio': '17:30', 'hora_fin': '18:15'},
            {'clase': 'Yoga integral', 'dia': 2, 'hora_inicio': '18:30', 'hora_fin': '19:45'},
            {'clase': 'Yoga menopausia', 'dia': 2, 'hora_inicio': '20:00', 'hora_fin': '21:15'},
            
            # Jueves
            {'clase': 'Yoga integral', 'dia': 3, 'hora_inicio': '09:00', 'hora_fin': '10:15'},
            {'clase': 'Yoga menopausia', 'dia': 3, 'hora_inicio': '10:30', 'hora_fin': '11:45'},
            {'clase': 'Yoga embarazadas', 'dia': 3, 'hora_inicio': '18:00', 'hora_fin': '19:15'},
            {'clase': 'Yoga integral', 'dia': 3, 'hora_inicio': '19:30', 'hora_fin': '20:45'},
            
            # Viernes
            {'clase': 'Meditación', 'dia': 4, 'hora_inicio': '08:30', 'hora_fin': '09:15'},
            {'clase': 'Yoga integral', 'dia': 4, 'hora_inicio': '09:30', 'hora_fin': '10:45'},
            {'clase': 'Yoga menopausia', 'dia': 4, 'hora_inicio': '11:00', 'hora_fin': '12:15'},
            {'clase': 'Yoga integral', 'dia': 4, 'hora_inicio': '18:00', 'hora_fin': '19:15'},
            {'clase': 'Meditación', 'dia': 4, 'hora_inicio': '20:00', 'hora_fin': '20:45'},
            
            # Sábado
            {'clase': 'Yoga integral', 'dia': 5, 'hora_inicio': '09:00', 'hora_fin': '10:15'},
            {'clase': 'Yoga integral', 'dia': 5, 'hora_inicio': '10:30', 'hora_fin': '11:45'},
            {'clase': 'Yoga menopausia', 'dia': 5, 'hora_inicio': '12:00', 'hora_fin': '13:15'},
            {'clase': 'Meditación', 'dia': 5, 'hora_inicio': '18:00', 'hora_fin': '18:45'}
        ]
        
        for horario_data in horarios_data:
            clase = Clase.query.filter_by(nombre=horario_data['clase']).first()
            if clase:
                horario = HorarioSemanal(
                    clase_id=clase.id,
                    dia_semana=horario_data['dia'],
                    hora_inicio=datetime.strptime(horario_data['hora_inicio'], '%H:%M').time(),
                    hora_fin=datetime.strptime(horario_data['hora_fin'], '%H:%M').time(),
                    instructor='Minouche'
                )
                db.session.add(horario)
        
        # Crear asistencias simuladas
        from app import Asistencia
        horarios_creados = HorarioSemanal.query.all()
        
        # Generar asistencias para los últimos 4 meses
        for semana in range(16):  # 16 semanas (4 meses)
            fecha_base = date.today() - timedelta(weeks=semana)
            
            for horario in horarios_creados:
                # Calcular fecha de la clase para esta semana
                dias_hasta_clase = (horario.dia_semana - fecha_base.weekday()) % 7
                fecha_clase = fecha_base + timedelta(days=dias_hasta_clase)
                
                # Solo crear asistencias para fechas pasadas
                if fecha_clase <= date.today():
                    # Seleccionar alumnos aleatorios para esta clase (30-70% de asistencia)
                    alumnos_asistentes = random.sample(alumnos_creados, random.randint(3, 8))
                    
                    for alumno in alumnos_asistentes:
                        # 85% de probabilidad de asistir
                        if random.random() < 0.85:
                            asistencia = Asistencia(
                                alumno_id=alumno.id,
                                horario_id=horario.id,
                                fecha_clase=fecha_clase,
                                presente=True,
                                observaciones=random.choice([
                                    '', 'Muy buena práctica', 'Necesita trabajar flexibilidad',
                                    'Excelente concentración', 'Mejorar alineación'
                                ])
                            )
                            db.session.add(asistencia)
        
        # Crear gastos mensuales simulados
        from app import GastoMensual
        
        gastos_simulados = [
            # Junio
            {'fecha': date(current_year, 6, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True},
            {'fecha': date(current_year, 6, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 135.20, 'pagado': True},
            {'fecha': date(current_year, 6, 10), 'concepto': 'Internet y teléfono', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True},
            {'fecha': date(current_year, 6, 15), 'concepto': 'Seguro responsabilidad civil', 'categoria': 'Seguros', 'importe': 85.00, 'pagado': True},
            {'fecha': date(current_year, 6, 20), 'concepto': 'Material inicial (bloques, mantas)', 'categoria': 'Material', 'importe': 250.00, 'pagado': True},
            
            # Julio
            {'fecha': date(current_year, 7, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True},
            {'fecha': date(current_year, 7, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 125.50, 'pagado': True},
            {'fecha': date(current_year, 7, 10), 'concepto': 'Internet y teléfono', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True},
            {'fecha': date(current_year, 7, 12), 'concepto': 'Agua', 'categoria': 'Suministros', 'importe': 42.30, 'pagado': True},
            {'fecha': date(current_year, 7, 20), 'concepto': 'Material yoga (esterillas)', 'categoria': 'Material', 'importe': 180.00, 'pagado': True},
            
            # Agosto
            {'fecha': date(current_year, 8, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True},
            {'fecha': date(current_year, 8, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 98.30, 'pagado': True},
            {'fecha': date(current_year, 8, 10), 'concepto': 'Internet y teléfono', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True},
            {'fecha': date(current_year, 8, 12), 'concepto': 'Limpieza profesional', 'categoria': 'Mantenimiento', 'importe': 120.00, 'pagado': True},
            {'fecha': date(current_year, 8, 15), 'concepto': 'Agua', 'categoria': 'Suministros', 'importe': 38.75, 'pagado': True},
            {'fecha': date(current_year, 8, 25), 'concepto': 'Curso de formación online', 'categoria': 'Formación', 'importe': 150.00, 'pagado': True},
            
            # Septiembre
            {'fecha': date(current_year, 9, 1), 'concepto': 'Alquiler del local', 'categoria': 'Alquiler', 'importe': 950.00, 'pagado': True},
            {'fecha': date(current_year, 9, 5), 'concepto': 'Factura de luz', 'categoria': 'Suministros', 'importe': 110.75, 'pagado': False},
            {'fecha': date(current_year, 9, 10), 'concepto': 'Internet y teléfono', 'categoria': 'Suministros', 'importe': 65.00, 'pagado': True},
            {'fecha': date(current_year, 9, 15), 'concepto': 'Agua', 'categoria': 'Suministros', 'importe': 45.20, 'pagado': False},
            {'fecha': date(current_year, 9, 16), 'concepto': 'Publicidad Facebook', 'categoria': 'Marketing', 'importe': 80.00, 'pagado': True},
            {'fecha': date(current_year, 9, 20), 'concepto': 'Mantenimiento aire acondicionado', 'categoria': 'Mantenimiento', 'importe': 95.00, 'pagado': True},
        ]
        
        for gasto_data in gastos_simulados:
            gasto = GastoMensual(
                fecha=gasto_data['fecha'],
                concepto=gasto_data['concepto'],
                categoria=gasto_data['categoria'],
                importe=gasto_data['importe'],
                pagado=gasto_data['pagado'],
                metodo_pago='transferencia' if gasto_data['pagado'] else None
            )
            db.session.add(gasto)
        
        try:
            db.session.commit()
            print("✅ Datos simulados creados exitosamente:")
            print(f"   - {len(alumnos_creados)} alumnos con historial de 4 meses")
            print(f"   - {len(proveedores_data)} proveedores con facturas")
            print(f"   - {len(gastos_simulados)} gastos mensuales")
            print(f"   - {len(horarios_data)} horarios semanales")
            print("   - Asistencias y pagos realistas")
            print("\n🎯 La escuela ahora tiene datos como si llevara 4 meses funcionando!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear datos de prueba: {e}")

if __name__ == "__main__":
    crear_datos_simulados()