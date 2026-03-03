import io
import os
import shutil
import uuid

import pytest

from app import create_app
from app.models import db as _db


# Minimal valid PDF content
MINIMAL_PDF = (
    b'%PDF-1.4\n'
    b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
    b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
    b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
    b'xref\n0 4\n'
    b'0000000000 65535 f \n'
    b'0000000009 00000 n \n'
    b'0000000058 00000 n \n'
    b'0000000115 00000 n \n'
    b'trailer\n<< /Size 4 /Root 1 0 R >>\n'
    b'startxref\n190\n%%EOF\n'
)


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    application = create_app('testing')

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()

    # Clean up test storage
    storage_path = application.config.get('STORAGE_PATH', '/tmp/dataroom_test_storage')
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)


@pytest.fixture(scope='function')
def raw_client(app):
    """Create unauthenticated test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def make_authed_client(app):
    """Create an authenticated client for a new user."""
    def _make():
        client = app.test_client()
        email = f"user-{uuid.uuid4().hex[:8]}@example.com"
        password = 'Secret123!'
        resp = client.post(
            '/api/v1/auth/register',
            json={'email': email, 'password': password},
        )
        token = resp.get_json()['token']
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return client

    return _make


@pytest.fixture(scope='function')
def client(make_authed_client):
    """Create authenticated test client."""
    return make_authed_client()


@pytest.fixture(scope='function')
def sample_pdf():
    """Return bytes of a minimal valid PDF."""
    return MINIMAL_PDF
