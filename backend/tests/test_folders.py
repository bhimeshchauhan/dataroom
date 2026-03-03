import json


def _create_dataroom(client, name='Test Dataroom'):
    resp = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': name}),
        content_type='application/json',
    )
    return resp.get_json()['id']


def test_create_folder_in_dataroom(client):
    """POST creates a root-level folder in a dataroom."""
    dataroom_id = _create_dataroom(client)

    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Documents'}),
        content_type='application/json',
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Documents'
    assert data['dataroom_id'] == dataroom_id
    assert data['parent_id'] is None
    assert data['path'].startswith('/')


def test_nested_folders(client):
    """Creating a child folder builds the correct materialized path."""
    dataroom_id = _create_dataroom(client)

    # Create parent
    parent_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Parent'}),
        content_type='application/json',
    )
    parent = parent_resp.get_json()

    # Create child
    child_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Child', 'parent_id': parent['id']}),
        content_type='application/json',
    )
    child = child_resp.get_json()

    assert child_resp.status_code == 201
    assert child['parent_id'] == parent['id']
    # Path should contain both parent ID and child ID
    assert parent['id'] in child['path']
    assert child['id'] in child['path']
    # Path should start with parent's path
    assert child['path'].startswith(parent['path'])


def test_duplicate_folder_rejected(client):
    """Same folder name in same parent returns 409."""
    dataroom_id = _create_dataroom(client)

    client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Financials'}),
        content_type='application/json',
    )

    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Financials'}),
        content_type='application/json',
    )
    assert response.status_code == 409


def test_delete_cascades(client):
    """Deleting a parent folder also soft-deletes its children."""
    dataroom_id = _create_dataroom(client)

    # Create parent
    parent_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Parent'}),
        content_type='application/json',
    )
    parent_id = parent_resp.get_json()['id']

    # Create child
    child_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Child', 'parent_id': parent_id}),
        content_type='application/json',
    )
    child_id = child_resp.get_json()['id']

    # Delete parent
    delete_resp = client.delete(f'/api/v1/folders/{parent_id}')
    assert delete_resp.status_code == 204

    # Child should not be accessible
    child_get_resp = client.get(f'/api/v1/folders/{child_id}/contents')
    assert child_get_resp.status_code == 404


def test_rename_folder(client):
    """PATCH renames a folder."""
    dataroom_id = _create_dataroom(client)

    create_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Old Folder'}),
        content_type='application/json',
    )
    folder_id = create_resp.get_json()['id']

    rename_resp = client.patch(
        f'/api/v1/folders/{folder_id}',
        data=json.dumps({'name': 'New Folder'}),
        content_type='application/json',
    )
    assert rename_resp.status_code == 200
    assert rename_resp.get_json()['name'] == 'New Folder'


def test_folder_contents(client):
    """GET /folders/<id>/contents lists child folders and files."""
    dataroom_id = _create_dataroom(client)

    # Create parent
    parent_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Parent'}),
        content_type='application/json',
    )
    parent_id = parent_resp.get_json()['id']

    # Create two children
    client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Child A', 'parent_id': parent_id}),
        content_type='application/json',
    )
    client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Child B', 'parent_id': parent_id}),
        content_type='application/json',
    )

    response = client.get(f'/api/v1/folders/{parent_id}/contents')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['folders']) == 2
    assert data['folder']['id'] == parent_id


def test_contents_pagination(client):
    """Pagination params limit returned folders/files and include totals."""
    dataroom_id = _create_dataroom(client)

    # Create parent
    parent_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Parent'}),
        content_type='application/json',
    )
    parent_id = parent_resp.get_json()['id']

    # Create 3 child folders
    for i in range(3):
        client.post(
            f'/api/v1/datarooms/{dataroom_id}/folders',
            data=json.dumps({'name': f'Child {i}', 'parent_id': parent_id}),
            content_type='application/json',
        )

    # Request page 1 with per_page=2
    resp = client.get(f'/api/v1/folders/{parent_id}/contents?per_page=2&page=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['folders']) == 2
    assert data['pagination']['total_folders'] == 3
    assert data['pagination']['total_files'] == 0
    assert data['pagination']['page'] == 1
    assert data['pagination']['per_page'] == 2

    # Request page 2 — should have 1 remaining folder
    resp2 = client.get(f'/api/v1/folders/{parent_id}/contents?per_page=2&page=2')
    data2 = resp2.get_json()
    assert len(data2['folders']) == 1
    assert data2['pagination']['total_folders'] == 3

    # Request page 3 — should be empty
    resp3 = client.get(f'/api/v1/folders/{parent_id}/contents?per_page=2&page=3')
    data3 = resp3.get_json()
    assert len(data3['folders']) == 0


def test_dataroom_tree(client):
    """GET /datarooms/<id>/tree returns nested folder structure."""
    dataroom_id = _create_dataroom(client)

    parent_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Root Folder'}),
        content_type='application/json',
    )
    parent_id = parent_resp.get_json()['id']

    client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps({'name': 'Sub Folder', 'parent_id': parent_id}),
        content_type='application/json',
    )

    response = client.get(f'/api/v1/datarooms/{dataroom_id}/tree')
    assert response.status_code == 200
    data = response.get_json()
    tree = data['tree']
    assert len(tree) == 1
    assert tree[0]['name'] == 'Root Folder'
    assert len(tree[0]['children']) == 1
    assert tree[0]['children'][0]['name'] == 'Sub Folder'
