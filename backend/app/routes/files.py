from io import BytesIO

from flask import request, jsonify, send_file, g
from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.file_service import FileService
from app.schemas import (
    FileSchema,
    RenameSchema,
    AppErrorSchema,
)
from app.extensions import limiter
from app.services.auth_service import AuthService
from app.utils.auth import require_auth
from app.utils.errors import UnauthorizedError

files_bp = Blueprint(
    'files',
    __name__,
    url_prefix='/api/v1',
    description='Operations on files',
)


@files_bp.route('/datarooms/<uuid:dataroom_id>/files')
class DataroomFiles(MethodView):

    @files_bp.response(201, FileSchema)
    @files_bp.alt_response(400, schema=AppErrorSchema, description='Validation error')
    @files_bp.alt_response(404, schema=AppErrorSchema, description='Dataroom or folder not found')
    @files_bp.alt_response(409, schema=AppErrorSchema, description='Duplicate filename')
    @limiter.limit('10/5minutes')
    @require_auth
    @files_bp.doc(
        description='Upload a PDF file to a dataroom.',
        requestBody={
            'content': {
                'multipart/form-data': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'file': {
                                'type': 'string',
                                'format': 'binary',
                                'description': 'PDF file to upload',
                            },
                            'folder_id': {
                                'type': 'string',
                                'description': 'Optional folder ID to upload into',
                            },
                        },
                        'required': ['file'],
                    },
                },
            },
        },
    )
    def post(self, dataroom_id):
        """Upload a file to a dataroom."""
        file = request.files.get('file')
        folder_id = request.form.get('folder_id')
        file_record = FileService.upload(
            dataroom_id=dataroom_id,
            file=file,
            folder_id=folder_id,
            user_id=g.current_user.id,
        )
        return jsonify(file_record.to_dict()), 201


@files_bp.route('/files/<uuid:file_id>')
class FileDetail(MethodView):

    @files_bp.response(200, FileSchema)
    @files_bp.alt_response(404, schema=AppErrorSchema, description='File not found')
    @limiter.limit('120/minute')
    @require_auth
    def get(self, file_id):
        """Get file metadata."""
        file_record = FileService.get(file_id, user_id=g.current_user.id)
        return jsonify(file_record.to_dict()), 200

    @files_bp.arguments(RenameSchema, location='json')
    @files_bp.response(200, FileSchema)
    @files_bp.alt_response(404, schema=AppErrorSchema, description='File not found')
    @files_bp.alt_response(409, schema=AppErrorSchema, description='Duplicate filename')
    @limiter.limit('30/minute')
    @require_auth
    def patch(self, json_data, file_id):
        """Rename a file."""
        file_record = FileService.rename(
            file_id=file_id,
            name=json_data.get('name'),
            user_id=g.current_user.id,
        )
        return jsonify(file_record.to_dict()), 200

    @files_bp.response(204)
    @files_bp.alt_response(404, schema=AppErrorSchema, description='File not found')
    @limiter.limit('20/minute')
    @require_auth
    def delete(self, file_id):
        """Delete a file (soft-delete)."""
        FileService.delete(file_id, user_id=g.current_user.id)
        return '', 204


@files_bp.route('/files/<uuid:file_id>/content')
class FileContent(MethodView):

    @files_bp.response(200, description='PDF file content')
    @files_bp.alt_response(404, schema=AppErrorSchema, description='File not found')
    @limiter.limit('60/minute')
    @files_bp.doc(
        produces=['application/pdf'],
    )
    def get(self, file_id):
        """Download file content."""
        auth = request.headers.get('Authorization', '')
        token = None

        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        elif request.args.get('token'):
            token = request.args.get('token', '').strip()

        if not token:
            raise UnauthorizedError('Authorization token is required')

        try:
            user = AuthService.get_user_from_token(token)
        except Exception as exc:  # noqa: BLE001
            raise UnauthorizedError(str(exc)) from exc
        file_record = FileService.get(file_id, user_id=user.id)
        content = FileService.get_content(file_id, user_id=user.id)
        return send_file(
            BytesIO(content),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=file_record.name,
        )
