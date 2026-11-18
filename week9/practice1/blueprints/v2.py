from flask import Blueprint, request
from .users_data import get_user, USERS

bp = Blueprint("v2", __name__, url_prefix="/users")

@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "not found"}, 404
    return {
        "id": uid,
        "first_name": u["first_name"],
        "last_name": u["last_name"],
        "email": u["email"],
    }

@bp.route("", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    missing = [k for k in ("first_name", "last_name", "email") if k not in data]
    if missing:
        return {"error": f"missing fields: {missing}"}, 400
    uid = max(USERS) + 1
    USERS[uid] = {k: data[k] for k in ("first_name", "last_name", "email")}
    return {"id": uid, **USERS[uid]}, 201