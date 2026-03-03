from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.folder_service import FolderService
from app.schemas import (
    FolderCreateSchema,
    FolderSchema,
    RenameSchema,
    ContentsSchema,
    AppErrorSchema,
)
from app.extensions import limiter
from app.utils.validation import validate_pagination, validate_sort
from app.utils.request_context import get_client_ip

folders_bp = Blueprint(
    "folders",
    __name__,
    url_prefix="/api/v1",
    description="Operations on folders",
)


@folders_bp.route("/datarooms/<uuid:dataroom_id>/folders")
class DataroomFolders(MethodView):

    @folders_bp.arguments(FolderCreateSchema, location="json")
    @folders_bp.response(201, FolderSchema)
    @folders_bp.alt_response(
        404, schema=AppErrorSchema, description="Dataroom or parent not found"
    )
    @folders_bp.alt_response(409, schema=AppErrorSchema, description="Duplicate name")
    @limiter.limit('30/minute')
    def post(self, json_data, dataroom_id):
        """Create a folder in a dataroom."""
        folder = FolderService.create(
            dataroom_id=dataroom_id,
            name=json_data.get("name"),
            parent_id=json_data.get("parent_id"),
            client_ip=get_client_ip(request),
        )
        return jsonify(folder.to_dict()), 201


@folders_bp.route("/folders/<uuid:folder_id>/contents")
class FolderContents(MethodView):

    @folders_bp.response(200, ContentsSchema)
    @folders_bp.alt_response(404, schema=AppErrorSchema, description="Folder not found")
    @limiter.limit('120/minute')
    def get(self, folder_id):
        """Get contents of a folder."""
        page, per_page = validate_pagination(request.args)
        sort_by, sort_order = validate_sort(request.args)
        search_query = (request.args.get('search') or '').strip() or None
        result = FolderService.get_contents(
            folder_id=folder_id,
            client_ip=get_client_ip(request),
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            search_query=search_query,
        )
        return jsonify(result), 200


@folders_bp.route("/folders/<uuid:folder_id>")
class FolderDetail(MethodView):

    @folders_bp.arguments(RenameSchema, location="json")
    @folders_bp.response(200, FolderSchema)
    @folders_bp.alt_response(404, schema=AppErrorSchema, description="Folder not found")
    @folders_bp.alt_response(409, schema=AppErrorSchema, description="Duplicate name")
    @limiter.limit('30/minute')
    def patch(self, json_data, folder_id):
        """Rename a folder."""
        folder = FolderService.rename(
            folder_id=folder_id,
            name=json_data.get("name"),
            client_ip=get_client_ip(request),
        )
        return jsonify(folder.to_dict()), 200

    @folders_bp.response(204)
    @folders_bp.alt_response(404, schema=AppErrorSchema, description="Folder not found")
    @limiter.limit('20/minute')
    def delete(self, folder_id):
        """Delete a folder and its descendants (soft-delete)."""
        FolderService.delete(folder_id, client_ip=get_client_ip(request))
        return "", 204
