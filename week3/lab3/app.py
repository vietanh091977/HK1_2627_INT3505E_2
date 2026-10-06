from flask import Flask, jsonify, request
import base64
import json
import uuid

app = Flask(__name__)
ERROR_BASE = 'https://api.example.com/probs'

STATUSES = ["pending", "paid", "shipped"]
ORDERS = [
    {
        "id": i,
        "customer_id": i % 5 + 1,
        "status": STATUSES[i % 3],
        "total": round(10 + i * 7.5, 2),
        "created_at": f"2026-01-{i % 28 + 1:02d}T10:00:00Z",
    }
    for i in range(1, 11)
]
SORTABLE = {"id", "created_at", "total"}
ALLOWED_FIELDS = {"id", "customer_id", "status", "total", "created_at"}
MAX_LIMIT = 100

class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        self.status, self.title, self.detail = status, title, detail
        self.type_path, self.extra = type_path, extra

@app.errorhandler(ApiProblem)
def handle_problem(e):
    body = {
        "type": f"{ERROR_BASE}/{e.type_path}" if e.type_path else "about:blank",
        "title": e.title,
        "status": e.status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4()),
    }
    if e.detail:
        body["detail"] = e.detail
    body.update(e.extra)
    resp = jsonify(body)
    resp.status_code = e.status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp

def encode_cursor(sort, value, last_id):
    raw = json.dumps({"sort": sort, "v": value, "id": last_id})
    return base64.urlsafe_b64encode(raw.encode()).decode()

def decode_cursor(token):
    try:
        data = json.loads(base64.urlsafe_b64decode(token.encode()))
        assert isinstance(data, dict) and {"sort", "v", "id"} <= data.keys()
        return data
    except Exception:
        raise ApiProblem(400, "Invalid cursor", detail="Cursor is malformed or expired.", type_path="invalid-cursor")


@app.get("/orders")
def list_orders():
    args = request.args

    # 1. limit
    try:
        limit = int(args.get("limit", 20))
    except ValueError:
        raise ApiProblem(400, "Invalid limit", "limit must be an integer")
    if not 1 <= limit <= MAX_LIMIT:
        raise ApiProblem(400, "Invalid limit", f"limit must be 1..{MAX_LIMIT}")

    # 2. sort
    sort = args.get("sort", "id")
    desc = sort.startswith("-")
    field = sort.lstrip("-")
    if field not in SORTABLE:
        raise ApiProblem(400, "Invalid sort field", f"Allowed: {sorted(SORTABLE)}")

    # 3. filter
    items = ORDERS
    if "status" in args:
        if args["status"] not in STATUSES:
            raise ApiProblem(400, "Invalid status", f"Allowed: {STATUSES}")
        items = [o for o in items if o["status"] == args["status"]]
    if "customer_id" in args:
        try:
            cid = int(args["customer_id"])
        except ValueError:
            raise ApiProblem(400, "Invalid customer_id")
        items = [o for o in items if o["customer_id"] == cid]

    # 4. sắp xếp theo (field, id)
    key = lambda o: (o[field], o["id"])
    items = sorted(items, key=key, reverse=desc)

    # 5. cursor
    if "cursor" in args:
        c = decode_cursor(args["cursor"])
        if c["sort"] != sort:
            raise ApiProblem(400, "Invalid cursor", "Cursor was issued for a different sort order.", type_path="invalid-cursor")
        last = (c["v"], c["id"])
        try:
            items = [o for o in items if (key(o) < last if desc else key(o) > last)]
        except TypeError:
            raise ApiProblem(400, "Invalid cursor", type_path="invalid-cursor")

    # 6. lấy limit + 1 để biết còn trang sau không
    page = items[:limit + 1]
    has_more = len(page) > limit
    page = page[:limit]

    next_cursor = None
    if has_more:
        last_item = page[-1]
        next_cursor = encode_cursor(sort, last_item[field], last_item["id"])

    # 7. sparse fieldsets
    if "fields" in args:
        wanted = [f for f in args["fields"].split(",") if f]
        bad = set(wanted) - ALLOWED_FIELDS
        if bad:
            raise ApiProblem(400, "Unknown field", f"Unknown: {sorted(bad)}")
        page = [{f: o[f] for f in wanted} for o in page]

    return jsonify({"data": page, "next_cursor": next_cursor, "has_more": has_more})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)