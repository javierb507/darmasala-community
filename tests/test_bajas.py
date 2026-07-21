from datetime import date

from models import db, Alumno


def test_desactivar_registra_fecha_baja(app, auth_client):
    with app.app_context():
        aid = Alumno.query.first().id
    auth_client.post(f'/alumnos/{aid}/eliminar')
    with app.app_context():
        alumno = db.session.get(Alumno, aid)
        assert alumno.activo is False
        assert alumno.fecha_baja == date.today()


def test_reactivar_limpia_fecha_baja(app, auth_client):
    with app.app_context():
        aid = Alumno.query.first().id
    auth_client.post(f'/alumnos/{aid}/eliminar')
    auth_client.post(f'/alumnos/{aid}/reactivar')
    with app.app_context():
        alumno = db.session.get(Alumno, aid)
        assert alumno.activo is True
        assert alumno.fecha_baja is None
