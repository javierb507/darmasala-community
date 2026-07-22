from datetime import date

from models import db, Alumno, Bono


def _bono(app, totales=10, consumidas=0, caducidad=None):
    with app.app_context():
        a = Alumno.query.first()
        b = Bono(alumno_id=a.id, clases_totales=totales, clases_consumidas=consumidas,
                 fecha_compra=date(2026, 1, 10), fecha_caducidad=caducidad, precio=80.0)
        db.session.add(b)
        db.session.commit()
        return b.id


def test_bono_vigente(app):
    bid = _bono(app)
    with app.app_context():
        b = db.session.get(Bono, bid)
        assert b.clases_restantes == 10
        assert b.esta_vigente(date(2026, 3, 1)) is True


def test_bono_agotado_no_vigente(app):
    bid = _bono(app, totales=5, consumidas=5)
    with app.app_context():
        assert db.session.get(Bono, bid).esta_vigente(date(2026, 3, 1)) is False


def test_bono_caducado_no_vigente(app):
    bid = _bono(app, caducidad=date(2026, 2, 28))
    with app.app_context():
        b = db.session.get(Bono, bid)
        assert b.esta_vigente(date(2026, 2, 28)) is True
        assert b.esta_vigente(date(2026, 3, 1)) is False
