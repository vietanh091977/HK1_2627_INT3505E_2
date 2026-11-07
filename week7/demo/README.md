# Demo: Code-first vs Design-first
Cùng một Product API (GET/POST /products, GET /products/{id}), cùng kho dữ liệu `store.py`

| | design_first/ (connexion) | code_first/ (flask-smorest) |
|---|---|---|
| Viết trước | `openapi.yaml` | `Schema` + `MethodView` |
| Nguồn sự thật | file YAML | code Python |
| Validate input | connexion tự làm theo YAML | Marshmallow (`@blp.arguments`) |
| Handler | hàm thường, tên = `operationId` | class `MethodView` |
| Spec/Docs | file có sẵn từ đầu | sinh ra tại `/openapi.json` |
| Lỗi validate | **400** (problem+json) | **422** (`errors.json.<field>`) |

## Chạy
```bash
pip install -r requirements.txt
cd design_first && python main.py     # http://localhost:5001/api/v1/ui/
cd code_first   && python main.py     # http://localhost:5002/docs  (spec: /openapi.json)
```
