import io
import os
import shutil

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
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def sample_pdf():
    """Return bytes of a minimal valid PDF."""
    return MINIMAL_PDF
