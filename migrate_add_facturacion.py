"""
Script para crear las tablas de facturación en la base de datos
"""
from app import app, db, Cliente, ConfiguracionFiscal, FacturaEmitida, LineaFactura

def create_facturacion_tables():
    """Crea las tablas necesarias para el sistema de facturación"""
    with app.app_context():
        print("=" * 60)
        print("CREACIÓN DE TABLAS DE FACTURACIÓN")
        print("=" * 60)
        print()

        # Crear todas las tablas (solo crea las que no existen)
        db.create_all()

        print("OK - Tablas creadas exitosamente:")
        print("  - cliente")
        print("  - configuracion_fiscal")
        print("  - factura_emitida")
        print("  - linea_factura")
        print()

        # Verificar si existe configuración fiscal, si no crear una por defecto
        config_fiscal = ConfiguracionFiscal.query.first()
        if not config_fiscal:
            config_fiscal = ConfiguracionFiscal(
                nombre_empresa='Atma Suddhi - Escuela de Yoga',
                nif='12345678Z',  # CAMBIAR POR EL NIF REAL
                direccion_fiscal='Calle Ejemplo, 123',  # CAMBIAR POR DIRECCION REAL
                codigo_postal='28001',
                ciudad='Madrid',
                provincia='Madrid',
                telefono='',
                email='',
                epigrafe_iae='',
                regimen_iva='exento',
                tipo_retencion_default=7.0,
                exento_iva=True,
                texto_exencion_iva='Exento de IVA segun art. 20.Uno.9 de la Ley 37/1992',
                serie_factura_default='A',
                pie_factura='Conserve esta factura durante 4 anos segun la normativa fiscal vigente.'
            )
            db.session.add(config_fiscal)
            db.session.commit()

            print("OK - Configuracion fiscal creada (IMPORTANTE: Actualizar con datos reales)")
            print()

        print("=" * 60)
        print("PROCESO COMPLETADO")
        print("=" * 60)
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Actualizar la configuración fiscal con los datos reales del negocio")
        print("2. Crear clientes para poder emitir facturas")
        print("3. Configurar las rutas y vistas de facturación")
        print()

if __name__ == "__main__":
    create_facturacion_tables()
