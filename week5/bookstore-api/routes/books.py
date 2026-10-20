from flask import Blueprint, request, jsonify
from sqlalchemy import select, func
from models import db, Book
from helpers.query import *

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")
DEFAULT_LIMIT, MAX_LIMIT = 20, 100


@bp.errorhandler(ApiError)
def handle(e):
    return jsonify({"error": e.code, "message": e.message}), e.status


@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor")
    if strategy not in ("offset", "cursor"):
        raise ApiError("bad_strategy", "strategy must be offset or cursor")

    limit = request.args.get("limit", DEFAULT_LIMIT, type=int)
    limit = max(1, min(limit, MAX_LIMIT))
    keys = parse_sort(request.args.get("sort"))
    genre = request.args.get("genre")

    base = apply_filters(select(Book), request.args)
    q = base.order_by(*order_by_clauses(keys))

    if strategy == "offset":
        offset = max(0, request.args.get("offset", 0, type=int))
        total = db.session.scalar(
            select(func.count()).select_from(base.order_by(None).subquery()))
        rows = db.session.scalars(q.offset(offset).limit(limit)).all()
        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {"strategy": "offset", "offset": offset,
                           "limit": limit, "total": total,
                           "has_more": offset + limit < total},
        })

    q = apply_cursor(q, request.args.get("cursor"), keys, genre)
    rows = db.session.scalars(q.limit(limit + 1)).all()   # +1 trick
    has_more = len(rows) > limit
    rows = rows[:limit]
    nxt = make_next_cursor(rows[-1], keys, genre) if rows and has_more else None
    return jsonify({
        "data": [b.to_dict() for b in rows],
        "pagination": {"strategy": "cursor", "limit": limit,
                       "next_cursor": nxt, "has_more": has_more},
    })