from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Order, OrderItem, Product
from ..schemas import OrderCreateSchema, OrderItemCreateSchema, OrderItemPatchSchema, OrderItemSchema, OrderSchema

blp = Blueprint("orders", __name__, description="Orders and order items")


def order_query():
    return select(Order).options(selectinload(Order.items).joinedload(OrderItem.product)).order_by(Order.id)


def get_order(order_id):
    order = db.session.scalars(order_query().where(Order.id == order_id)).first()
    if order is None:
        abort(404, message=f"order {order_id} not found")
    return order


def create_item(order, product_id, quantity):
    product = db.session.scalar(select(Product).where(Product.id == product_id, Product.archived.is_(False)))
    if product is None:
        abort(404, message=f"product {product_id} not found")
    updated = db.session.execute(
        update(Product).where(Product.id == product_id, Product.qty_in_stock >= quantity)
        .values(qty_in_stock=Product.qty_in_stock - quantity)
    )
    if updated.rowcount != 1:
        abort(409, message=f"insufficient stock for product {product_id}")
    return OrderItem(product=product, quantity=quantity, unit_price_cents=product.price_cents)


@blp.route("")
class OrderList(MethodView):
    @blp.response(200, OrderSchema(many=True))
    def get(self):
        return db.session.scalars(order_query()).all()

    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderSchema)
    def post(self, data):
        order = Order(status="pending")
        db.session.add(order)
        try:
            for item_data in data["items"]:
                order.items.append(create_item(order, item_data["product_id"], item_data["quantity"]))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="an order cannot contain the same product more than once")
        except Exception:
            db.session.rollback()
            raise
        return db.session.scalars(order_query().where(Order.id == order.id)).one()


@blp.route("/<int:order_id>")
class OrderResource(MethodView):
    @blp.response(200, OrderSchema)
    def get(self, order_id):
        return get_order(order_id)


@blp.route("/<int:order_id>/items")
class OrderItemList(MethodView):
    @blp.response(200, OrderItemSchema(many=True))
    def get(self, order_id):
        order = get_order(order_id)
        return order.items

    @blp.arguments(OrderItemCreateSchema)
    @blp.response(201, OrderItemSchema)
    def post(self, data, order_id):
        order = get_order(order_id)
        item = create_item(order, data["product_id"], data["quantity"])
        order.items.append(item)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="product already exists in this order")
        return item


@blp.route("/<int:order_id>/items/<int:item_id>")
class OrderItemResource(MethodView):
    @blp.response(200, OrderItemSchema)
    def get(self, order_id, item_id):
        order = get_order(order_id)
        item = next((row for row in order.items if row.id == item_id), None)
        if item is None:
            abort(404, message=f"order item {item_id} not found")
        return item

    @blp.arguments(OrderItemPatchSchema)
    @blp.response(200, OrderItemSchema)
    def patch(self, data, order_id, item_id):
        order = get_order(order_id)
        item = next((row for row in order.items if row.id == item_id), None)
        if item is None:
            abort(404, message=f"order item {item_id} not found")
        delta = data["quantity"] - item.quantity
        if delta > 0:
            changed = db.session.execute(update(Product).where(
                Product.id == item.product_id, Product.qty_in_stock >= delta
            ).values(qty_in_stock=Product.qty_in_stock - delta))
            if changed.rowcount != 1:
                db.session.rollback()
                abort(409, message="insufficient stock")
        elif delta < 0:
            db.session.execute(update(Product).where(Product.id == item.product_id).values(
                qty_in_stock=Product.qty_in_stock - delta
            ))
        item.quantity = data["quantity"]
        db.session.commit()
        return item

    @blp.response(204)
    def delete(self, order_id, item_id):
        order = get_order(order_id)
        item = next((row for row in order.items if row.id == item_id), None)
        if item is None:
            abort(404, message=f"order item {item_id} not found")
        db.session.execute(update(Product).where(Product.id == item.product_id).values(
            qty_in_stock=Product.qty_in_stock + item.quantity
        ))
        db.session.delete(item)
        db.session.commit()
        return "", 204

