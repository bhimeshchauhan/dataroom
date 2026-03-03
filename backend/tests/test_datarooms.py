import json


def test_create_dataroom(client):
    """POST /api/v1/datarooms creates a dataroom and returns 201."""
    response = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Project Alpha', 'description': 'First dataroom'}),
        content_type='application/json',
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Project Alpha'
    assert data['description'] == 'First dataroom'
    assert 'id' in data
    assert data['deleted_at'] is None


def test_list_datarooms(client):
    """GET /api/v1/datarooms lists all active datarooms."""
    # Create two datarooms
    client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Dataroom A'}),
        content_type='application/json',
    )
    client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Dataroom B'}),
        content_type='application/json',
    )

    response = client.get('/api/v1/datarooms')
    assert response.status_code == 200
    data = response.get_json()
    assert data['pagination']['total'] == 2
    assert len(data['datarooms']) == 2


def test_duplicate_name_rejected(client):
    """Creating two datarooms with the same name returns 409."""
    client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Unique Room'}),
        content_type='application/json',
    )

    response = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Unique Room'}),
        content_type='application/json',
    )
    assert response.status_code == 409
    data = response.get_json()
    assert 'error' in data


def test_get_dataroom(client):
    """GET /api/v1/datarooms/<id> returns the dataroom."""
    create_resp = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Fetch Me'}),
        content_type='application/json',
    )
    dataroom_id = create_resp.get_json()['id']

    response = client.get(f'/api/v1/datarooms/{dataroom_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Fetch Me'


def test_update_dataroom(client):
    """PATCH /api/v1/datarooms/<id> updates name and description."""
    create_resp = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Old Name'}),
        content_type='application/json',
    )
    dataroom_id = create_resp.get_json()['id']

    response = client.patch(
        f'/api/v1/datarooms/{dataroom_id}',
        data=json.dumps({'name': 'New Name', 'description': 'Updated'}),
        content_type='application/json',
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'New Name'
    assert data['description'] == 'Updated'


def test_delete_dataroom(client):
    """DELETE /api/v1/datarooms/<id> soft-deletes and returns 204."""
    create_resp = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'To Delete'}),
        content_type='application/json',
    )
    dataroom_id = create_resp.get_json()['id']

    response = client.delete(f'/api/v1/datarooms/{dataroom_id}')
    assert response.status_code == 204

    # Should no longer appear in listing
    list_resp = client.get('/api/v1/datarooms')
    assert list_resp.get_json()['pagination']['total'] == 0


def test_datarooms_are_isolated_by_user(make_authed_client):
    """Dataroom listing is scoped by authenticated user."""
    client_one = make_authed_client()
    client_two = make_authed_client()
    client_one.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'IP One Room'}),
        content_type='application/json',
    )
    client_two.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'IP Two Room'}),
        content_type='application/json',
    )

    user1_list = client_one.get('/api/v1/datarooms')
    user2_list = client_two.get('/api/v1/datarooms')

    assert user1_list.status_code == 200
    assert user2_list.status_code == 200
    assert user1_list.get_json()['pagination']['total'] == 1
    assert user2_list.get_json()['pagination']['total'] == 1


def test_same_dataroom_name_allowed_across_different_users(make_authed_client):
    """Two different users can each create a dataroom with the same name."""
    client_one = make_authed_client()
    client_two = make_authed_client()
    first = client_one.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Shared Name'}),
        content_type='application/json',
    )
    second = client_two.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Shared Name'}),
        content_type='application/json',
    )

    assert first.status_code == 201
    assert second.status_code == 201


def test_health_endpoint(client):
    """GET /api/v1/health returns basic service status."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
