from datetime import date, datetime

from models import db, Alumno, Pago, Asistencia, HorarioSemanal


def test_pagina_informes_carga(auth_client):
    r = auth_client.get('/informes')
    assert r.status_code == 200


def test_informes_refleja_ingresos_y_bajas(app, auth_client):
    with app.app_context():
        alumno = Alumno.query.first()
        db.session.add(Pago(alumno_id=alumno.id, tipo_pago='yogaterapia', monto=53.17,
                            fecha_creacion=datetime.now()))
        alumno2 = Alumno(nombre='Baja', apellido='Mes', email='baja@t.local',
                         tipo_cuota='1_clase_semanal', activo=False,
                         fecha_baja=date.today())
        db.session.add(alumno2)
        db.session.commit()
    r = auth_client.get('/informes')
    assert r.status_code == 200
    assert b'53.17' in r.data  # el pago de yogaterapia aparece en los datos del chart


def test_informes_ocupacion(app, auth_client):
    with app.app_context():
        alumno = Alumno.query.first()
        horario = HorarioSemanal.query.first()
        db.session.add(Asistencia(alumno_id=alumno.id, horario_id=horario.id,
                                  fecha_clase=date.today(), presente=True))
        db.session.commit()
    r = auth_client.get('/informes')
    assert r.status_code == 200
    assert b'Yoga Test' in r.data  # el horario seed aparece en ocupación


def test_economia_historico_incluye_yogaterapia_y_bonos(app, auth_client):
    from datetime import datetime as _dt
    with app.app_context():
        alumno = Alumno.query.first()
        db.session.add(Pago(alumno_id=alumno.id, tipo_pago='yogaterapia', monto=61.07,
                            fecha_creacion=_dt.now()))
        db.session.add(Pago(alumno_id=alumno.id, tipo_pago='bono', monto=87.03,
                            fecha_creacion=_dt.now()))
        db.session.commit()
    r = auth_client.get('/economia/historico')
    assert r.status_code == 200
    assert b'61.07' in r.data
    assert b'87.03' in r.data
