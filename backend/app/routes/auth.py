from flask import jsonify, g
from flask.views import MethodView
from flask_smorest import Blueprint

from app.schemas import (
    AuthRegisterSchema,
    AuthLoginSchema,
    AuthResponseSchema,
    UserSchema,
    AppErrorSchema,
)
from app.services.auth_service import AuthService
from app.utils.auth import require_auth


auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/v1/auth',
    description='Authentication endpoints',
)


@auth_bp.route('/register')
class Register(MethodView):

    @auth_bp.arguments(AuthRegisterSchema, location='json')
    @auth_bp.response(201, AuthResponseSchema)
    @auth_bp.alt_response(409, schema=AppErrorSchema, description='Duplicate email')
    def post(self, json_data):
        result = AuthService.register(
            email=json_data.get('email'),
            password=json_data.get('password'),
        )
        return jsonify({
            'user': result['user'].to_dict(),
            'token': result['token'],
        }), 201


@auth_bp.route('/login')
class Login(MethodView):

    @auth_bp.arguments(AuthLoginSchema, location='json')
    @auth_bp.response(200, AuthResponseSchema)
    @auth_bp.alt_response(400, schema=AppErrorSchema, description='Invalid credentials')
    def post(self, json_data):
        result = AuthService.login(
            email=json_data.get('email'),
            password=json_data.get('password'),
        )
        return jsonify({
            'user': result['user'].to_dict(),
            'token': result['token'],
        }), 200


@auth_bp.route('/me')
class Me(MethodView):

    @auth_bp.response(200, UserSchema)
    @require_auth
    def get(self):
        return jsonify(g.current_user.to_dict()), 200
