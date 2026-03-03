from flask import jsonify
from flask_smorest import Api


api = Api()


def register_blueprints(app):
    api.init_app(app)

    from app.routes.datarooms import datarooms_bp
    from app.routes.folders import folders_bp
    from app.routes.files import files_bp
    from app.routes.auth import auth_bp

    api.register_blueprint(auth_bp)
    api.register_blueprint(datarooms_bp)
    api.register_blueprint(folders_bp)
    api.register_blueprint(files_bp)

    @app.route('/')
    def health():
        return jsonify({'status': 'ok', 'service': 'dataroom-api'})
