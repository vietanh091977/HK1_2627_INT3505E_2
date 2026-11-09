from flask_smorest import Blueprint
from sqlalchemy import text

from .. import database_is_ready
from ..extensions import db

blp = Blueprint("health", __name__, url_prefix="", description="Process and dependency health checks")


@blp.get("/healthz")
@blp.response(200)
def liveness():
    """Liveness only checks that the web process can serve a request."""
    return {"status": "ok"}


@blp.get("/ready")
@blp.response(200)
def readiness():
    """Readiness checks the database dependency separately from liveness."""
    try:
        database_is_ready()
        return {"status": "ready", "checks": {"database": "ok"}}
    except Exception:
        db.session.rollback()
        return {"status": "not_ready", "checks": {"database": "unavailable"}}, 503
