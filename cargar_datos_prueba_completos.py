"""
Script para cargar datos de prueba completos en el sistema
Incluye: alumnos, horarios, asistencias, facturas, proveedores, gastos fijos
"""
from app import app, db, Alumno, HorarioSemanal, Clase, Pago, Asistencia
from app import Cliente, FacturaEmitida, LineaFactura, ConfiguracionFiscal
from app import Proveedor, FacturaProveedor, CategoriaGasto, GastoFijo, Tarifa
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
import random

def cargar_datos_completos(modo_web=False):
    """
    Carga datos de prueba completos
    modo_web: Si es True, no elimina datos existentes (solo añade)
    """
    with app.app_context():
        if not modo_web:
            print("=" * 60)
            print("CARGA DE DATOS DE PRUEBA COMPLETOS")
            print("=" * 60)
            print()

        try:
            # 1. CONFIGURACIÓN FISCAL
            if not modo_web:
                print("1. Verificando configuración fiscal...")

            config_fiscal = ConfiguracionFiscal.query.first()
            if not config_fiscal:
                config_fiscal = ConfiguracionFiscal(
                    nombre_empresa='Atma Suddhi - Escuela de Yoga',
                    nif='12345678Z',
                    direccion_fiscal='Calle Ejemplo, 123',
                    codigo_postal='28001',
                    ciudad='Madrid',
                    provincia='Madrid',
                    tipo_retencion_default=7.0,
                    exento_iva=True,
                    texto_exencion_iva='Exento de IVA según art. 20.Uno.9 de la Ley 37/1992',
                    serie_factura_default='A'
                )
                db.session.add(config_fiscal)
                db.session.commit()
                if not modo_web:
                    print("   - Configuración fiscal creada")

            # 2. HORARIOS SEMANALES
            if not modo_web:
                print("2. Creando horarios semanales...")

            # Siempre verificar y crear horarios si no existen los correctos
            horarios_existentes = HorarioSemanal.query.count()
            if horarios_existentes == 0:
                yoga_integral = Clase.query.filter_by(nombre='Yoga integral').first()
                meditacion = Clase.query.filter_by(nombre='Meditación').first()
                yoga_menopausia = Clase.query.filter_by(nombre='Yoga menopausia').first()

                if yoga_integral and meditacion and yoga_menopausia:
                    horarios_creados = 0

                    # Lunes a Viernes: 10:00-11:30 Yoga Integral
                    for dia in range(5):
                        horario = HorarioSemanal(
                            clase_id=yoga_integral.id,
                            dia_semana=dia,
                            hora_inicio=time(10, 0),
                            hora_fin=time(11, 30),
                            instructor='Minouche'
                        )
                        db.session.add(horario)
                        horarios_creados += 1

                    # Lunes a Viernes: 19:30-20:45 Yoga Integral
                    for dia in range(5):
                        horario = HorarioSemanal(
                            clase_id=yoga_integral.id,
                            dia_semana=dia,
                            hora_inicio=time(19, 30),
                            hora_fin=time(20, 45),
                            instructor='Minouche'
                        )
                        db.session.add(horario)
                        horarios_creados += 1

                    # Solo Lunes: 17:00-18:15 Yoga Menopausia
                    horario = HorarioSemanal(
                        clase_id=yoga_menopausia.id,
                        dia_semana=0,  # Lunes
                        hora_inicio=time(17, 0),
                        hora_fin=time(18, 15),
                        instructor='Minouche'
                    )
                    db.session.add(horario)
                    horarios_creados += 1

                    db.session.commit()
                    if not modo_web:
                        print(f"   - {horarios_creados} horarios creados")
                else:
                    if not modo_web:
                        print("   ! No se encontraron todas las clases necesarias")
            else:
                if not modo_web:
                    print(f"   - Ya existen {horarios_existentes} horarios en el sistema")

            # 3. ALUMNOS
            if not modo_web:
                print("3. Creando alumnos...")

            # Función para generar DNI español válido
            def generar_dni_valido():
                """Genera un DNI español válido con letra de control correcta"""
                letras_dni = 'TRWAGMYFPDXBNJZSQVHLCKE'
                numero = random.randint(10000000, 99999999)
                letra = letras_dni[numero % 23]
                return f'{numero}{letra}'

            alumnos_iniciales = Alumno.query.count()
            if alumnos_iniciales < 10:
                nombres = ['Ana', 'María', 'Carmen', 'Laura', 'Isabel', 'Pedro', 'Juan', 'Carlos', 'Miguel', 'José']
                apellidos = ['García', 'Martínez', 'López', 'Sánchez', 'González', 'Rodríguez', 'Fernández', 'Pérez']
                tipos_cuota = ['1_clase_semanal', '2_clases_semanal', 'plana', '1_clase_bimensual', '2_clases_bimensual']

                alumnos_creados = []
                for i in range(10 - alumnos_iniciales):
                    nombre = random.choice(nombres)
                    apellido = random.choice(apellidos)

                    alumno = Alumno(
                        nombre=nombre,
                        apellido=apellido,
                        email=f'{nombre.lower()}.{apellido.lower()}{i}@test.com',
                        telefono=f'6{random.randint(10000000, 99999999)}',
                        fecha_nacimiento=date.today() - timedelta(days=random.randint(9125, 21900)),  # 25-60 años
                        tipo_cuota=random.choice(tipos_cuota),
                        matricula_pagada=random.choice([True, True, True, False]),  # 75% tienen matrícula pagada
                        activo=True,
                        dni=generar_dni_valido()
                    )
                    db.session.add(alumno)
                    alumnos_creados.append(alumno)

                db.session.commit()
                if not modo_web:
                    print(f"   - {len(alumnos_creados)} alumnos creados")

            # 4. ASISTENCIAS
            if not modo_web:
                print("4. Generando asistencias...")

            alumnos = Alumno.query.filter_by(activo=True).all()
            horarios = HorarioSemanal.query.all()

            if alumnos and horarios and Asistencia.query.count() < 50:
                asistencias_creadas = 0
                # Crear asistencias para las últimas 4 semanas
                hoy = date.today()

                for semanas_atras in range(4):
                    fecha_inicio_semana = hoy - timedelta(weeks=semanas_atras, days=hoy.weekday())

                    for horario in horarios:
                        # Fecha de la clase en esa semana
                        fecha_clase = fecha_inicio_semana + timedelta(days=horario.dia_semana)

                        # Solo crear asistencias para fechas pasadas
                        if fecha_clase <= hoy:
                            # Seleccionar alumnos aleatorios (60-90% de asistencia)
                            num_asistentes = random.randint(int(len(alumnos) * 0.6), int(len(alumnos) * 0.9))
                            alumnos_asistentes = random.sample(alumnos, num_asistentes)

                            for alumno in alumnos_asistentes:
                                # Verificar que no exista ya
                                asistencia_existe = Asistencia.query.filter_by(
                                    alumno_id=alumno.id,
                                    horario_id=horario.id,
                                    fecha_clase=fecha_clase
                                ).first()

                                if not asistencia_existe:
                                    asistencia = Asistencia(
                                        alumno_id=alumno.id,
                                        horario_id=horario.id,
                                        fecha_clase=fecha_clase,
                                        presente=True
                                    )
                                    db.session.add(asistencia)
                                    asistencias_creadas += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {asistencias_creadas} asistencias creadas")

            # 5. CLIENTES PARA FACTURACIÓN
            if not modo_web:
                print("5. Creando clientes...")

            if Cliente.query.count() < 5:
                alumnos_para_clientes = Alumno.query.limit(5).all()

                clientes_data = [
                    {
                        'nombre': 'María García López',
                        'nif_cif': '12345678A',
                        'direccion': 'Calle Mayor 15',
                        'codigo_postal': '28001',
                        'ciudad': 'Madrid',
                        'provincia': 'Madrid',
                        'email': 'maria.garcia@email.com',
                        'telefono': '666111222',
                        'tipo_cliente': 'particular',
                        'alumno_id': alumnos_para_clientes[0].id if len(alumnos_para_clientes) > 0 else None
                    },
                    {
                        'nombre': 'Centro Deportivo Wellness SL',
                        'nif_cif': 'B87654321',
                        'direccion': 'Avenida de la Salud 42',
                        'codigo_postal': '28002',
                        'ciudad': 'Madrid',
                        'provincia': 'Madrid',
                        'email': 'admin@wellness.com',
                        'telefono': '917555333',
                        'tipo_cliente': 'empresa'
                    },
                    {
                        'nombre': 'Juan Pérez Martínez',
                        'nif_cif': '87654321B',
                        'direccion': 'Plaza del Sol 8',
                        'codigo_postal': '28013',
                        'ciudad': 'Madrid',
                        'provincia': 'Madrid',
                        'email': 'juan.perez@email.com',
                        'telefono': '655444333',
                        'tipo_cliente': 'autonomo',
                        'alumno_id': alumnos_para_clientes[1].id if len(alumnos_para_clientes) > 1 else None
                    },
                    {
                        'nombre': 'Ana Rodríguez Sánchez',
                        'nif_cif': '23456789C',
                        'direccion': 'Calle de la Paz 23',
                        'codigo_postal': '28004',
                        'ciudad': 'Madrid',
                        'provincia': 'Madrid',
                        'email': 'ana.rodriguez@email.com',
                        'telefono': '644555666',
                        'tipo_cliente': 'particular',
                        'alumno_id': alumnos_para_clientes[2].id if len(alumnos_para_clientes) > 2 else None
                    },
                    {
                        'nombre': 'Ayuntamiento de Madrid',
                        'nif_cif': 'P2807900B',
                        'direccion': 'Plaza de la Villa 5',
                        'codigo_postal': '28005',
                        'ciudad': 'Madrid',
                        'provincia': 'Madrid',
                        'email': 'cultura@madrid.es',
                        'telefono': '914800000',
                        'tipo_cliente': 'empresa'
                    }
                ]

                clientes_creados = 0
                for cliente_data in clientes_data:
                    if not Cliente.query.filter_by(nif_cif=cliente_data['nif_cif']).first():
                        cliente = Cliente(**cliente_data)
                        db.session.add(cliente)
                        clientes_creados += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {clientes_creados} clientes creados")

            # 6. FACTURAS EMITIDAS
            if not modo_web:
                print("6. Creando facturas emitidas...")

            clientes = Cliente.query.all()
            if clientes and FacturaEmitida.query.count() < 10:
                facturas_creadas = 0
                conceptos = [
                    ('Clase de Yoga Integral - Mes completo', 70.00),
                    ('Taller de Meditación', 45.00),
                    ('Clase de Yoga para Embarazadas', 65.00),
                    ('Sesión individual de Yoga', 50.00),
                    ('Curso de Yoga (4 sesiones)', 120.00),
                    ('Clase de Yoga Menopausia', 60.00)
                ]

                for mes_atras in range(6):
                    fecha_base = date.today() - timedelta(days=30 * mes_atras)
                    num_facturas = random.randint(2, 4)

                    for _ in range(num_facturas):
                        cliente = random.choice(clientes)

                        factura = FacturaEmitida(
                            serie='A',
                            fecha_emision=fecha_base - timedelta(days=random.randint(0, 25)),
                            fecha_prestacion=fecha_base - timedelta(days=random.randint(0, 25)),
                            cliente_id=cliente.id,
                            exenta_iva=True,
                            tipo_iva=0.0,
                            tipo_retencion=7.0 if cliente.tipo_cliente in ['empresa', 'autonomo'] else 0.0,
                            motivo_exencion=config_fiscal.texto_exencion_iva,
                            base_imponible=0,
                            total=0
                        )

                        factura.generar_numero_factura()
                        db.session.add(factura)
                        db.session.flush()

                        num_lineas = random.randint(1, 3)
                        for i in range(num_lineas):
                            concepto, precio = random.choice(conceptos)
                            cantidad = random.randint(1, 2)

                            linea = LineaFactura(
                                factura_id=factura.id,
                                orden=i,
                                descripcion=concepto,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=cantidad * precio
                            )
                            db.session.add(linea)

                        factura.calcular_totales()
                        factura.estado = random.choice(['emitida', 'pagada', 'pagada', 'pagada'])

                        if factura.estado == 'pagada':
                            factura.fecha_pago = factura.fecha_emision + timedelta(days=random.randint(1, 15))
                            factura.metodo_pago = random.choice(['transferencia', 'efectivo', 'tarjeta'])

                        facturas_creadas += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {facturas_creadas} facturas emitidas creadas")

            # 7. CATEGORÍAS DE GASTOS
            if not modo_web:
                print("7. Verificando categorías de gastos...")

            categorias_data = [
                {'nombre': 'Alquiler', 'color': '#dc3545'},
                {'nombre': 'Suministros', 'color': '#ffc107'},
                {'nombre': 'Material', 'color': '#28a745'},
                {'nombre': 'Marketing', 'color': '#007bff'},
                {'nombre': 'Formación', 'color': '#6f42c1'},
                {'nombre': 'Seguros', 'color': '#fd7e14'},
                {'nombre': 'Mantenimiento', 'color': '#20c997'},
                {'nombre': 'Otros', 'color': '#6c757d'}
            ]

            for cat_data in categorias_data:
                if not CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first():
                    categoria = CategoriaGasto(**cat_data)
                    db.session.add(categoria)

            db.session.commit()

            # 8. PROVEEDORES
            if not modo_web:
                print("8. Creando proveedores...")

            if Proveedor.query.count() < 5:
                proveedores_data = [
                    {
                        'nombre': 'Suministros Yoga Spain SL',
                        'cif_nif': 'B12345678',
                        'direccion': 'Polígono Industrial Las Rozas',
                        'telefono': '918765432',
                        'email': 'ventas@yogasuministros.es',
                        'contacto_principal': 'Carlos Martínez'
                    },
                    {
                        'nombre': 'Inmobiliaria Centro SL',
                        'cif_nif': 'B87654321',
                        'direccion': 'Gran Vía 45',
                        'telefono': '915551234',
                        'email': 'info@inmobiliariacentro.es',
                        'contacto_principal': 'Laura Gómez'
                    },
                    {
                        'nombre': 'Iberdrola SA',
                        'cif_nif': 'A48010615',
                        'direccion': 'Plaza Euskadi 5, Bilbao',
                        'telefono': '900225522',
                        'email': 'clientes@iberdrola.es',
                        'contacto_principal': 'Atención al Cliente'
                    },
                    {
                        'nombre': 'Material Deportivo Pro',
                        'cif_nif': 'B23456789',
                        'direccion': 'Calle del Deporte 12',
                        'telefono': '916667788',
                        'email': 'pedidos@matdeportivo.com',
                        'contacto_principal': 'Pedro Sánchez'
                    },
                    {
                        'nombre': 'Seguros Mapfre',
                        'cif_nif': 'A28141935',
                        'direccion': 'Carretera de Pozuelo 52, Madrid',
                        'telefono': '913581100',
                        'email': 'empresas@mapfre.com',
                        'contacto_principal': 'Departamento Empresas'
                    }
                ]

                proveedores_creados = 0
                for prov_data in proveedores_data:
                    if not Proveedor.query.filter_by(cif_nif=prov_data['cif_nif']).first():
                        proveedor = Proveedor(**prov_data)
                        db.session.add(proveedor)
                        proveedores_creados += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {proveedores_creados} proveedores creados")

            # 9. GASTOS FIJOS
            if not modo_web:
                print("9. Creando gastos fijos...")

            if GastoFijo.query.count() < 3:
                proveedores = Proveedor.query.all()
                categorias = CategoriaGasto.query.all()

                gastos_fijos_data = [
                    {
                        'nombre': 'Alquiler del Local',
                        'descripcion': 'Alquiler mensual del local de la escuela',
                        'proveedor_id': next((p.id for p in proveedores if 'Inmobiliaria' in p.nombre), None),
                        'categoria_id': next((c.id for c in categorias if c.nombre == 'Alquiler'), categorias[0].id),
                        'importe': 950.00,
                        'frecuencia': 'mensual',
                        'dia_cargo': 1,
                        'fecha_inicio': date.today() - timedelta(days=180)
                    },
                    {
                        'nombre': 'Suministro Eléctrico',
                        'descripcion': 'Factura de luz mensual',
                        'proveedor_id': next((p.id for p in proveedores if 'Iberdrola' in p.nombre), None),
                        'categoria_id': next((c.id for c in categorias if c.nombre == 'Suministros'), categorias[0].id),
                        'importe': 120.00,
                        'frecuencia': 'mensual',
                        'dia_cargo': 5,
                        'fecha_inicio': date.today() - timedelta(days=180)
                    },
                    {
                        'nombre': 'Seguro de Responsabilidad Civil',
                        'descripcion': 'Seguro anual del negocio',
                        'proveedor_id': next((p.id for p in proveedores if 'Mapfre' in p.nombre), None),
                        'categoria_id': next((c.id for c in categorias if c.nombre == 'Seguros'), categorias[0].id),
                        'importe': 450.00,
                        'frecuencia': 'anual',
                        'dia_cargo': 1,
                        'fecha_inicio': date.today() - timedelta(days=180)
                    }
                ]

                gastos_creados = 0
                for gasto_data in gastos_fijos_data:
                    gasto = GastoFijo(**gasto_data)
                    db.session.add(gasto)
                    gastos_creados += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {gastos_creados} gastos fijos creados")

            # 10. FACTURAS DE PROVEEDORES
            if not modo_web:
                print("10. Creando facturas de proveedores...")

            proveedores = Proveedor.query.all()
            categorias = CategoriaGasto.query.all()

            if proveedores and categorias and FacturaProveedor.query.count() < 10:
                prov_categorias = {
                    'Suministros Yoga Spain SL': 'Material',
                    'Inmobiliaria Centro SL': 'Alquiler',
                    'Iberdrola SA': 'Suministros',
                    'Material Deportivo Pro': 'Material',
                    'Seguros Mapfre': 'Seguros'
                }

                facturas_prov_creadas = 0
                for mes_atras in range(6):
                    fecha_base = date.today() - timedelta(days=30 * mes_atras)
                    num_facturas = random.randint(3, 5)

                    for _ in range(num_facturas):
                        proveedor = random.choice(proveedores)
                        cat_nombre = prov_categorias.get(proveedor.nombre, 'Otros')
                        categoria = next((c for c in categorias if c.nombre == cat_nombre), categorias[0])

                        if categoria.nombre == 'Alquiler':
                            importe_base = random.choice([800, 900, 950, 1000])
                        elif categoria.nombre == 'Suministros':
                            importe_base = random.uniform(50, 150)
                        elif categoria.nombre == 'Material':
                            importe_base = random.uniform(100, 500)
                        elif categoria.nombre == 'Seguros':
                            importe_base = random.uniform(150, 300)
                        else:
                            importe_base = random.uniform(50, 300)

                        fecha_factura = fecha_base - timedelta(days=random.randint(0, 28))
                        fecha_vencimiento = fecha_factura + timedelta(days=30)

                        factura_prov = FacturaProveedor(
                            numero_factura=f'F-{random.randint(1000, 9999)}',
                            proveedor_id=proveedor.id,
                            categoria_id=categoria.id,
                            fecha_factura=fecha_factura,
                            fecha_vencimiento=fecha_vencimiento,
                            importe_sin_iva=importe_base,
                            iva=21.0,
                            importe_total=importe_base * 1.21,
                            descripcion=f'Servicio/suministro del mes {fecha_factura.strftime("%B %Y")}',
                            estado=random.choice(['pagada', 'pagada', 'pendiente']),
                            metodo_pago=random.choice(['transferencia', 'domiciliacion', 'tarjeta'])
                        )

                        if factura_prov.estado == 'pagada':
                            factura_prov.fecha_pago = fecha_factura + timedelta(days=random.randint(5, 25))

                        db.session.add(factura_prov)
                        facturas_prov_creadas += 1

                db.session.commit()
                if not modo_web:
                    print(f"   - {facturas_prov_creadas} facturas de proveedores creadas")

            if not modo_web:
                print()
                print("=" * 60)
                print("DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
                print("=" * 60)
                print()
                print("RESUMEN:")
                print(f"  - Alumnos: {Alumno.query.count()}")
                print(f"  - Horarios: {HorarioSemanal.query.count()}")
                print(f"  - Asistencias: {Asistencia.query.count()}")
                print(f"  - Clientes: {Cliente.query.count()}")
                print(f"  - Facturas emitidas: {FacturaEmitida.query.count()}")
                print(f"  - Proveedores: {Proveedor.query.count()}")
                print(f"  - Gastos fijos: {GastoFijo.query.count()}")
                print(f"  - Facturas proveedores: {FacturaProveedor.query.count()}")
                print()

            return True

        except Exception as e:
            if not modo_web:
                print(f"Error: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    cargar_datos_completos(modo_web=False)
