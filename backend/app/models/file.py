import uuid
from datetime import datetime, timezone

from app.models import db


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    dataroom_id = db.Column(
        db.String(36),
        db.ForeignKey('datarooms.id'),
        nullable=False,
    )
    folder_id = db.Column(
        db.String(36),
        db.ForeignKey('folders.id'),
        nullable=True,
    )
    name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(
        db.String(100),
        nullable=False,
        default='application/pdf',
    )
    size_bytes = db.Column(db.BigInteger, nullable=False)
    storage_path = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'dataroom_id': self.dataroom_id,
            'folder_id': self.folder_id,
            'name': self.name,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }
