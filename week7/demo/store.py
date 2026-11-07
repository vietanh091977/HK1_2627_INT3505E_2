
class SkuExists(Exception):
    pass


class Store:
    def __init__(self):
        self._items, self._next = {}, 1

    def all(self):
        return list(self._items.values())

    def get(self, id):
        return self._items.get(id)

    def create(self, data):
        if any(p["sku"] == data["sku"] for p in self._items.values()):
            raise SkuExists
        p = {"id": self._next, "qty_in_stock": 0, **data}
        self._items[self._next] = p
        self._next += 1
        return p
