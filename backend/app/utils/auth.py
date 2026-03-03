from functools import wraps

from flask import g, request

from app.services.auth_service import AuthService
from app.utils.errors import UnauthorizedError


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            raise UnauthorizedError('Authorization token is required')
        token = auth.split(' ', 1)[1].strip()
        if not token:
            raise UnauthorizedError('Authorization token is required')
        try:
            g.current_user = AuthService.get_user_from_token(token)
        except Exception as exc:  # noqa: BLE001
            raise UnauthorizedError(str(exc)) from exc
        return fn(*args, **kwargs)
    return wrapper
