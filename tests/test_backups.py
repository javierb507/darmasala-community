"""Backups completos en ZIP (BD + adjuntos) — issue #38.

Los tests aíslan los directorios de backups y uploads en tmp_path vía
app.config['BACKUP_DIR'] / app.config['UPLOAD_FOLDER'], así que nunca
tocan backups/ ni uploads/ reales ni la BD de desarrollo.
"""
import io
import json
import zipfile

import pytest

from models import db, Alumno


@pytest.fixture()
def backup_env(app, tmp_path):
    """Redirige backups y uploads a directorios temporales."""
    backups_dir = tmp_path / 'backups'
    uploads_dir = tmp_path / 'uploads'
    (uploads_dir / 'yogaterapia' / '1').mkdir(parents=True)
    (uploads_dir / 'logo.png').write_bytes(b'fake-logo')
    (uploads_dir / 'yogaterapia' / '1' / 'informe.pdf').write_bytes(b'fake-pdf')

    old_upload = app.config.get('UPLOAD_FOLDER')
    app.config['BACKUP_DIR'] = str(backups_dir)
    app.config['UPLOAD_FOLDER'] = str(uploads_dir)
    yield {'backups': backups_dir, 'uploads': uploads_dir}
    app.config['UPLOAD_FOLDER'] = old_upload
    app.config.pop('BACKUP_DIR', None)


def _zips(backups_dir):
    return sorted(backups_dir.glob('backup_darmasala_*.zip'))


def test_crear_backup_zip(backup_env, auth_client):
    r = auth_client.post('/backup/crear')
    assert r.status_code == 302

    zips = _zips(backup_env['backups'])
    assert len(zips) == 1

    with zipfile.ZipFile(zips[0]) as z:
        names = z.namelist()
        assert 'yoga_school.db' in names
        assert 'uploads/logo.png' in names
        assert 'uploads/yogaterapia/1/informe.pdf' in names
        assert z.read('uploads/logo.png') == b'fake-logo'
        meta = json.loads(z.read('meta.json'))
        assert 'fecha' in meta and 'alembic' in meta and 'version' in meta


def test_listado_muestra_zip_y_db(backup_env, auth_client):
    (backup_env['backups']).mkdir(exist_ok=True)
    (backup_env['backups'] / 'backup_legacy.db').write_bytes(b'legacy')
    auth_client.post('/backup/crear')

    r = auth_client.get('/configuracion')
    html = r.data.decode('utf-8')
    assert 'backup_legacy.db' in html
    assert _zips(backup_env['backups'])[0].name in html


def test_descargar_backup_individual(backup_env, auth_client):
    auth_client.post('/backup/crear')
    nombre = _zips(backup_env['backups'])[0].name

    r = auth_client.get(f'/backup/descargar/{nombre}')
    assert r.status_code == 200
    # es un zip válido con la BD dentro
    with zipfile.ZipFile(io.BytesIO(r.data)) as z:
        assert 'yoga_school.db' in z.namelist()


def test_restaurar_backup_zip_roundtrip(backup_env, auth_client, app):
    # 1. alumno marcador y backup
    marcador = Alumno(nombre='Marcador', apellido='Backup',
                      email='marcador@test.local', tipo_cuota='1_clase_semanal')
    db.session.add(marcador)
    db.session.commit()
    auth_client.post('/backup/crear')
    zip_bytes = _zips(backup_env['backups'])[0].read_bytes()
    nombre_zip = _zips(backup_env['backups'])[0].name

    # 2. borrar alumno y un adjunto
    db.session.delete(Alumno.query.filter_by(email='marcador@test.local').one())
    db.session.commit()
    (backup_env['uploads'] / 'logo.png').unlink()
    assert Alumno.query.filter_by(email='marcador@test.local').count() == 0

    # 3. restaurar el zip
    r = auth_client.post('/backup/restaurar', data={
        'backup_file': (io.BytesIO(zip_bytes), nombre_zip),
    }, content_type='multipart/form-data')
    assert r.status_code == 302

    # 4. el alumno y el adjunto vuelven
    db.session.remove()
    assert Alumno.query.filter_by(email='marcador@test.local').count() == 1
    assert (backup_env['uploads'] / 'logo.png').read_bytes() == b'fake-logo'
    # y se creó copia de seguridad automática del estado anterior
    assert list(backup_env['backups'].glob('*before_restore*'))


def test_restaurar_zip_sin_db_no_toca_nada(backup_env, auth_client):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('otra_cosa.txt', 'nada')
    buf.seek(0)

    alumnos_antes = Alumno.query.count()
    r = auth_client.post('/backup/restaurar', data={
        'backup_file': (buf, 'malo.zip'),
    }, content_type='multipart/form-data')
    assert r.status_code == 302

    db.session.remove()
    assert Alumno.query.count() == alumnos_antes
    # sin copia de seguridad automática: no se llegó a tocar la BD
    assert not list(backup_env['backups'].glob('*before_restore*'))


def test_restaurar_db_legacy(backup_env, auth_client, app):
    # copia cruda de la BD actual (comportamiento antiguo con .db)
    db_path = db.engine.url.database
    marcador = Alumno(nombre='Legacy', apellido='Db',
                      email='legacy@test.local', tipo_cuota='1_clase_semanal')
    db.session.add(marcador)
    db.session.commit()
    with open(db_path, 'rb') as f:
        db_bytes = f.read()

    db.session.delete(Alumno.query.filter_by(email='legacy@test.local').one())
    db.session.commit()

    r = auth_client.post('/backup/restaurar', data={
        'backup_file': (io.BytesIO(db_bytes), 'copia.db'),
    }, content_type='multipart/form-data')
    assert r.status_code == 302

    db.session.remove()
    assert Alumno.query.filter_by(email='legacy@test.local').count() == 1


def test_eliminar_backup_zip(backup_env, auth_client):
    auth_client.post('/backup/crear')
    nombre = _zips(backup_env['backups'])[0].name

    r = auth_client.post(f'/backup/eliminar/{nombre}')
    assert r.status_code == 302
    assert not _zips(backup_env['backups'])


def test_descargar_db_actual(backup_env, auth_client):
    r = auth_client.get('/descargar-db')
    assert r.status_code == 200
    assert r.data[:15] == b'SQLite format 3'


def test_restaurar_db_basura_rechazado(app, auth_client):
    """Un .db que no es SQLite no debe tocar la BD."""
    import io as _io
    from models import Alumno
    with app.app_context():
        antes = Alumno.query.count()
    r = auth_client.post('/backup/restaurar', data={
        'backup_file': (_io.BytesIO(b'esto no es una base de datos'), 'malo.db')},
        content_type='multipart/form-data', follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Alumno.query.count() == antes
