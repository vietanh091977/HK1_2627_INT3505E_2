from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index, UniqueConstraint, func
from sqlalchemy.orm import relationship

from .extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_cents >= 0", name="ck_products_price_nonnegative"),
        CheckConstraint("qty_in_stock >= 0", name="ck_products_stock_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(32), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    qty_in_stock = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    archived = db.Column(db.Boolean, nullable=False, default=False, server_default="false", index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    order_items = relationship("OrderItem", back_populates="product", lazy="selectin")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default="pending", server_default="pending")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_items_order_product"),
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="ck_order_items_price_nonnegative"),
        Index("ix_order_items_product_id", "product_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Snapshot the price when the item is added; later catalog edits do not alter old orders.
    unit_price_cents = db.Column(db.Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items", lazy="joined")
