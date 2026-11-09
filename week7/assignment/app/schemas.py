from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class PaginationSchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    size = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class ProductCreateSchema(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Int(required=True, strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))


class ProductPatchSchema(Schema):
    sku = fields.Str(validate=validate.Length(min=3, max=32))
    name = fields.Str(validate=validate.Length(min=1, max=255))
    price_cents = fields.Int(strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(strict=True, validate=validate.Range(min=0))

    @validates_schema
    def require_change(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field is required.")


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ReserveSchema(Schema):
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderItemCreateSchema(Schema):
    product_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderItemPatchSchema(Schema):
    quantity = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderCreateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemCreateSchema), required=True, validate=validate.Length(min=1))


class OrderItemSchema(Schema):
    id = fields.Int(dump_only=True)
    order_id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()
    unit_price_cents = fields.Int()
    product = fields.Nested(ProductSchema, dump_only=True)


class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema))
