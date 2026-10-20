import base64, json
from sqlalchemy import and_, or_
from models import Book, Category

SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title,
    "stock": Book.stock,
}
MAX_KEYS = 3


class ApiError(Exception):
    def __init__(self, code, message, status=400):
        self.code, self.message, self.status = code, message, status


def parse_sort(raw):
    """'-price,title' -> [(name, column, desc), ..., ('id', Book.id, desc)]"""
    keys, seen = [], set()
    for part in filter(None, (raw or "-id").split(",")):
        desc = part.startswith("-")
        name = part.lstrip("-")
        if name not in SORT_FIELDS:
            raise ApiError("bad_sort", f"Unknown sort field: {name}")
        if name in seen:
            raise ApiError("bad_sort", f"Duplicate sort field: {name}")
        seen.add(name)
        keys.append((name, SORT_FIELDS[name], desc))
    if len(keys) > MAX_KEYS:
        raise ApiError("bad_sort", f"Max {MAX_KEYS} sort keys")
    if "id" not in seen:
        keys.append(("id", Book.id, keys[-1][2]))
    return keys


def canonical_sort(keys):
    return ",".join(("-" if d else "") + n for n, _, d in keys)


def order_by_clauses(keys):
    return [c.desc() if d else c.asc() for _, c, d in keys]


def apply_filters(q, args):
    genre = args.get("genre")
    if genre:
        q = q.join(Category, Book.category_id == Category.id)\
             .filter(Category.slug == genre)
    if args.get("in_stock") == "true":
        q = q.filter(Book.stock > 0)
    p_min = args.get("price_min", type=int)
    p_max = args.get("price_max", type=int)
    if p_min is not None:
        q = q.filter(Book.price_vnd >= p_min)
    if p_max is not None:
        q = q.filter(Book.price_vnd <= p_max)
    return q


def enc(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")


def dec(t):
    try:
        return json.loads(base64.urlsafe_b64decode(t + "=" * (-len(t) % 4)))
    except Exception:
        raise ApiError("bad_cursor", "Invalid cursor")


def keyset_condition(keys, values):
    ors = []
    for i, (_, col, desc) in enumerate(keys):
        ands = [keys[j][1] == values[j] for j in range(i)]
        ands.append(col < values[i] if desc else col > values[i])
        ors.append(and_(*ands))
    return or_(*ors)


def apply_cursor(q, raw, keys, genre):
    if not raw:
        return q
    c = dec(raw)
    if c.get("s") != canonical_sort(keys) or c.get("g") != genre:
        raise ApiError("cursor_mismatch", "Cursor does not match sort/filter")
    return q.filter(keyset_condition(keys, c["v"]))


def make_next_cursor(last, keys, genre):
    return enc({
        "s": canonical_sort(keys),
        "g": genre,
        "v": [getattr(last, col.key) for _, col, _ in keys],
    })