import uuid
from datetime import datetime, timezone

from app.models import db


class Folder(db.Model):
    __tablename__ = 'folders'

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
    parent_id = db.Column(
        db.String(36),
        db.ForeignKey('folders.id'),
        nullable=True,
    )
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.Text, nullable=False, default='')
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

    children = db.relationship(
        'Folder',
        backref=db.backref('parent', remote_side='Folder.id'),
        lazy='dynamic',
    )
    files = db.relationship('File', backref='folder', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'dataroom_id': self.dataroom_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'path': self.path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }
