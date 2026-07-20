def test_app_arranca(client):
    r = client.get('/login')
    assert r.status_code == 200


def test_login_admin(auth_client):
    r = auth_client.get('/', follow_redirects=True)
    assert r.status_code == 200
    assert r.request.path == '/'


def test_login_incorrecto(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'mal'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert r.request.path != '/'
