from models import Asistencia, Alumno, HorarioSemanal


def _ids(app):
    with app.app_context():
        return Alumno.query.first().id, HorarioSemanal.query.first().id


def test_lote_crea_asistencia(app, auth_client):
    aid, hid = _ids(app)
    r = auth_client.post('/api/asistencias/registrar-lote', json={
        'horario_id': hid, 'fecha': '2026-07-20',
        'registro': [{'alumno_id': aid, 'asistio': True, 'observaciones': ''}]})
    assert r.get_json()['success'] is True
    with app.app_context():
        a = Asistencia.query.filter_by(alumno_id=aid, horario_id=hid).one()
        assert a.presente is True


def test_lote_actualiza_sin_duplicar(app, auth_client):
    aid, hid = _ids(app)
    payload = {'horario_id': hid, 'fecha': '2026-07-20',
               'registro': [{'alumno_id': aid, 'asistio': True}]}
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    payload['registro'][0]['asistio'] = False
    auth_client.post('/api/asistencias/registrar-lote', json=payload)
    with app.app_context():
        registros = Asistencia.query.filter_by(alumno_id=aid, horario_id=hid).all()
        assert len(registros) == 1
        assert registros[0].presente is False


def test_lote_ignora_sin_marcar(app, auth_client):
    aid, hid = _ids(app)
    auth_client.post('/api/asistencias/registrar-lote', json={
        'horario_id': hid, 'fecha': '2026-07-20',
        'registro': [{'alumno_id': aid, 'asistio': None}]})
    with app.app_context():
        assert Asistencia.query.count() == 0
