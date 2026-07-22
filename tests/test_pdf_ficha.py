"""Tests del PDF descargable con la ficha completa del alumno (issue #37)."""
from datetime import date, timedelta


def test_pdf_ficha_descarga(app, auth_client):
    with app.app_context():
        from models import db, Alumno, Pago, Bono
        alumno = Alumno.query.first()
        aid = alumno.id
        # Datos representativos: un pago y un bono
        db.session.add(Pago(alumno_id=aid, mes='2026-07', monto=40.0,
                            tipo_pago='cuota', metodo_pago='efectivo'))
        db.session.add(Bono(alumno_id=aid, clases_totales=10, clases_consumidas=3,
                            fecha_compra=date.today(),
                            fecha_caducidad=date.today() + timedelta(days=90),
                            precio=80.0))
        db.session.commit()

    r = auth_client.get(f'/alumnos/{aid}/pdf')
    assert r.status_code == 200
    assert r.mimetype == 'application/pdf'
    assert r.data.startswith(b'%PDF')
    assert len(r.data) > 1000


def test_pdf_ficha_requiere_login(client):
    r = client.get('/alumnos/1/pdf')
    assert r.status_code == 302  # redirige a login
