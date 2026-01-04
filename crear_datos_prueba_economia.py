"""
Script para crear datos de prueba para el módulo de gestión económica
"""
from app import app, db, Cliente, FacturaEmitida, LineaFactura, ConfiguracionFiscal, Proveedor, FacturaProveedor, CategoriaGasto, Alumno
from datetime import datetime, date, timedelta
import random

def crear_datos_prueba_economia():
    """Crea datos de prueba completos para la gestión económica"""
    with app.app_context():
        print("=" * 60)
        print("CREACION DE DATOS DE PRUEBA - GESTION ECONOMICA")
        print("=" * 60)
        print()

        # Crear todas las tablas si no existen
        db.create_all()
        print("Tablas de base de datos verificadas/creadas")
        print()

        # Crear configuración fiscal si no existe
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
                texto_exencion_iva='Exento de IVA segun art. 20.Uno.9 de la Ley 37/1992',
                serie_factura_default='A'
            )
            db.session.add(config_fiscal)
            db.session.commit()
            print("Configuracion fiscal creada")
            print()

        # Verificar si ya existen datos
        if FacturaEmitida.query.count() > 0:
            print("Ya existen facturas emitidas en la base de datos.")
            respuesta = input("Deseas eliminar todos los datos de economia y crear nuevos? (s/n): ")
            if respuesta.lower() != 's':
                print("Operacion cancelada.")
                return

            # Eliminar datos existentes
            print("Eliminando datos existentes...")
            LineaFactura.query.delete()
            FacturaEmitida.query.delete()
            Cliente.query.delete()
            FacturaProveedor.query.delete()
            Proveedor.query.delete()
            db.session.commit()
            print("Datos eliminados.")
            print()

        # 1. CLIENTES PARA FACTURACION
        print("1. Creando clientes...")

        # Obtener algunos alumnos para vincular
        alumnos = Alumno.query.limit(5).all()

        clientes_data = [
            {
                'nombre': 'Maria Garcia Lopez',
                'nif_cif': '12345678A',
                'direccion': 'Calle Mayor 15',
                'codigo_postal': '28001',
                'ciudad': 'Madrid',
                'provincia': 'Madrid',
                'email': 'maria.garcia@email.com',
                'telefono': '666111222',
                'tipo_cliente': 'particular',
                'alumno_id': alumnos[0].id if len(alumnos) > 0 else None
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
                'nombre': 'Juan Perez Martinez',
                'nif_cif': '87654321B',
                'direccion': 'Plaza del Sol 8',
                'codigo_postal': '28013',
                'ciudad': 'Madrid',
                'provincia': 'Madrid',
                'email': 'juan.perez@email.com',
                'telefono': '655444333',
                'tipo_cliente': 'autonomo',
                'alumno_id': alumnos[1].id if len(alumnos) > 1 else None
            },
            {
                'nombre': 'Ana Rodriguez Sanchez',
                'nif_cif': '23456789C',
                'direccion': 'Calle de la Paz 23',
                'codigo_postal': '28004',
                'ciudad': 'Madrid',
                'provincia': 'Madrid',
                'email': 'ana.rodriguez@email.com',
                'telefono': '644555666',
                'tipo_cliente': 'particular',
                'alumno_id': alumnos[2].id if len(alumnos) > 2 else None
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

        clientes_creados = []
        for cliente_data in clientes_data:
            if not Cliente.query.filter_by(nif_cif=cliente_data['nif_cif']).first():
                cliente = Cliente(**cliente_data)
                db.session.add(cliente)
                clientes_creados.append(cliente)

        db.session.commit()
        print(f"   - {len(clientes_creados)} clientes creados")

        # 2. FACTURAS EMITIDAS A CLIENTES
        print("2. Creando facturas emitidas...")

        config_fiscal = ConfiguracionFiscal.query.first()
        if not config_fiscal:
            print("   ERROR: No hay configuracion fiscal. Ejecuta migrate_add_facturacion.py primero")
            return

        clientes = Cliente.query.all()
        facturas_creadas = 0

        # Crear facturas de los últimos 6 meses
        for mes_atras in range(6):
            fecha_base = date.today() - timedelta(days=30 * mes_atras)

            # 2-4 facturas por mes
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

                # Crear líneas de factura
                num_lineas = random.randint(1, 3)
                conceptos = [
                    ('Clase de Yoga Integral - Mes completo', 70.00),
                    ('Taller de Meditacion', 45.00),
                    ('Clase de Yoga para Embarazadas', 65.00),
                    ('Sesion individual de Yoga', 50.00),
                    ('Curso de Yoga (4 sesiones)', 120.00),
                    ('Clase de Yoga Menopausia', 60.00)
                ]

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

                # Calcular totales
                factura.calcular_totales()

                # Asignar estado aleatorio
                estados_posibles = ['emitida', 'pagada', 'pagada', 'pagada']  # Más probabilidad de pagadas
                factura.estado = random.choice(estados_posibles)

                if factura.estado == 'pagada':
                    factura.fecha_pago = factura.fecha_emision + timedelta(days=random.randint(1, 15))
                    factura.metodo_pago = random.choice(['transferencia', 'efectivo', 'tarjeta'])

                facturas_creadas += 1

        db.session.commit()
        print(f"   - {facturas_creadas} facturas emitidas creadas")

        # 3. CATEGORIAS DE GASTOS
        print("3. Creando categorías de gastos...")
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
        print("   - Categorias de gastos creadas/verificadas")

        # 4. PROVEEDORES
        print("4. Creando proveedores...")

        proveedores_data = [
            {
                'nombre': 'Suministros Yoga Spain SL',
                'cif_nif': 'B12345678',
                'direccion': 'Poligono Industrial Las Rozas',
                'telefono': '918765432',
                'email': 'ventas@yogasuministros.es',
                'contacto_principal': 'Carlos Martinez'
            },
            {
                'nombre': 'Inmobiliaria Centro SL',
                'cif_nif': 'B87654321',
                'direccion': 'Gran Via 45',
                'telefono': '915551234',
                'email': 'info@inmobiliariacentro.es',
                'contacto_principal': 'Laura Gomez'
            },
            {
                'nombre': 'Iberdrola SA',
                'cif_nif': 'A48010615',
                'direccion': 'Plaza Euskadi 5, Bilbao',
                'telefono': '900225522',
                'email': 'clientes@iberdrola.es',
                'contacto_principal': 'Atencion al Cliente'
            },
            {
                'nombre': 'Material Deportivo Pro',
                'cif_nif': 'B23456789',
                'direccion': 'Calle del Deporte 12',
                'telefono': '916667788',
                'email': 'pedidos@matdeportivo.com',
                'contacto_principal': 'Pedro Sanchez'
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

        proveedores_creados = []
        for prov_data in proveedores_data:
            if not Proveedor.query.filter_by(cif_nif=prov_data['cif_nif']).first():
                proveedor = Proveedor(**prov_data)
                db.session.add(proveedor)
                proveedores_creados.append(proveedor)

        db.session.commit()
        print(f"   - {len(proveedores_creados)} proveedores creados")

        # 5. FACTURAS DE PROVEEDORES (GASTOS)
        print("5. Creando facturas de proveedores...")

        proveedores = Proveedor.query.all()
        categorias = CategoriaGasto.query.all()
        facturas_prov_creadas = 0

        # Mapeo de proveedores a categorías
        prov_categorias = {
            'Suministros Yoga Spain SL': 'Material',
            'Inmobiliaria Centro SL': 'Alquiler',
            'Iberdrola SA': 'Suministros',
            'Material Deportivo Pro': 'Material',
            'Seguros Mapfre': 'Seguros'
        }

        # Crear facturas de los últimos 6 meses
        for mes_atras in range(6):
            fecha_base = date.today() - timedelta(days=30 * mes_atras)

            # 3-5 facturas de proveedores por mes
            num_facturas = random.randint(3, 5)

            for _ in range(num_facturas):
                proveedor = random.choice(proveedores)

                # Buscar categoría apropiada
                cat_nombre = prov_categorias.get(proveedor.nombre, 'Otros')
                categoria = next((c for c in categorias if c.nombre == cat_nombre), categorias[0])

                # Importes según tipo de gasto
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
        print(f"   - {facturas_prov_creadas} facturas de proveedores creadas")

        print()
        print("=" * 60)
        print("DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("=" * 60)
        print()
        print("RESUMEN:")
        print(f"  - Clientes: {len(clientes_creados)}")
        print(f"  - Facturas emitidas: {facturas_creadas}")
        print(f"  - Proveedores: {len(proveedores_creados)}")
        print(f"  - Facturas de proveedores: {facturas_prov_creadas}")
        print()
        print("Accede a http://localhost:5000/economia para ver el dashboard")
        print()

if __name__ == "__main__":
    crear_datos_prueba_economia()
