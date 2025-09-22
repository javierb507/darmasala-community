#!/usr/bin/env python3
"""
Script para cargar datos de prueba del módulo de contabilidad
Incluye proveedores, categorías de gastos, facturas y gastos fijos de los últimos 3 meses
"""

from app import app, db, CategoriaGasto, Proveedor, GastoFijo, FacturaProveedor, GastoMensual
from datetime import datetime, date, timedelta
import random

def cargar_datos_contabilidad():
    """Cargar datos de prueba para el módulo de contabilidad"""
    
    with app.app_context():
        print("Cargando datos de contabilidad...")
        
        # 1. Crear categorías de gastos
        categorias = [
            {'nombre': 'Servicios Básicos', 'descripcion': 'Luz, agua, gas, internet', 'activo': True},
            {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'activo': True},
            {'nombre': 'Seguros', 'descripcion': 'Seguros del local y responsabilidad civil', 'activo': True},
            {'nombre': 'Mantenimiento', 'descripcion': 'Reparaciones y mantenimiento del local', 'activo': True},
            {'nombre': 'Marketing', 'descripcion': 'Publicidad, redes sociales, material promocional', 'activo': True},
            {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, cinturones, etc.', 'activo': True},
            {'nombre': 'Formación', 'descripcion': 'Cursos, talleres, certificaciones', 'activo': True},
            {'nombre': 'Administración', 'descripcion': 'Gestoría, asesoría, software', 'activo': True},
            {'nombre': 'Transporte', 'descripcion': 'Combustible, transporte público', 'activo': True},
            {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'activo': True}
        ]
        
        for cat_data in categorias:
            categoria = CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria:
                categoria = CategoriaGasto(**cat_data)
                db.session.add(categoria)
        
        db.session.commit()
        print("✓ Categorías de gastos creadas")
        
        # 2. Crear proveedores
        proveedores = [
            {
                'nombre': 'Endesa Energía',
                'cif_nif': 'A81948009',
                'direccion': 'Calle de la Energía, 123, Madrid',
                'telefono': '900 123 456',
                'email': 'facturacion@endesa.es',
                'contacto_principal': 'Departamento de Facturación',
                'notas': 'Proveedor de electricidad',
                'activo': True
            },
            {
                'nombre': 'Canal de Isabel II',
                'cif_nif': 'G28000000',
                'direccion': 'Calle de Santa Engracia, 125, Madrid',
                'telefono': '900 100 100',
                'email': 'atencion@canaldeisabelsegunda.es',
                'contacto_principal': 'Atención al Cliente',
                'notas': 'Proveedor de agua',
                'activo': True
            },
            {
                'nombre': 'Gas Natural Fenosa',
                'cif_nif': 'A81948009',
                'direccion': 'Av. de San Luis, 77, Madrid',
                'telefono': '900 750 750',
                'email': 'clientes@gasnaturalfenosa.com',
                'contacto_principal': 'Atención al Cliente',
                'notas': 'Proveedor de gas',
                'activo': True
            },
            {
                'nombre': 'Movistar',
                'cif_nif': 'A78953125',
                'direccion': 'Ronda de la Comunicación, s/n, Madrid',
                'telefono': '1004',
                'email': 'atencion@movistar.es',
                'contacto_principal': 'Atención al Cliente',
                'notas': 'Proveedor de internet y telefonía',
                'activo': True
            },
            {
                'nombre': 'Propietario Local - María González',
                'cif_nif': '12345678A',
                'direccion': 'Calle del Yoga, 45, Madrid',
                'telefono': '666 123 456',
                'email': 'maria.gonzalez@email.com',
                'contacto_principal': 'María González',
                'notas': 'Propietaria del local',
                'activo': True
            },
            {
                'nombre': 'Mapfre Seguros',
                'cif_nif': 'A08001898',
                'direccion': 'Calle de Alcalá, 9, Madrid',
                'telefono': '900 123 123',
                'email': 'atencion@mapfre.es',
                'contacto_principal': 'Departamento Comercial',
                'notas': 'Seguro de responsabilidad civil y local',
                'activo': True
            },
            {
                'nombre': 'Yoga Material',
                'cif_nif': 'B12345678',
                'direccion': 'Calle de la Paz, 12, Madrid',
                'telefono': '911 234 567',
                'email': 'pedidos@yogamaterial.com',
                'contacto_principal': 'Pedro Martínez',
                'notas': 'Material de yoga y accesorios',
                'activo': True
            },
            {
                'nombre': 'Gestoría Contable SL',
                'cif_nif': 'B87654321',
                'direccion': 'Calle de la Contabilidad, 8, Madrid',
                'telefono': '915 678 901',
                'email': 'info@gestoriacontable.es',
                'contacto_principal': 'Ana López',
                'notas': 'Servicios de gestoría y asesoría fiscal',
                'activo': True
            },
            {
                'nombre': 'Marketing Digital Pro',
                'cif_nif': 'B11223344',
                'direccion': 'Calle Digital, 15, Madrid',
                'telefono': '917 890 123',
                'email': 'hola@marketingdigitalpro.com',
                'contacto_principal': 'Carlos Ruiz',
                'notas': 'Servicios de marketing digital y redes sociales',
                'activo': True
            },
            {
                'nombre': 'Formación Yoga Internacional',
                'cif_nif': 'B55667788',
                'direccion': 'Calle de la Formación, 22, Madrid',
                'telefono': '918 456 789',
                'email': 'info@formacionyoga.com',
                'contacto_principal': 'Sofia Martín',
                'notas': 'Cursos y certificaciones de yoga',
                'activo': True
            }
        ]
        
        for prov_data in proveedores:
            proveedor = Proveedor.query.filter_by(nombre=prov_data['nombre']).first()
            if not proveedor:
                proveedor = Proveedor(**prov_data)
                db.session.add(proveedor)
        
        db.session.commit()
        print("✓ Proveedores creados")
        
        # 3. Crear gastos fijos mensuales
        gastos_fijos = [
            {
                'nombre': 'Alquiler Local',
                'descripcion': 'Alquiler mensual del local',
                'categoria_id': CategoriaGasto.query.filter_by(nombre='Alquiler').first().id,
                'importe': 1200.00,
                'frecuencia': 'mensual',
                'dia_cargo': 1,
                'fecha_inicio': date(2024, 10, 1),
                'fecha_fin': date(2025, 12, 31),
                'activo': True
            },
            {
                'nombre': 'Seguro Responsabilidad Civil',
                'descripcion': 'Seguro de responsabilidad civil anual',
                'categoria_id': CategoriaGasto.query.filter_by(nombre='Seguros').first().id,
                'importe': 300.00,
                'frecuencia': 'anual',
                'dia_cargo': 1,
                'fecha_inicio': date(2024, 1, 1),
                'fecha_fin': date(2024, 12, 31),
                'activo': True
            },
            {
                'nombre': 'Gestoría Contable',
                'descripcion': 'Servicios de gestoría mensual',
                'categoria_id': CategoriaGasto.query.filter_by(nombre='Administración').first().id,
                'importe': 150.00,
                'frecuencia': 'mensual',
                'dia_cargo': 5,
                'fecha_inicio': date(2024, 10, 1),
                'fecha_fin': date(2025, 12, 31),
                'activo': True
            }
        ]
        
        for gasto_data in gastos_fijos:
            gasto = GastoFijo.query.filter_by(nombre=gasto_data['nombre']).first()
            if not gasto:
                gasto = GastoFijo(**gasto_data)
                db.session.add(gasto)
        
        db.session.commit()
        print("✓ Gastos fijos creados")
        
        # 4. Crear facturas de los últimos 3 meses
        hoy = date.today()
        tres_meses_atras = hoy - timedelta(days=90)
        
        # Obtener proveedores y categorías
        proveedores_db = Proveedor.query.filter_by(activo=True).all()
        categorias_db = CategoriaGasto.query.filter_by(activo=True).all()
        
        facturas_ejemplo = [
            # Facturas de electricidad
            {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 85.0, 'iva': 21.0},
            {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 92.0, 'iva': 21.0},
            {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 78.0, 'iva': 21.0},
            
            # Facturas de agua
            {'proveedor': 'Canal de Isabel II', 'categoria': 'Servicios Básicos', 'frecuencia': 'bimensual', 'importe_base': 45.0, 'iva': 21.0},
            {'proveedor': 'Canal de Isabel II', 'categoria': 'Servicios Básicos', 'frecuencia': 'bimensual', 'importe_base': 52.0, 'iva': 21.0},
            
            # Facturas de gas
            {'proveedor': 'Gas Natural Fenosa', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 35.0, 'iva': 21.0},
            {'proveedor': 'Gas Natural Fenosa', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 42.0, 'iva': 21.0},
            {'proveedor': 'Gas Natural Fenosa', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 38.0, 'iva': 21.0},
            
            # Facturas de internet
            {'proveedor': 'Movistar', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 65.0, 'iva': 21.0},
            {'proveedor': 'Movistar', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 65.0, 'iva': 21.0},
            {'proveedor': 'Movistar', 'categoria': 'Servicios Básicos', 'frecuencia': 'mensual', 'importe_base': 65.0, 'iva': 21.0},
            
            # Facturas de alquiler
            {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'frecuencia': 'mensual', 'importe_base': 1200.0, 'iva': 0.0},
            {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'frecuencia': 'mensual', 'importe_base': 1200.0, 'iva': 0.0},
            {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'frecuencia': 'mensual', 'importe_base': 1200.0, 'iva': 0.0},
            
            # Facturas de seguros
            {'proveedor': 'Mapfre Seguros', 'categoria': 'Seguros', 'frecuencia': 'anual', 'importe_base': 300.0, 'iva': 21.0},
            
            # Facturas de material
            {'proveedor': 'Yoga Material', 'categoria': 'Material', 'frecuencia': 'mensual', 'importe_base': 120.0, 'iva': 21.0},
            {'proveedor': 'Yoga Material', 'categoria': 'Material', 'frecuencia': 'mensual', 'importe_base': 85.0, 'iva': 21.0},
            {'proveedor': 'Yoga Material', 'categoria': 'Material', 'frecuencia': 'mensual', 'importe_base': 95.0, 'iva': 21.0},
            
            # Facturas de gestoría
            {'proveedor': 'Gestoría Contable SL', 'categoria': 'Administración', 'frecuencia': 'mensual', 'importe_base': 150.0, 'iva': 21.0},
            {'proveedor': 'Gestoría Contable SL', 'categoria': 'Administración', 'frecuencia': 'mensual', 'importe_base': 150.0, 'iva': 21.0},
            {'proveedor': 'Gestoría Contable SL', 'categoria': 'Administración', 'frecuencia': 'mensual', 'importe_base': 150.0, 'iva': 21.0},
            
            # Facturas de marketing
            {'proveedor': 'Marketing Digital Pro', 'categoria': 'Marketing', 'frecuencia': 'mensual', 'importe_base': 200.0, 'iva': 21.0},
            {'proveedor': 'Marketing Digital Pro', 'categoria': 'Marketing', 'frecuencia': 'mensual', 'importe_base': 180.0, 'iva': 21.0},
            {'proveedor': 'Marketing Digital Pro', 'categoria': 'Marketing', 'frecuencia': 'mensual', 'importe_base': 220.0, 'iva': 21.0},
            
            # Facturas de formación
            {'proveedor': 'Formación Yoga Internacional', 'categoria': 'Formación', 'frecuencia': 'trimestral', 'importe_base': 450.0, 'iva': 21.0},
        ]
        
        # Generar fechas para las facturas
        fecha_actual = tres_meses_atras
        numero_factura = 1
        
        for factura_data in facturas_ejemplo:
            # Buscar proveedor y categoría
            proveedor = Proveedor.query.filter_by(nombre=factura_data['proveedor']).first()
            categoria = CategoriaGasto.query.filter_by(nombre=factura_data['categoria']).first()
            
            if proveedor and categoria:
                # Calcular fecha de vencimiento (30 días después)
                fecha_vencimiento = fecha_actual + timedelta(days=30)
                
                # Crear factura
                factura = FacturaProveedor(
                    numero_factura=f"FAC-{numero_factura:04d}",
                    proveedor_id=proveedor.id,
                    categoria_id=categoria.id,
                    fecha_factura=fecha_actual,
                    fecha_vencimiento=fecha_vencimiento,
                    importe_sin_iva=factura_data['importe_base'],
                    iva=factura_data['iva'],
                    importe_total=factura_data['importe_base'] * (1 + factura_data['iva'] / 100),
                    descripcion=f"Factura de {factura_data['categoria'].lower()} - {fecha_actual.strftime('%B %Y')}",
                    estado='pagada' if fecha_actual < hoy - timedelta(days=15) else 'pendiente',
                    fecha_pago=fecha_actual + timedelta(days=random.randint(1, 15)) if fecha_actual < hoy - timedelta(days=15) else None,
                    metodo_pago=random.choice(['transferencia', 'efectivo', 'tarjeta']) if fecha_actual < hoy - timedelta(days=15) else None
                )
                
                db.session.add(factura)
                numero_factura += 1
                
                # Avanzar fecha según frecuencia
                if factura_data['frecuencia'] == 'mensual':
                    fecha_actual += timedelta(days=30)
                elif factura_data['frecuencia'] == 'bimensual':
                    fecha_actual += timedelta(days=60)
                elif factura_data['frecuencia'] == 'trimestral':
                    fecha_actual += timedelta(days=90)
                elif factura_data['frecuencia'] == 'anual':
                    fecha_actual += timedelta(days=365)
        
        db.session.commit()
        print("✓ Facturas de los últimos 3 meses creadas")
        
        # 5. Crear gastos mensuales variables
        gastos_mensuales = [
            {'categoria': 'Mantenimiento', 'descripcion': 'Reparación grifo baño', 'importe': 85.50, 'fecha': hoy - timedelta(days=15)},
            {'categoria': 'Mantenimiento', 'descripcion': 'Limpieza profunda local', 'importe': 120.00, 'fecha': hoy - timedelta(days=45)},
            {'categoria': 'Transporte', 'descripcion': 'Combustible para desplazamientos', 'importe': 45.30, 'fecha': hoy - timedelta(days=20)},
            {'categoria': 'Transporte', 'descripcion': 'Taxi para reunión', 'importe': 25.00, 'fecha': hoy - timedelta(days=35)},
            {'categoria': 'Otros', 'descripcion': 'Material de oficina', 'importe': 35.75, 'fecha': hoy - timedelta(days=25)},
            {'categoria': 'Otros', 'descripcion': 'Regalo cumpleaños alumna', 'importe': 15.00, 'fecha': hoy - timedelta(days=10)},
        ]
        
        for gasto_data in gastos_mensuales:
            gasto = GastoMensual(
                concepto=gasto_data['descripcion'],
                categoria=gasto_data['categoria'],
                importe=gasto_data['importe'],
                fecha=gasto_data['fecha'],
                pagado=True,
                metodo_pago=random.choice(['efectivo', 'tarjeta', 'transferencia'])
            )
            db.session.add(gasto)
        
        db.session.commit()
        print("✓ Gastos mensuales variables creados")
        
        print("\n🎉 ¡Datos de contabilidad cargados exitosamente!")
        print(f"📊 Resumen:")
        print(f"   - {len(categorias)} categorías de gastos")
        print(f"   - {len(proveedores)} proveedores")
        print(f"   - {len(gastos_fijos)} gastos fijos")
        print(f"   - {numero_factura - 1} facturas de los últimos 3 meses")
        print(f"   - {len(gastos_mensuales)} gastos variables")

if __name__ == '__main__':
    cargar_datos_contabilidad()
