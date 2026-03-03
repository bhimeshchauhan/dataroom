from flask import jsonify


class AppError(Exception):
    """Base application error."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message='Resource not found'):
        super().__init__(message, 404)


class ConflictError(AppError):
    """Resource conflict (e.g. duplicate name)."""

    def __init__(self, message='Resource already exists'):
        super().__init__(message, 409)


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message='Validation error'):
        super().__init__(message, 400)


class UnauthorizedError(AppError):
    """Authentication required or token invalid."""

    def __init__(self, message='Unauthorized'):
        super().__init__(message, 401)


def register_error_handlers(app):
    """Register JSON error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(413)
    def handle_request_entity_too_large(error):
        return jsonify({'error': 'File too large'}), 413

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
