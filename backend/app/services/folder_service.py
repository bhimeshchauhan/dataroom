from datetime import datetime, timezone

from app.models import db
from app.models.dataroom import Dataroom
from app.models.folder import Folder
from app.models.file import File
from app.utils.errors import NotFoundError, ConflictError
from app.utils.validation import validate_folder_name


class FolderService:

    @staticmethod
    def _get_active_dataroom(dataroom_id):
        dataroom = Dataroom.query.filter(
            Dataroom.id == str(dataroom_id),
            Dataroom.deleted_at.is_(None),
        ).first()
        if not dataroom:
            raise NotFoundError(f'Dataroom {dataroom_id} not found')
        return dataroom

    @staticmethod
    def create(dataroom_id, name, parent_id=None):
        name = validate_folder_name(name)
        FolderService._get_active_dataroom(dataroom_id)

        parent = None
        if parent_id:
            parent = Folder.query.filter(
                Folder.id == str(parent_id),
                Folder.dataroom_id == str(dataroom_id),
                Folder.deleted_at.is_(None),
            ).first()
            if not parent:
                raise NotFoundError(f'Parent folder {parent_id} not found')

        # Check uniqueness: same name in same parent within same dataroom
        uniqueness_query = Folder.query.filter(
            Folder.dataroom_id == str(dataroom_id),
            Folder.name == name,
            Folder.deleted_at.is_(None),
        )
        if parent_id:
            uniqueness_query = uniqueness_query.filter(Folder.parent_id == str(parent_id))
        else:
            uniqueness_query = uniqueness_query.filter(Folder.parent_id.is_(None))

        if uniqueness_query.first():
            raise ConflictError(f'A folder named "{name}" already exists in this location')

        folder = Folder(
            dataroom_id=str(dataroom_id),
            parent_id=str(parent_id) if parent_id else None,
            name=name,
        )
        db.session.add(folder)
        db.session.flush()  # Get the ID

        # Build materialized path
        if parent:
            folder.path = f'{parent.path}/{folder.id}'
        else:
            folder.path = f'/{folder.id}'

        db.session.commit()
        return folder

    @staticmethod
    def get(folder_id):
        folder = Folder.query.filter(
            Folder.id == str(folder_id),
            Folder.deleted_at.is_(None),
        ).first()
        if not folder:
            raise NotFoundError(f'Folder {folder_id} not found')
        return folder

    @staticmethod
    def get_contents(folder_id=None, dataroom_id=None, page=1, per_page=20,
                     sort_by='name', sort_order='asc'):
        current_folder = None
        breadcrumbs = []

        if folder_id:
            current_folder = FolderService.get(folder_id)
            dataroom_id = current_folder.dataroom_id
            breadcrumbs = FolderService._build_breadcrumbs(current_folder)
            folder_query = Folder.query.filter(
                Folder.parent_id == str(folder_id),
                Folder.deleted_at.is_(None),
            )
            file_query = File.query.filter(
                File.folder_id == str(folder_id),
                File.deleted_at.is_(None),
            )
        elif dataroom_id:
            FolderService._get_active_dataroom(dataroom_id)
            folder_query = Folder.query.filter(
                Folder.dataroom_id == str(dataroom_id),
                Folder.parent_id.is_(None),
                Folder.deleted_at.is_(None),
            )
            file_query = File.query.filter(
                File.dataroom_id == str(dataroom_id),
                File.folder_id.is_(None),
                File.deleted_at.is_(None),
            )
        else:
            raise NotFoundError('Either folder_id or dataroom_id is required')

        # Apply sorting
        folder_sort_col = getattr(Folder, sort_by, Folder.name)
        file_sort_col = getattr(File, sort_by, File.name)

        if sort_order == 'desc':
            folder_query = folder_query.order_by(folder_sort_col.desc())
            file_query = file_query.order_by(file_sort_col.desc())
        else:
            folder_query = folder_query.order_by(folder_sort_col.asc())
            file_query = file_query.order_by(file_sort_col.asc())

        folders_pagination = folder_query.paginate(
            page=page, per_page=per_page, error_out=False,
        )
        files_pagination = file_query.paginate(
            page=page, per_page=per_page, error_out=False,
        )

        return {
            'folder': current_folder.to_dict() if current_folder else None,
            'breadcrumbs': breadcrumbs,
            'folders': [f.to_dict() for f in folders_pagination.items],
            'files': [f.to_dict() for f in files_pagination.items],
            'pagination': {
                'total_folders': folders_pagination.total,
                'total_files': files_pagination.total,
                'page': page,
                'per_page': per_page,
            },
        }

    @staticmethod
    def _build_breadcrumbs(folder):
        """Build breadcrumbs from materialized path."""
        if not folder or not folder.path:
            return []

        # Path is like /uuid1/uuid2/uuid3 - extract ancestor IDs
        parts = [p for p in folder.path.split('/') if p]
        if not parts:
            return []

        ancestors = Folder.query.filter(
            Folder.id.in_(parts),
        ).all()

        # Sort them in path order
        ancestor_map = {a.id: a for a in ancestors}
        breadcrumbs = []
        for part_id in parts:
            ancestor = ancestor_map.get(part_id)
            if ancestor:
                breadcrumbs.append({
                    'id': ancestor.id,
                    'name': ancestor.name,
                })
        return breadcrumbs

    @staticmethod
    def rename(folder_id, name):
        name = validate_folder_name(name)
        folder = FolderService.get(folder_id)

        # Check uniqueness in same parent
        uniqueness_query = Folder.query.filter(
            Folder.dataroom_id == folder.dataroom_id,
            Folder.name == name,
            Folder.deleted_at.is_(None),
            Folder.id != str(folder_id),
        )
        if folder.parent_id:
            uniqueness_query = uniqueness_query.filter(
                Folder.parent_id == folder.parent_id,
            )
        else:
            uniqueness_query = uniqueness_query.filter(Folder.parent_id.is_(None))

        if uniqueness_query.first():
            raise ConflictError(f'A folder named "{name}" already exists in this location')

        folder.name = name
        folder.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return folder

    @staticmethod
    def delete(folder_id):
        folder = FolderService.get(folder_id)
        now = datetime.now(timezone.utc)

        # Find all descendant folders via materialized path
        descendant_folders = Folder.query.filter(
            Folder.path.like(f'{folder.path}/%'),
            Folder.deleted_at.is_(None),
        ).all()

        all_folder_ids = [str(folder_id)] + [f.id for f in descendant_folders]

        # Soft-delete all descendant folders
        Folder.query.filter(
            Folder.id.in_(all_folder_ids),
            Folder.deleted_at.is_(None),
        ).update({'deleted_at': now}, synchronize_session='fetch')

        # Soft-delete all files in those folders
        File.query.filter(
            File.folder_id.in_(all_folder_ids),
            File.deleted_at.is_(None),
        ).update({'deleted_at': now}, synchronize_session='fetch')

        db.session.commit()

    @staticmethod
    def get_tree(dataroom_id):
        FolderService._get_active_dataroom(dataroom_id)

        folders = Folder.query.filter(
            Folder.dataroom_id == str(dataroom_id),
            Folder.deleted_at.is_(None),
        ).order_by(Folder.name.asc()).all()

        # Build tree in memory
        folder_map = {}
        for f in folders:
            folder_map[f.id] = {
                **f.to_dict(),
                'children': [],
            }

        roots = []
        for f in folders:
            node = folder_map[f.id]
            if f.parent_id and f.parent_id in folder_map:
                folder_map[f.parent_id]['children'].append(node)
            else:
                roots.append(node)

        return roots
