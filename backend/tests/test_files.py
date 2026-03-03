import io
import json


def _create_dataroom(client, name='Test Dataroom'):
    resp = client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': name}),
        content_type='application/json',
    )
    return resp.get_json()['id']


def _create_folder(client, dataroom_id, name='Test Folder', parent_id=None):
    payload = {'name': name}
    if parent_id:
        payload['parent_id'] = parent_id
    resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/folders',
        data=json.dumps(payload),
        content_type='application/json',
    )
    return resp.get_json()['id']


def test_upload_file(client, sample_pdf):
    """POST uploads a valid PDF and returns 201."""
    dataroom_id = _create_dataroom(client)

    data = {
        'file': (io.BytesIO(sample_pdf), 'document.pdf', 'application/pdf'),
    }
    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    assert response.status_code == 201
    result = response.get_json()
    assert result['name'] == 'document.pdf'
    assert result['mime_type'] == 'application/pdf'
    assert result['size_bytes'] > 0
    assert result['dataroom_id'] == dataroom_id
    assert result['folder_id'] is None


def test_upload_to_folder(client, sample_pdf):
    """Uploading a file to a specific folder stores the folder_id."""
    dataroom_id = _create_dataroom(client)
    folder_id = _create_folder(client, dataroom_id, 'Reports')

    data = {
        'file': (io.BytesIO(sample_pdf), 'report.pdf', 'application/pdf'),
        'folder_id': folder_id,
    }
    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    assert response.status_code == 201
    result = response.get_json()
    assert result['folder_id'] == folder_id


def test_reject_non_pdf(client):
    """Uploading a non-PDF file returns 400."""
    dataroom_id = _create_dataroom(client)

    data = {
        'file': (io.BytesIO(b'not a pdf'), 'document.pdf', 'application/pdf'),
    }
    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result
    assert 'PDF' in result['error'] or 'pdf' in result['error']


def test_rename_file(client, sample_pdf):
    """PATCH renames a file and the new name is reflected."""
    dataroom_id = _create_dataroom(client)

    # Upload
    data = {
        'file': (io.BytesIO(sample_pdf), 'original.pdf', 'application/pdf'),
    }
    upload_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    file_id = upload_resp.get_json()['id']

    # Rename
    rename_resp = client.patch(
        f'/api/v1/files/{file_id}',
        data=json.dumps({'name': 'renamed.pdf'}),
        content_type='application/json',
    )
    assert rename_resp.status_code == 200
    assert rename_resp.get_json()['name'] == 'renamed.pdf'


def test_delete_file(client, sample_pdf):
    """DELETE soft-deletes a file and it becomes inaccessible."""
    dataroom_id = _create_dataroom(client)

    data = {
        'file': (io.BytesIO(sample_pdf), 'to_delete.pdf', 'application/pdf'),
    }
    upload_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    file_id = upload_resp.get_json()['id']

    # Delete
    delete_resp = client.delete(f'/api/v1/files/{file_id}')
    assert delete_resp.status_code == 204

    # Should not be found
    get_resp = client.get(f'/api/v1/files/{file_id}')
    assert get_resp.status_code == 404


def test_get_file_metadata(client, sample_pdf):
    """GET /files/<id> returns file metadata."""
    dataroom_id = _create_dataroom(client)

    data = {
        'file': (io.BytesIO(sample_pdf), 'info.pdf', 'application/pdf'),
    }
    upload_resp = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    file_id = upload_resp.get_json()['id']

    response = client.get(f'/api/v1/files/{file_id}')
    assert response.status_code == 200
    result = response.get_json()
    assert result['id'] == file_id
    assert result['name'] == 'info.pdf'


def test_reject_non_pdf_extension(client):
    """Uploading a file without .pdf extension returns 400."""
    dataroom_id = _create_dataroom(client)

    data = {
        'file': (io.BytesIO(b'%PDF-1.4 fake'), 'document.txt', 'application/pdf'),
    }
    response = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data=data,
        content_type='multipart/form-data',
    )
    assert response.status_code == 400


def test_file_access_isolated_by_user(make_authed_client, sample_pdf):
    """File metadata/content are not accessible from a different user."""
    owner_client = make_authed_client()
    other_client = make_authed_client()
    create_resp = owner_client.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Private Room'}),
        content_type='application/json',
    )
    dataroom_id = create_resp.get_json()['id']

    upload_resp = owner_client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data={'file': (io.BytesIO(sample_pdf), 'private.pdf', 'application/pdf')},
        content_type='multipart/form-data',
    )
    file_id = upload_resp.get_json()['id']

    forbidden_meta = other_client.get(
        f'/api/v1/files/{file_id}',
    )
    forbidden_content = other_client.get(
        f'/api/v1/files/{file_id}/content',
    )

    assert forbidden_meta.status_code == 404
    assert forbidden_content.status_code == 404


def test_reject_upload_when_user_storage_quota_reached(client, sample_pdf):
    """Uploads are rejected when per-user free quota would be exceeded."""
    dataroom_id = _create_dataroom(client)
    client.application.config['FREE_STORAGE_QUOTA_BYTES'] = len(sample_pdf) + 10

    first_upload = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data={'file': (io.BytesIO(sample_pdf), 'first.pdf', 'application/pdf')},
        content_type='multipart/form-data',
    )
    assert first_upload.status_code == 201

    second_upload = client.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data={'file': (io.BytesIO(sample_pdf), 'second.pdf', 'application/pdf')},
        content_type='multipart/form-data',
    )
    assert second_upload.status_code == 400
    assert 'Storage limit reached' in second_upload.get_json()['error']


def test_storage_usage_endpoint_scoped_by_user(make_authed_client, sample_pdf):
    """Storage usage endpoint returns usage for current authenticated user."""
    client_one = make_authed_client()
    client_two = make_authed_client()
    create_resp = client_one.post(
        '/api/v1/datarooms',
        data=json.dumps({'name': 'Usage Room'}),
        content_type='application/json',
    )
    dataroom_id = create_resp.get_json()['id']

    upload_resp = client_one.post(
        f'/api/v1/datarooms/{dataroom_id}/files',
        data={'file': (io.BytesIO(sample_pdf), 'usage.pdf', 'application/pdf')},
        content_type='multipart/form-data',
    )
    assert upload_resp.status_code == 201

    usage_ip1 = client_one.get('/api/v1/storage/usage')
    usage_ip2 = client_two.get('/api/v1/storage/usage')

    assert usage_ip1.status_code == 200
    assert usage_ip2.status_code == 200

    ip1_data = usage_ip1.get_json()
    ip2_data = usage_ip2.get_json()
    assert ip1_data['used_bytes'] > 0
    assert ip2_data['used_bytes'] == 0
    assert ip1_data['quota_bytes'] == client_one.application.config['FREE_STORAGE_QUOTA_BYTES']
