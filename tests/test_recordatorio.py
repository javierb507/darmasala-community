from datetime import date, datetime

from models import db, Alumno, Pago
from utils.email_utils import componer_recordatorio


def _moroso(app, nombre='Remiso', email='remiso@t.local'):
    with app.app_context():
        a = Alumno(nombre=nombre, apellido='Prueba', email=email,
                   tipo_cuota='1_clase_semanal', fecha_registro=datetime(2026, 1, 1))
        db.session.add(a)
        db.session.commit()
        return a.id


def test_componer_recordatorio_defaults(app):
    aid = _moroso(app)
    with app.app_context():
        alumno = db.session.get(Alumno, aid)
        asunto, html = componer_recordatorio(alumno, hoy=date(2026, 3, 15))
        assert 'Remiso' in html
        assert 'Ene' in html and 'Mar' in html   # periodos pendientes
        assert '120.00' in html                   # 3 meses x 40 €
        assert asunto  # asunto por defecto no vacío


def test_componer_recordatorio_plantilla_personalizada(app):
    aid = _moroso(app, email='remiso2@t.local')
    with app.app_context():
        from models import Configuracion
        db.session.add(Configuracion(clave='recordatorio_asunto', valor='Aviso {escuela}'))
        db.session.add(Configuracion(
            clave='recordatorio_plantilla',
            valor='Hola {nombre}: debes {deuda} de {periodos}.'))
        db.session.commit()
        alumno = db.session.get(Alumno, aid)
        asunto, html = componer_recordatorio(alumno, hoy=date(2026, 2, 10))
        assert asunto.startswith('Aviso ')
        assert html.startswith('Hola Remiso: debes 80.00')


def test_componer_placeholder_invalido_no_revienta(app):
    aid = _moroso(app, email='remiso3@t.local')
    with app.app_context():
        from models import Configuracion
        db.session.add(Configuracion(clave='recordatorio_plantilla', valor='Rota {noexiste}'))
        db.session.commit()
        alumno = db.session.get(Alumno, aid)
        asunto, html = componer_recordatorio(alumno, hoy=date(2026, 2, 10))
        assert 'Rota' in html   # se envía sin formatear, no lanza excepción


def test_enviar_recordatorio(app, auth_client, monkeypatch):
    aid = _moroso(app, email='remiso4@t.local')
    enviados = []
    monkeypatch.setattr('routes.finance_routes.enviar_email',
                        lambda dest, asunto, html: enviados.append((dest, asunto)) or (True, ''))
    r = auth_client.post(f'/morosidad/{aid}/recordatorio')
    assert r.status_code == 302
    assert enviados and enviados[0][0] == 'remiso4@t.local'


def test_recordatorio_sin_deuda_no_envia(app, auth_client, monkeypatch):
    # Alumno con alta este mes y la cuota del mes pagada → 0 periodos pendientes
    with app.app_context():
        hoy = date.today()
        a = Alumno(nombre='AlDia', apellido='Prueba', email='aldia@t.local',
                   tipo_cuota='1_clase_semanal',
                   fecha_registro=datetime(hoy.year, hoy.month, 1))
        db.session.add(a)
        db.session.flush()
        db.session.add(Pago(alumno_id=a.id, tipo_pago='cuota',
                            mes=hoy.strftime('%Y-%m'), monto=40))
        db.session.commit()
        aid = a.id
    enviados = []
    monkeypatch.setattr('routes.finance_routes.enviar_email',
                        lambda *a, **k: enviados.append(a) or (True, ''))
    auth_client.post(f'/morosidad/{aid}/recordatorio')
    assert enviados == []


def test_guardar_textos_recordatorio(app, auth_client):
    r = auth_client.post('/configuracion/recordatorio/guardar', data={
        'recordatorio_asunto': 'Pago pendiente {escuela}',
        'recordatorio_plantilla': 'Debes {deuda}'})
    assert r.status_code == 302
    aid = _moroso(app, email='remiso5@t.local')
    with app.app_context():
        alumno = db.session.get(Alumno, aid)
        asunto, html = componer_recordatorio(alumno, hoy=date(2026, 2, 10))
        assert html.startswith('Debes ')
