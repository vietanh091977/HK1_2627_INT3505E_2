from flask import Flask, jsonify
from flask_smorest import Api
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from .extensions import db, migrate


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        API_TITLE="Product and Order API",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        MAX_CONTENT_LENGTH=1024 * 1024,
        SECRET_KEY="development-only-change-me",
    )
    if test_config:
        app.config.update(test_config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = __import__("os").environ.get(
            "DATABASE_URL", "sqlite:///product_service.db"
        )

    db.init_app(app)
    migrate.init_app(app, db)
    api = Api(app)

    from .api.health import blp as health_blp
    from .api.products import blp as products_blp
    from .api.orders import blp as orders_blp

    api.register_blueprint(health_blp)
    api.register_blueprint(products_blp, url_prefix="/api/v1/products")
    api.register_blueprint(orders_blp, url_prefix="/api/v1/orders")

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.name.lower().replace(" ", "_"), detail=error.description), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled request error")
        return jsonify(error="internal_server_error", detail="An unexpected error occurred."), 500

    return app


def database_is_ready():
    db.session.execute(text("SELECT 1"))
    return True
