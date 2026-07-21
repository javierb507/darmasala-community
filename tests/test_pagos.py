from models import db, Pago, Alumno


def _alumno_id(app):
    with app.app_context():
        return Alumno.query.first().id


def test_pago_cuota_se_crea(app, auth_client):
    aid = _alumno_id(app)
    r = auth_client.post(f'/alumnos/{aid}/pago', data={
        'tipo_pago': 'cuota', 'mes': '2026-07', 'monto': '40', 'metodo_pago': 'efectivo'})
    assert r.status_code == 302
    with app.app_context():
        assert Pago.query.filter_by(alumno_id=aid, tipo_pago='cuota', mes='2026-07').count() == 1


def test_pago_cuota_duplicado_rechazado(app, auth_client):
    aid = _alumno_id(app)
    for _ in range(2):
        auth_client.post(f'/alumnos/{aid}/pago', data={
            'tipo_pago': 'cuota', 'mes': '2026-07', 'monto': '40'})
    with app.app_context():
        assert Pago.query.filter_by(alumno_id=aid, tipo_pago='cuota', mes='2026-07').count() == 1


def test_matricula_marca_alumno(app, auth_client):
    aid = _alumno_id(app)
    auth_client.post(f'/alumnos/{aid}/pago', data={
        'tipo_pago': 'matricula', 'año': '2026', 'monto': '30'})
    with app.app_context():
        alumno = db.session.get(Alumno, aid)
        assert alumno.matricula_pagada is True
        assert Pago.query.filter_by(alumno_id=aid, tipo_pago='matricula', año=2026).count() == 1


def test_matricula_duplicada_rechazada(app, auth_client):
    aid = _alumno_id(app)
    for _ in range(2):
        auth_client.post(f'/alumnos/{aid}/pago', data={
            'tipo_pago': 'matricula', 'año': '2026', 'monto': '30'})
    with app.app_context():
        assert Pago.query.filter_by(alumno_id=aid, tipo_pago='matricula', año=2026).count() == 1


def test_clase_suelta_duplicada_rechazada(app, auth_client):
    aid = _alumno_id(app)
    for _ in range(2):
        auth_client.post(f'/alumnos/{aid}/pago', data={
            'tipo_pago': 'clase_suelta', 'fecha_clase': '2026-07-15', 'monto': '15'})
    with app.app_context():
        assert Pago.query.filter_by(alumno_id=aid, tipo_pago='clase_suelta').count() == 1
