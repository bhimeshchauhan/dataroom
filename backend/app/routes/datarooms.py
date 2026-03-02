from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.dataroom_service import DataroomService
from app.services.folder_service import FolderService
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
)
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
    def get(self):
        """List all datarooms."""
        page, per_page = validate_pagination(request.args)
        result = DataroomService.list_all(page=page, per_page=per_page)
        return jsonify(result), 200

    @datarooms_bp.arguments(DataroomCreateSchema, location='json')
    @datarooms_bp.response(201, DataroomSchema)
    @datarooms_bp.alt_response(409, schema=AppErrorSchema, description='Duplicate name')
    def post(self, json_data):
        """Create a dataroom."""
        dataroom = DataroomService.create(
            name=json_data.get('name'),
            description=json_data.get('description'),
        )
        return jsonify(dataroom.to_dict()), 201


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>')
class DataroomDetail(MethodView):

    @datarooms_bp.response(200, DataroomSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    def get(self, dataroom_id):
        """Get a dataroom by ID."""
        dataroom = DataroomService.get(dataroom_id)
        return jsonify(dataroom.to_dict()), 200

    @datarooms_bp.arguments(DataroomUpdateSchema, location='json')
    @datarooms_bp.response(200, DataroomSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    def patch(self, json_data, dataroom_id):
        """Update a dataroom."""
        dataroom = DataroomService.update(
            dataroom_id=dataroom_id,
            name=json_data.get('name'),
            description=json_data.get('description'),
        )
        return jsonify(dataroom.to_dict()), 200

    @datarooms_bp.response(204)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    def delete(self, dataroom_id):
        """Delete a dataroom (soft-delete)."""
        DataroomService.delete(dataroom_id)
        return '', 204


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>/contents')
class DataroomContents(MethodView):

    @datarooms_bp.response(200, ContentsSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    def get(self, dataroom_id):
        """Get root-level contents of a dataroom."""
        page, per_page = validate_pagination(request.args)
        sort_by, sort_order = validate_sort(request.args)
        result = FolderService.get_contents(
            dataroom_id=dataroom_id,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200


@datarooms_bp.route('/datarooms/<uuid:dataroom_id>/tree')
class DataroomTree(MethodView):

    @datarooms_bp.response(200, TreeSchema)
    @datarooms_bp.alt_response(404, schema=AppErrorSchema, description='Not found')
    def get(self, dataroom_id):
        """Get the folder tree of a dataroom."""
        tree = FolderService.get_tree(dataroom_id)
        return jsonify({'tree': tree}), 200
