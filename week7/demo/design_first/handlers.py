import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from store import Store, SkuExists

db = Store()


def list_products():
    return db.all(), 200


def create_product(body):
    try:
        return db.create(body), 201
    except SkuExists:
        return {"code": "conflict", "message": "sku already exists"}, 409


def get_product(id):
    p = db.get(id)
    if p is None:
        return {"code": "not_found", "message": f"product {id} not found"}, 404
    return p, 200
