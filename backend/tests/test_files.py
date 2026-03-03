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
