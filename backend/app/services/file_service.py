import os
import uuid
from datetime import datetime, timezone

from flask import current_app
from werkzeug.utils import secure_filename

from app.models import db
from app.models.dataroom import Dataroom
from app.models.folder import Folder
from app.models.file import File
from app.services.storage_service import build_storage_backend
from app.utils.errors import NotFoundError, ConflictError, ValidationError


class FileService:

    @staticmethod
    def validate_upload(file):
        """Validate an uploaded file. Returns file size on success."""
        # 1. File present with filename
        if not file or not file.filename:
            raise ValidationError('No file provided')

        # 2. Extension is .pdf
        if not file.filename.lower().endswith('.pdf'):
            raise ValidationError('Only PDF files are allowed')

        # 3. Content-Type is application/pdf
        if file.content_type != 'application/pdf':
            raise ValidationError('File must have application/pdf content type')

        # 4. File size check
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size <= 0:
            raise ValidationError('File is empty')

        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        if size > max_size:
            raise ValidationError(f'File size exceeds maximum of {max_size} bytes')

        # 5. Magic bytes check
        header = file.read(4)
        file.seek(0)

        if header != b'%PDF':
            raise ValidationError('File does not appear to be a valid PDF')

        return size

    @staticmethod
    def upload(dataroom_id, file, folder_id=None):
        # Verify dataroom exists
        dataroom = Dataroom.query.filter(
            Dataroom.id == str(dataroom_id),
            Dataroom.deleted_at.is_(None),
        ).first()
        if not dataroom:
            raise NotFoundError(f'Dataroom {dataroom_id} not found')

        # Verify folder if given
        if folder_id:
            folder = Folder.query.filter(
                Folder.id == str(folder_id),
                Folder.dataroom_id == str(dataroom_id),
                Folder.deleted_at.is_(None),
            ).first()
            if not folder:
                raise NotFoundError(f'Folder {folder_id} not found')

        # Validate file
        size = FileService.validate_upload(file)

        # Sanitize filename
        original_name = secure_filename(file.filename)
        if not original_name:
            original_name = 'document.pdf'
        if not original_name.lower().endswith('.pdf'):
            original_name += '.pdf'

        # Check uniqueness
        uniqueness_query = File.query.filter(
            File.dataroom_id == str(dataroom_id),
            File.name == original_name,
            File.deleted_at.is_(None),
        )
        if folder_id:
            uniqueness_query = uniqueness_query.filter(
                File.folder_id == str(folder_id),
            )
        else:
            uniqueness_query = uniqueness_query.filter(File.folder_id.is_(None))

        if uniqueness_query.first():
            raise ConflictError(
                f'A file named "{original_name}" already exists in this location',
            )

        # Save to disk, then commit to DB atomically.
        # If DB commit fails, clean up the orphaned file on disk.
        file_uuid = str(uuid.uuid4())
        storage_filename = f'{file_uuid}.pdf'
        storage = build_storage_backend(current_app.config)
        file.stream.seek(0)
        storage.write(storage_filename, file.stream)

        try:
            file_record = File(
                id=file_uuid,
                dataroom_id=str(dataroom_id),
                folder_id=str(folder_id) if folder_id else None,
                name=original_name,
                mime_type='application/pdf',
                size_bytes=size,
                storage_path=storage_filename,
            )
            db.session.add(file_record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            try:
                storage.delete(storage_filename)
            except Exception:
                pass
            raise
        return file_record

    @staticmethod
    def get(file_id):
        file_record = File.query.filter(
            File.id == str(file_id),
            File.deleted_at.is_(None),
        ).first()
        if not file_record:
            raise NotFoundError(f'File {file_id} not found')
        return file_record

    @staticmethod
    def get_storage_path(file_id):
        file_record = FileService.get(file_id)
        storage = build_storage_backend(current_app.config)
        if storage.name != 'local':
            raise ValidationError('get_storage_path is only available for local storage backend')
        storage_dir = current_app.config['STORAGE_PATH']
        abs_path = os.path.join(os.path.abspath(storage_dir), file_record.storage_path)
        if not os.path.isfile(abs_path):
            raise NotFoundError('File content not found on disk')
        return abs_path

    @staticmethod
    def get_content(file_id):
        file_record = FileService.get(file_id)
        storage = build_storage_backend(current_app.config)
        return storage.read(file_record.storage_path)

    @staticmethod
    def rename(file_id, name):
        if not name or not isinstance(name, str):
            raise ValidationError('Name is required')

        name = name.strip()
        if not name:
            raise ValidationError('Name cannot be empty')

        if len(name) > 255:
            raise ValidationError('Name must be 255 characters or fewer')

        if not name.lower().endswith('.pdf'):
            raise ValidationError('File name must end with .pdf')

        file_record = FileService.get(file_id)

        # Check uniqueness in same location
        uniqueness_query = File.query.filter(
            File.dataroom_id == file_record.dataroom_id,
            File.name == name,
            File.deleted_at.is_(None),
            File.id != str(file_id),
        )
        if file_record.folder_id:
            uniqueness_query = uniqueness_query.filter(
                File.folder_id == file_record.folder_id,
            )
        else:
            uniqueness_query = uniqueness_query.filter(File.folder_id.is_(None))

        if uniqueness_query.first():
            raise ConflictError(f'A file named "{name}" already exists in this location')

        file_record.name = name
        file_record.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return file_record

    @staticmethod
    def delete(file_id):
        file_record = FileService.get(file_id)
        file_record.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
