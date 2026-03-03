import io

import pytest

from app.utils.errors import ValidationError
from app.services.storage_service import build_storage_backend


class DummyS3Client:
    def __init__(self):
        self.put_calls = []
        self.get_calls = []

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)

    def get_object(self, **kwargs):
        self.get_calls.append(kwargs)
        return {'Body': io.BytesIO(b'%PDF-1.4\nmock\n%%EOF')}


def test_build_storage_backend_defaults_to_local():
    backend = build_storage_backend({
        'STORAGE_PATH': '/tmp/dataroom_test_storage',
    })
    assert backend.name == 'local'


def test_build_storage_backend_rejects_invalid_backend_name():
    with pytest.raises(ValidationError):
        build_storage_backend({
            'STORAGE_BACKEND': 'invalid',
            'STORAGE_PATH': '/tmp/dataroom_test_storage',
        })


def test_build_storage_backend_requires_s3_settings():
    with pytest.raises(ValidationError):
        build_storage_backend({
            'STORAGE_BACKEND': 's3',
            'S3_BUCKET': '',
            'S3_REGION': 'auto',
        })


def test_s3_backend_uploads_and_downloads(monkeypatch):
    client = DummyS3Client()

    def _fake_client(*args, **kwargs):
        return client

    monkeypatch.setattr('app.services.storage_service.boto3.client', _fake_client)

    backend = build_storage_backend({
        'STORAGE_BACKEND': 's3',
        'S3_BUCKET': 'demo-bucket',
        'S3_REGION': 'auto',
        'S3_ENDPOINT_URL': 'https://example.r2.cloudflarestorage.com',
        'S3_ACCESS_KEY_ID': 'key',
        'S3_SECRET_ACCESS_KEY': 'secret',
        'S3_KEY_PREFIX': 'dataroom',
    })

    backend.write('test-id.pdf', io.BytesIO(b'%PDF-1.4\ncontent\n%%EOF'))
    data = backend.read('test-id.pdf')

    assert data.startswith(b'%PDF')
    assert client.put_calls
    assert client.get_calls
