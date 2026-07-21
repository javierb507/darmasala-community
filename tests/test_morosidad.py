"""Tests de morosidad: periodos de cuota pendientes acotados por fecha de alta."""
from datetime import date, datetime

import pytest

from models import db, Alumno, Pago
from utils.finance_utils import periodos_pendientes, calcular_morosidad


def _alta(app, tipo_cuota, fecha_registro, pagos_meses=()):
    """Crea alumno con alta y pagos de cuota dados. Devuelve id."""
    with app.app_context():
        a = Alumno(nombre='Moroso', apellido='Test',
                   email=f'{tipo_cuota}{fecha_registro}@t.local',
                   tipo_cuota=tipo_cuota,
                   fecha_registro=datetime.combine(fecha_registro, datetime.min.time()))
        db.session.add(a)
        db.session.flush()
        for mes in pagos_meses:
            db.session.add(Pago(alumno_id=a.id, tipo_pago='cuota', mes=mes, monto=40))
        db.session.commit()
        return a.id


def test_mensual_debe_meses_desde_alta(app):
    aid = _alta(app, '1_clase_semanal', date(2026, 1, 10), pagos_meses=['2026-01', '2026-02'])
    with app.app_context():
        pendientes = periodos_pendientes(db.session.get(Alumno, aid), hoy=date(2026, 4, 15))
        assert [p.mes_inicio for p in pendientes] == [3, 4]


def test_alta_reciente_no_debe_meses_anteriores(app):
    aid = _alta(app, '1_clase_semanal', date(2026, 9, 1))
    with app.app_context():
        pendientes = periodos_pendientes(db.session.get(Alumno, aid), hoy=date(2026, 10, 20))
        assert [p.mes_inicio for p in pendientes] == [9, 10]


def test_bimensual_por_bimestres(app):
    aid = _alta(app, '1_clase_bimensual', date(2026, 1, 10), pagos_meses=['2026-01'])
    with app.app_context():
        pendientes = periodos_pendientes(db.session.get(Alumno, aid), hoy=date(2026, 4, 15))
        # Ene/Feb pagado; pendiente solo Mar/Abr
        assert len(pendientes) == 1
        assert (pendientes[0].mes_inicio, pendientes[0].mes_fin) == (3, 4)


def test_clase_suelta_sin_morosidad(app):
    aid = _alta(app, 'clase_suelta', date(2026, 1, 10))
    with app.app_context():
        assert periodos_pendientes(db.session.get(Alumno, aid), hoy=date(2026, 6, 1)) == []


def test_calcular_morosidad_agrega_deuda(app):
    _alta(app, '1_clase_semanal', date(2026, 1, 10))  # debe ene-abr = 4 periodos
    with app.app_context():
        morosos = calcular_morosidad(hoy=date(2026, 4, 15))
        moroso = next(m for m in morosos if m['alumno'].nombre == 'Moroso')
        assert len(moroso['periodos']) == 4
        assert moroso['deuda'] == pytest.approx(4 * moroso['alumno'].get_precio_cuota())

def test_pagina_morosidad(app, auth_client):
    _alta(app, '1_clase_semanal', date(2026, 1, 10))
    r = auth_client.get('/morosidad')
    assert r.status_code == 200
    assert 'Moroso'.encode() in r.data
