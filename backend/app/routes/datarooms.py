from flask import request, jsonify, g
from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.dataroom_service import DataroomService
from app.services.folder_service import FolderService
from app.services.file_service import FileService
from app.schemas import (
    DataroomCreateSchema,
    DataroomUpdateSchema,
    DataroomSchema,
    DataroomListSchema,
    ContentsSchema,
    ContentQuerySchema,
    PaginationQuerySchema,
    TreeSchema,
    AppErrorSchema,
    StorageUsageSchema,
    HealthSchema,
)
from app.extensions import limiter
from app.utils.auth import require_auth
from app.utils.validation import validate_pagination, validate_sort

datarooms_bp = Blueprint(
    'datarooms',
    __name__,
    url_prefix='/api/v1',
    description='Operations on datarooms',
)


@datarooms_bp.route('/datarooms')
class DataroomList(MethodView):

    @datarooms_bp.response(200, DataroomListSchema)
    @limiter.limit('120/minute')
    @require_auth
    def get(self):
        """List all datarooms."""
        page, per_page = validate_pagination(request.args)
        result = DataroomService.list_all(
            page=page,
            per_page=per_page,
            user_id=g.current_user.id,
        )
        return jsonify(result), 200

    @datarooms_bp.arguments(DataroomCreateSchema, location='json')
    @datarooms_bp.response(201, DataroomSchema)
    @datarooms_bp.alt_response(409, schema=AppErrorSchema, description='Duplicate name')
    @limiter.limit('20/minute')
    @require_auth
    def post(self, json_data):
        """Create a dataroom."""
        dataroom = DataroomService.create(
            name=json_data.get('name'),
            description=json_data.get('description'),
            user_id=g.current_user.id,
        )
        return jsonify(dataroom.to_dict()), 201


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>')
class DataroomDetail(MethodView):

    @datarooms_bp.response(200, DataroomSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    @limiter.limit('120/minute')
    @require_auth
    def get(self, dataroom_id):
        """Get a dataroom by ID."""
        dataroom = DataroomService.get(dataroom_id, user_id=g.current_user.id)
        return jsonify(dataroom.to_dict()), 200

    @datarooms_bp.arguments(DataroomUpdateSchema, location='json')
    @datarooms_bp.response(200, DataroomSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    @limiter.limit('30/minute')
    @require_auth
    def patch(self, json_data, dataroom_id):
        """Update a dataroom."""
        dataroom = DataroomService.update(
            dataroom_id=dataroom_id,
            name=json_data.get('name'),
            description=json_data.get('description'),
            user_id=g.current_user.id,
        )
        return jsonify(dataroom.to_dict()), 200

    @datarooms_bp.response(204)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    @limiter.limit('20/minute')
    @require_auth
    def delete(self, dataroom_id):
        """Delete a dataroom (soft-delete)."""
        DataroomService.delete(dataroom_id, user_id=g.current_user.id)
        return '', 204


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>/contents')
class DataroomContents(MethodView):

    @datarooms_bp.response(200, ContentsSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    @limiter.limit('120/minute')
    @require_auth
    def get(self, dataroom_id):
        """Get root-level contents of a dataroom."""
        page, per_page = validate_pagination(request.args)
        sort_by, sort_order = validate_sort(request.args)
        search_query = (request.args.get('search') or '').strip() or None
        result = FolderService.get_contents(
            dataroom_id=dataroom_id,
            user_id=g.current_user.id,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            search_query=search_query,
        )
        return jsonify(result), 200


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>/tree')
class DataroomTree(MethodView):

    @datarooms_bp.response(200, TreeSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    @limiter.limit('120/minute')
    @require_auth
    def get(self, dataroom_id):
        """Get the folder tree of a dataroom."""
        tree = FolderService.get_tree(dataroom_id, user_id=g.current_user.id)
        return jsonify({'tree': tree}), 200


@datarooms_bp.route('/storage/usage')
class StorageUsage(MethodView):

    @datarooms_bp.response(200, StorageUsageSchema)
    @limiter.limit('120/minute')
    @require_auth
    def get(self):
        """Get current caller's free storage usage."""
        usage = FileService.get_usage(user_id=g.current_user.id)
        return jsonify(usage), 200


@datarooms_bp.route('/health')
class HealthCheck(MethodView):

    @datarooms_bp.response(200, HealthSchema)
    @limiter.limit('300/minute')
    def get(self):
        """Simple health check endpoint."""
        return jsonify({'status': 'ok'}), 200
