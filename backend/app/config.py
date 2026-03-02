import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://dataroom:dataroom@localhost:5432/dataroom',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 50 * 1024 * 1024))
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
    STORAGE_PATH = os.environ.get('STORAGE_PATH', './storage')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_REGION = os.environ.get('S3_REGION', 'auto')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_KEY_PREFIX = os.environ.get('S3_KEY_PREFIX', '')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    STORAGE_PATH = '/tmp/dataroom_test_storage'
