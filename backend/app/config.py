import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://dataroom:dataroom@localhost:5432/dataroom',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 25 * 1024 * 1024))
    FREE_STORAGE_QUOTA_BYTES = int(
        os.environ.get('FREE_STORAGE_QUOTA_BYTES', 800 * 1024 * 1024)
    )
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
    STORAGE_PATH = os.environ.get('STORAGE_PATH', './storage')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_REGION = os.environ.get('S3_REGION', 'auto')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_KEY_PREFIX = os.environ.get('S3_KEY_PREFIX', '')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    TRUST_PROXY_HEADERS = _as_bool(os.environ.get('TRUST_PROXY_HEADERS'), False)
    RATELIMIT_ENABLED = _as_bool(os.environ.get('RATELIMIT_ENABLED'), True)
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    STORAGE_PATH = '/tmp/dataroom_test_storage'
    RATELIMIT_ENABLED = False
