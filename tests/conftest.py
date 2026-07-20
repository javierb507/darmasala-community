"""Fixtures compartidas. La BD de tests es un SQLite temporal — se fija
DATABASE_URL ANTES de importar app (app.py lee la URI en import)."""
import os
import tempfile

import pytest

_db_fd, _db_path = tempfile.mkstemp(suffix='_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{_db_path}'

from app import app as flask_app          # noqa: E402  (tras fijar DATABASE_URL)
from models import (db, Usuario, Alumno, Clase, HorarioSemanal,       # noqa: E402
                    ConfiguracionFiscal, Cliente, Configuracion)
from werkzeug.security import generate_password_hash                   # noqa: E402
from datetime import time                                              # noqa: E402


def _seed():
    """Datos mínimos: admin, config fiscal, cliente, alumno inscrito en un horario."""
    admin = Usuario(username='admin', email='admin@test.local',
                    password_hash=generate_password_hash('test123'),
                    nombre='Admin', apellido='Test', rol='admin')
    clase = Clase(nombre='Yoga Test')
    db.session.add_all([admin, clase])
    db.session.flush()
    horario = HorarioSemanal(clase_id=clase.id, dia_semana=0,
                             hora_inicio=time(10, 0), hora_fin=time(11, 0))
    alumno = Alumno(nombre='Ana', apellido='Prueba', email='ana@test.local',
                    tipo_cuota='1_clase_semanal')
    fiscal = ConfiguracionFiscal(nombre_empresa='Test SL', nif='B00000000',
                                 direccion_fiscal='Calle Test 1')
    db.session.add_all([horario, alumno, fiscal])
    db.session.flush()
    alumno.horarios.append(horario)
    cliente = Cliente(nombre='Cliente Test', nif_cif='11111111H',
                      direccion='Calle Cliente 2')
    db.session.add(cliente)
    db.session.commit()


@pytest.fixture()
def app():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        _seed()
        yield flask_app
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    client.post('/login', data={'username': 'admin', 'password': 'test123'})
    return client
