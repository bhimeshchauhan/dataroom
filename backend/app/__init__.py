import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate

from app.extensions import limiter
from app.models import db
from app.services.storage_service import build_storage_backend

logger = logging.getLogger(__name__)


migrate = Migrate()

# Partial unique indexes and btree indexes for PostgreSQL
INDEX_SQL = [
    "ALTER TABLE datarooms ADD COLUMN IF NOT EXISTS user_id VARCHAR(36);",
    "DROP INDEX IF EXISTS uq_active_dataroom_name;",
    "DROP INDEX IF EXISTS uq_active_dataroom_name_owner;",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_active_dataroom_name_owner ON datarooms (user_id, name) WHERE deleted_at IS NULL;",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_active_folder_name ON folders (dataroom_id, COALESCE(parent_id, '00000000-0000-0000-0000-000000000000'), name) WHERE deleted_at IS NULL;",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_active_file_name ON files (dataroom_id, COALESCE(folder_id, '00000000-0000-0000-0000-000000000000'), name) WHERE deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_folders_path ON folders USING btree (path text_pattern_ops);",
    "CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders (parent_id) WHERE deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_folders_dataroom ON folders (dataroom_id) WHERE parent_id IS NULL AND deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_files_folder ON files (folder_id) WHERE deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_files_dataroom_root ON files (dataroom_id) WHERE folder_id IS NULL AND deleted_at IS NULL;",
]


def create_app(config_name=None):
    app = Flask(__name__)

    # Load config
    if config_name == 'testing':
        from app.config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config import Config
        app.config.from_object(Config)

    # flask-smorest / OpenAPI configuration
    app.config.setdefault('API_TITLE', 'Dataroom API')
    app.config.setdefault('API_VERSION', 'v1')
    app.config.setdefault('OPENAPI_VERSION', '3.0.3')
    app.config.setdefault('OPENAPI_URL_PREFIX', '/api')
    app.config.setdefault('OPENAPI_SWAGGER_UI_PATH', '/docs')
    app.config.setdefault('OPENAPI_SWAGGER_UI_URL', 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/')

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')

        is_pdf_content = (
            request.path.startswith('/api/v1/files/')
            and request.path.endswith('/content')
        )

        if is_pdf_content:
            # Allow iframe embedding from configured frontend origins.
            origins = [o.strip() for o in app.config.get('CORS_ORIGINS', []) if o.strip()]
            frame_ancestors = " ".join(["'self'"] + origins)
            response.headers['Content-Security-Policy'] = f'frame-ancestors {frame_ancestors};'
            response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
            response.headers.pop('X-Frame-Options', None)
        else:
            response.headers.setdefault('X-Frame-Options', 'DENY')
            response.headers.setdefault('Cross-Origin-Resource-Policy', 'same-site')

        return response

    with app.app_context():
        db.create_all()

        # Create PostgreSQL-specific indexes; skip on SQLite
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri:
            try:
                with db.engine.connect() as conn:
                    for sql in INDEX_SQL:
                        conn.execute(db.text(sql))
                    conn.commit()
                logger.info('Database indexes created successfully')
            except Exception as e:
                if app.config.get('ENV') == 'production' or not app.debug:
                    raise RuntimeError(
                        f'Failed to create required database indexes: {e}'
                    ) from e
                logger.warning('Index creation failed (non-production): %s', e)

        # Validate and initialize configured storage backend.
        # Local backend creates storage directory here.
        build_storage_backend(app.config)

    return app
