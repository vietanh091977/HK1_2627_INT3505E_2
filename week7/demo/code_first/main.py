import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate
from store import Store, SkuExists

db = Store()


class ProductInSchema(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))


class ProductSchema(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()
    qty_in_stock = fields.Int()


blp = Blueprint("products", __name__, description="Product API (Code-first)")


@blp.route("")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return db.all()

    @blp.arguments(ProductInSchema) # validate body (sai -> 422)
    @blp.response(201, ProductSchema)
    def post(self, data):
        try:
            return db.create(data)
        except SkuExists:
            abort(409, message="sku already exists")


@blp.route("/<int:id>")
class ProductItem(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, id):
        p = db.get(id)
        if p is None:
            abort(404, message=f"product {id} not found")
        return p


def create_app():
    app = Flask(__name__)
    app.config.update(
        API_TITLE="Product API (Code-first)", API_VERSION="1.0.0",
        OPENAPI_VERSION="3.0.3", OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json", OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )
    api = Api(app)
    api.register_blueprint(blp, url_prefix="/api/v1/products")
    return app


app = create_app()

if __name__ == "__main__":
    # Spec: http://localhost:5002/openapi.json
    # UI: http://localhost:5002/docs
    app.run(port=5002)
