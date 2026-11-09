# Week 7: Product API

## Chạy bằng Docker Compose

Từ thư mục dự án:

```bash
docker compose up --build
```

API có tại `http://localhost:5000`; Swagger UI ở `/docs`, OpenAPI JSON ở `/openapi.json`.

## Chạy local với SQLite

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1         # macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
$env:FLASK_APP = "app:create_app"  # macOS/Linux: export FLASK_APP=app:create_app
flask db upgrade
flask run
```

## Chạy pytest

```bash
python -m pytest -q
```

## API

### Products - `/api/v1/products`

| Method | Endpoint |
|---|---|
| GET | `/api/v1/products?page=1&size=20` |
| GET | `/api/v1/products/{id}` |
| POST | `/api/v1/products` |
| POST | `/api/v1/products/{id}/reserve` |
| PATCH | `/api/v1/products/{id}` |
| DELETE | `/api/v1/products/{id}` |

### Orders và OrderItems - `/api/v1/orders`

| Method | Endpoint |
|---|---|
| GET | `/api/v1/orders` |
| POST | `/api/v1/orders` |
| GET | `/api/v1/orders/{order_id}` |
| GET | `/api/v1/orders/{order_id}/items` |
| POST | `/api/v1/orders/{order_id}/items` |
| GET | `/api/v1/orders/{order_id}/items/{item_id}` |
| PATCH | `/api/v1/orders/{order_id}/items/{item_id}` |
| DELETE | `/api/v1/orders/{order_id}/items/{item_id}` |

### Health checks

- `GET /healthz`: liveness, chỉ xác nhận tiến trình HTTP đang trả lời.
- `GET /ready`: readiness, kiểm tra kết nối database.

## Cấu trúc

- `app/__init__.py`: application factory, extensions và error handlers.
- `app/models.py`, `app/schemas.py`: ORM models và Marshmallow schemas.
- `app/api/products.py`: Product API.
- `app/api/orders.py`: Order và OrderItem resources.
- `app/api/health.py`: liveness/readiness.
- `migrations/`: Alembic migration tạo ba bảng và các ràng buộc.
- `tests/`: pytest và kiểm tra query count cho eager loading.
