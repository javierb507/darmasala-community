from datetime import date

import pytest

from models import db, FacturaEmitida, LineaFactura, Cliente


def _factura(app, serie='A', base=100.0, exenta=True, retencion=0.0, iva=0.0):
    """Crea factura con una línea a nivel de modelo y devuelve su id."""
    with app.app_context():
        cliente = Cliente.query.first()
        f = FacturaEmitida(serie=serie, fecha_emision=date(2026, 7, 20),
                           fecha_prestacion=date(2026, 7, 20), cliente_id=cliente.id,
                           exenta_iva=exenta, tipo_iva=iva, tipo_retencion=retencion,
                           base_imponible=0, total=0)
        f.generar_numero_factura()
        db.session.add(f)
        db.session.flush()
        linea = LineaFactura(factura_id=f.id, orden=0, descripcion='Clases yoga',
                             cantidad=1, precio_unitario=base)
        linea.calcular_subtotal()
        db.session.add(linea)
        f.calcular_totales()
        db.session.commit()
        return f.id


def test_numeracion_correlativa_por_serie(app):
    id1 = _factura(app, serie='A')
    id2 = _factura(app, serie='A')
    id3 = _factura(app, serie='B')
    with app.app_context():
        f1, f2, f3 = (db.session.get(FacturaEmitida, i) for i in (id1, id2, id3))
        assert f1.numero_completo == 'A/2026/0001'
        assert f2.numero_completo == 'A/2026/0002'
        assert f3.numero_completo == 'B/2026/0001'


def test_totales_exenta_con_irpf(app):
    fid = _factura(app, base=100.0, exenta=True, retencion=7.0)
    with app.app_context():
        f = db.session.get(FacturaEmitida, fid)
        assert f.base_imponible == 100.0
        assert f.cuota_iva == 0.0
        assert f.cuota_retencion == pytest.approx(7.0)
        assert f.total == pytest.approx(93.0)


def test_totales_con_iva_sin_exencion(app):
    fid = _factura(app, base=100.0, exenta=False, iva=21.0, retencion=7.0)
    with app.app_context():
        f = db.session.get(FacturaEmitida, fid)
        assert f.cuota_iva == 21.0
        assert f.total == 114.0


def test_crear_factura_via_ruta(app, auth_client):
    with app.app_context():
        cliente_id = Cliente.query.first().id
    r = auth_client.post('/facturas-emitidas/nueva', data={
        'serie': 'A', 'fecha_emision': '2026-07-20', 'fecha_prestacion': '2026-07-20',
        'cliente_id': str(cliente_id), 'exenta_iva': 'on', 'tipo_iva': '0',
        'tipo_retencion': '7', 'lineas_count': '1',
        'linea_0_descripcion': 'Clases julio',
        'linea_0_cantidad': '1', 'linea_0_precio': '80'})
    assert r.status_code == 302
    with app.app_context():
        f = FacturaEmitida.query.first()
        assert f is not None
        assert f.numero_completo == 'A/2026/0001'
        assert f.total == pytest.approx(80 - 80 * 0.07)
