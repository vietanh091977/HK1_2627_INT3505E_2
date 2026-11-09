from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Product
from ..schemas import PaginationSchema, ProductCreateSchema, ProductPatchSchema, ProductSchema, ReserveSchema

blp = Blueprint("products", __name__, description="Product catalog and inventory")


def visible_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        abort(404, message=f"product {product_id} not found")
    return product


@blp.route("")
class ProductList(MethodView):
    @blp.arguments(PaginationSchema, location="query")
    def get(self, args):
        base = select(Product).where(Product.archived.is_(False)).order_by(Product.id)
        total = db.session.scalar(select(func.count()).select_from(Product).where(Product.archived.is_(False)))
        products = db.session.scalars(
            base.options(selectinload(Product.order_items)).offset((args["page"] - 1) * args["size"]).limit(args["size"])
        ).all()
        return {"items": ProductSchema(many=True).dump(products), "page": args["page"], "size": args["size"], "total": total}

    @blp.arguments(ProductCreateSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        product = Product(**data)
        db.session.add(product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="sku already exists")
        return product


@blp.route("/<int:product_id>")
class ProductResource(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        return visible_product(product_id)

    @blp.arguments(ProductPatchSchema)
    @blp.response(200, ProductSchema)
    def patch(self, data, product_id):
        product = visible_product(product_id)
        for key, value in data.items():
            setattr(product, key, value)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="sku already exists")
        return product

    @blp.response(204)
    def delete(self, product_id):
        product = visible_product(product_id)
        product.archived = True
        db.session.commit()
        return "", 204


@blp.route("/<int:product_id>/reserve")
class ProductReserve(MethodView):
    @blp.arguments(ReserveSchema)
    @blp.response(200, ProductSchema)
    def post(self, data, product_id):
        visible_product(product_id)
        result = db.session.execute(
            update(Product)
            .where(Product.id == product_id, Product.archived.is_(False), Product.qty_in_stock >= data["qty"])
            .values(qty_in_stock=Product.qty_in_stock - data["qty"])
        )
        if result.rowcount != 1:
            db.session.rollback()
            abort(409, message="insufficient stock")
        db.session.commit()
        return visible_product(product_id)
