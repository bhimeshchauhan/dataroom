from datetime import datetime, timezone

from app.models import db
from app.models.dataroom import Dataroom
from app.models.folder import Folder
from app.models.file import File
from app.utils.errors import NotFoundError, ConflictError
from app.utils.validation import validate_name


class DataroomService:

    @staticmethod
    def create(name, description=None, user_id=None):
        name = validate_name(name)

        existing = Dataroom.query.filter(
            Dataroom.name == name,
            Dataroom.user_id == str(user_id),
            Dataroom.deleted_at.is_(None),
        ).first()
        if existing:
            raise ConflictError(f'A dataroom named "{name}" already exists')

        dataroom = Dataroom(name=name, description=description, user_id=str(user_id))
        db.session.add(dataroom)
        db.session.commit()
        return dataroom

    @staticmethod
    def list_all(page=1, per_page=20, user_id=None):
        query = Dataroom.query.filter(
            Dataroom.user_id == str(user_id),
            Dataroom.deleted_at.is_(None),
        ).order_by(Dataroom.updated_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'datarooms': [d.to_dict() for d in pagination.items],
            'pagination': {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
            },
        }

    @staticmethod
    def get(dataroom_id, user_id=None):
        dataroom = Dataroom.query.filter(
            Dataroom.id == str(dataroom_id),
            Dataroom.user_id == str(user_id),
            Dataroom.deleted_at.is_(None),
        ).first()
        if not dataroom:
            raise NotFoundError(f'Dataroom {dataroom_id} not found')
        return dataroom

    @staticmethod
    def update(dataroom_id, name=None, description=None, user_id=None):
        dataroom = DataroomService.get(dataroom_id, user_id=user_id)

        if name is not None:
            name = validate_name(name)
            existing = Dataroom.query.filter(
                Dataroom.name == name,
                Dataroom.user_id == str(user_id),
                Dataroom.deleted_at.is_(None),
                Dataroom.id != str(dataroom_id),
            ).first()
            if existing:
                raise ConflictError(f'A dataroom named "{name}" already exists')
            dataroom.name = name

        if description is not None:
            dataroom.description = description

        dataroom.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return dataroom

    @staticmethod
    def delete(dataroom_id, user_id=None):
        dataroom = DataroomService.get(dataroom_id, user_id=user_id)
        now = datetime.now(timezone.utc)

        dataroom.deleted_at = now

        Folder.query.filter(
            Folder.dataroom_id == str(dataroom_id),
            Folder.deleted_at.is_(None),
        ).update({'deleted_at': now}, synchronize_session='fetch')

        File.query.filter(
            File.dataroom_id == str(dataroom_id),
            File.deleted_at.is_(None),
        ).update({'deleted_at': now}, synchronize_session='fetch')

        db.session.commit()
