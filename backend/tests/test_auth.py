import json


def test_register_login_me_flow(raw_client):
    register = raw_client.post(
        '/api/v1/auth/register',
        data=json.dumps({'email': 'test@example.com', 'password': 'Secret123!'}),
        content_type='application/json',
    )
    assert register.status_code == 201
    reg_data = register.get_json()
    assert 'token' in reg_data
    assert reg_data['user']['email'] == 'test@example.com'

    login = raw_client.post(
        '/api/v1/auth/login',
        data=json.dumps({'email': 'test@example.com', 'password': 'Secret123!'}),
        content_type='application/json',
    )
    assert login.status_code == 200
    token = login.get_json()['token']

    me = raw_client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    assert me.get_json()['email'] == 'test@example.com'


def test_duplicate_registration_rejected(raw_client):
    payload = {'email': 'dupe@example.com', 'password': 'Secret123!'}
    first = raw_client.post('/api/v1/auth/register', data=json.dumps(payload), content_type='application/json')
    second = raw_client.post('/api/v1/auth/register', data=json.dumps(payload), content_type='application/json')
    assert first.status_code == 201
    assert second.status_code == 409


def test_protected_endpoint_requires_auth(raw_client):
    resp = raw_client.get('/api/v1/datarooms')
    assert resp.status_code == 401
