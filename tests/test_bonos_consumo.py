from datetime import date, datetime

from models import db, Alumno, Pago, Bono, Asistencia, HorarioSemanal
from utils.finance_utils import tiene_cuota_mes, sincronizar_consumo_bono


def _prep(app, tipo_cuota='clase_suelta', con_bono=True, caducidad=None,
          totales=10, pagos_meses=()):
    """Alumno nuevo + horario seed + opcional bono y pagos de cuota. → (alumno_id, horario_id, bono_id|None)"""
    with app.app_context():
        a = Alumno(nombre='Bonista', apellido='Test',
                   email=f'b{tipo_cuota}{len(pagos_meses)}{con_bono}@t.local',
                   tipo_cuota=tipo_cuota,
                   fecha_registro=datetime(2026, 1, 1))
        db.session.add(a)
        db.session.flush()
        for mes in pagos_meses:
            db.session.add(Pago(alumno_id=a.id, tipo_pago='cuota', mes=mes, monto=40))
        bid = None
        if con_bono:
            b = Bono(alumno_id=a.id, clases_totales=totales,
                     fecha_compra=date(2026, 1, 5), fecha_caducidad=caducidad, precio=80)
            db.session.add(b)
            db.session.flush()
            bid = b.id
        db.session.commit()
        return a.id, HorarioSemanal.query.first().id, bid


def _asistencia(app, aid, hid, presente=True, fecha=date(2026, 3, 2)):
    with app.app_context():
        asi = Asistencia(alumno_id=aid, horario_id=hid, fecha_clase=fecha, presente=presente)
        db.session.add(asi)
        db.session.flush()
        sincronizar_consumo_bono(asi)
        db.session.commit()
        return asi.id


def test_tiene_cuota_mes(app):
    aid, _, _ = _prep(app, tipo_cuota='1_clase_semanal', con_bono=False,
                      pagos_meses=['2026-03'])
    with app.app_context():
        a = db.session.get(Alumno, aid)
        assert tiene_cuota_mes(a, date(2026, 3, 15)) is True
        assert tiene_cuota_mes(a, date(2026, 4, 15)) is False


def test_consume_bono_sin_cuota(app):
    aid, hid, bid = _prep(app)
    sid = _asistencia(app, aid, hid)
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 1
        assert db.session.get(Asistencia, sid).bono_id == bid


def test_no_consume_con_cuota_del_mes(app):
    aid, hid, bid = _prep(app, tipo_cuota='1_clase_semanal', pagos_meses=['2026-03'])
    _asistencia(app, aid, hid)
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 0


def test_consumo_idempotente(app):
    aid, hid, bid = _prep(app)
    sid = _asistencia(app, aid, hid)
    with app.app_context():
        asi = db.session.get(Asistencia, sid)
        sincronizar_consumo_bono(asi)  # segunda llamada, mismo estado
        db.session.commit()
        assert db.session.get(Bono, bid).clases_consumidas == 1


def test_flip_a_ausente_devuelve_clase(app):
    aid, hid, bid = _prep(app)
    sid = _asistencia(app, aid, hid)
    with app.app_context():
        asi = db.session.get(Asistencia, sid)
        asi.presente = False
        sincronizar_consumo_bono(asi)
        db.session.commit()
        assert db.session.get(Bono, bid).clases_consumidas == 0
        assert db.session.get(Asistencia, sid).bono_id is None


def test_bono_caducado_no_consume(app):
    aid, hid, bid = _prep(app, caducidad=date(2026, 2, 1))
    _asistencia(app, aid, hid, fecha=date(2026, 3, 2))
    with app.app_context():
        assert db.session.get(Bono, bid).clases_consumidas == 0


def test_fifo_bonos(app):
    aid, hid, bid1 = _prep(app, totales=1)
    with app.app_context():
        b2 = Bono(alumno_id=aid, clases_totales=5, fecha_compra=date(2026, 2, 1), precio=50)
        db.session.add(b2)
        db.session.commit()
        bid2 = b2.id
    _asistencia(app, aid, hid, fecha=date(2026, 3, 2))
    _asistencia(app, aid, hid, fecha=date(2026, 3, 9))
    with app.app_context():
        assert db.session.get(Bono, bid1).clases_consumidas == 1  # el viejo primero
        assert db.session.get(Bono, bid2).clases_consumidas == 1  # luego el nuevo
