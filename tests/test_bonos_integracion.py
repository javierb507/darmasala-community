"""Tests de integración: consumo de bonos vía registro de asistencia por lotes."""
from datetime import date, datetime

from models import db, Alumno, Bono, Asistencia, HorarioSemanal


def _bonista(app):
    with app.app_context():
        a = Alumno(nombre='Lote', apellido='Bono', email='lotebono@t.local',
                   tipo_cuota='clase_suelta', fecha_registro=datetime(2026, 1, 1))
        db.session.add(a)
        db.session.flush()
        b = Bono(alumno_id=a.id, clases_totales=10, fecha_compra=date(2026, 1, 5), precio=80)
        db.session.add(b)
        db.session.commit()
        return a.id, HorarioSemanal.query.first().id, b.id


def test_lote_consume_bono(app, auth_client):
    aid, hid, bid = _bonista(app)
    auth_client.post('/api/asistencias/registrar-lote', json={
        'horario_id': hid, 'fecha': '2026-03-02',
        'registro': [{'alumno_id': aid, 'asistio': True}]})
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 1


def test_lote_repetido_no_doble_consumo(app, auth_client):
    aid, hid, bid = _bonista(app)
    payload = {'horario_id': hid, 'fecha': '2026-03-02',
               'registro': [{'alumno_id': aid, 'asistio': True}]}
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 1


def test_lote_flip_devuelve(app, auth_client):
    aid, hid, bid = _bonista(app)
    payload = {'horario_id': hid, 'fecha': '2026-03-02',
               'registro': [{'alumno_id': aid, 'asistio': True}]}
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    payload['registro'][0]['asistio'] = False
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 0


def test_venta_bono_crea_pago_y_bono(app, auth_client):
    with app.app_context():
        aid = Alumno.query.first().id
    r = auth_client.post(f'/alumnos/{aid}/pago', data={
        'tipo_pago': 'bono', 'monto': '80', 'bono_clases': '10',
        'bono_caducidad': '2026-12-31', 'metodo_pago': 'efectivo'})
    assert r.status_code == 302
    with app.app_context():
        bono = Bono.query.filter_by(alumno_id=aid).order_by(Bono.id.desc()).first()
        assert bono is not None
        assert bono.clases_totales == 10
        assert bono.precio == 80.0
        assert bono.fecha_caducidad == date(2026, 12, 31)
        assert bono.pago_id is not None
