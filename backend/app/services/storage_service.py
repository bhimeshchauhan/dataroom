import os
from io import BytesIO
from typing import Mapping

import boto3
from botocore.config import Config as BotoConfig

from app.utils.errors import NotFoundError, ValidationError


class BaseStorageBackend:
    name = 'base'

    def write(self, key, stream):
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError


class LocalStorageBackend(BaseStorageBackend):
    name = 'local'

    def __init__(self, storage_path):
        self.storage_path = os.path.abspath(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)

    def write(self, key, stream):
        abs_path = os.path.join(self.storage_path, key)
        stream.seek(0)
        with open(abs_path, 'wb') as fh:
            fh.write(stream.read())

    def read(self, key):
        abs_path = os.path.join(self.storage_path, key)
        if not os.path.isfile(abs_path):
            raise NotFoundError('File content not found on disk')
        with open(abs_path, 'rb') as fh:
            return fh.read()

    def delete(self, key):
        abs_path = os.path.join(self.storage_path, key)
        try:
            os.remove(abs_path)
        except FileNotFoundError:
            pass


class S3StorageBackend(BaseStorageBackend):
    name = 's3'

    def __init__(
        self,
        *,
        bucket,
        region,
        endpoint_url,
        access_key_id,
        secret_access_key,
        key_prefix='',
    ):
        self.bucket = bucket
        self.key_prefix = key_prefix.strip('/')
        self.client = boto3.client(
            's3',
            region_name=region,
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=BotoConfig(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
            ),
        )

    def _key(self, key):
        if not self.key_prefix:
            return key
        return f'{self.key_prefix}/{key}'

    def write(self, key, stream):
        stream.seek(0)
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._key(key),
            Body=BytesIO(stream.read()),
            ContentType='application/pdf',
        )

    def read(self, key):
        obj = self.client.get_object(
            Bucket=self.bucket,
            Key=self._key(key),
        )
        return obj['Body'].read()

    def delete(self, key):
        self.client.delete_object(
            Bucket=self.bucket,
            Key=self._key(key),
        )


def build_storage_backend(config: Mapping[str, object]):
    backend = (config.get('STORAGE_BACKEND') or 'local').lower()

    if backend == 'local':
        storage_path = config.get('STORAGE_PATH')
        if not storage_path:
            raise ValidationError('STORAGE_PATH is required for local storage backend')
        return LocalStorageBackend(storage_path=str(storage_path))

    if backend == 's3':
        required = {
            'S3_BUCKET': config.get('S3_BUCKET'),
            'S3_ACCESS_KEY_ID': config.get('S3_ACCESS_KEY_ID'),
            'S3_SECRET_ACCESS_KEY': config.get('S3_SECRET_ACCESS_KEY'),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValidationError(f'Missing required s3 settings: {", ".join(missing)}')

        return S3StorageBackend(
            bucket=str(config.get('S3_BUCKET')),
            region=str(config.get('S3_REGION') or 'auto'),
            endpoint_url=str(config.get('S3_ENDPOINT_URL') or ''),
            access_key_id=str(config.get('S3_ACCESS_KEY_ID')),
            secret_access_key=str(config.get('S3_SECRET_ACCESS_KEY')),
            key_prefix=str(config.get('S3_KEY_PREFIX') or ''),
        )

    raise ValidationError(f'Unsupported STORAGE_BACKEND: {backend}')
