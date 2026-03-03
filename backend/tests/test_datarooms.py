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
