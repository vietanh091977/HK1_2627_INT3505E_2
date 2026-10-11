import os
import uuid
from datetime import datetime, timezone
import yaml
from flask import Flask, jsonify, request, Response, render_template_string

app = Flask(__name__)

TASKS = {}

SWAGGER_UI_HTML = '''<!doctype html><html><head><title>Tasks API docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'});</script></body></html>'''


@app.route("/openapi.json", methods=["GET"])
def get_openapi_json():
    spec_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
    if not os.path.exists(spec_path):
        return jsonify({
            "type": "https://api.example.vn/errors/internal-error",
            "title": "Not Found",
            "status": 500,
            "detail": "Không tìm thấy file openapi.yaml"
        }), 500

    with open(spec_path, "r", encoding="utf-8") as f:
        spec_dict = yaml.safe_load(f)
    return jsonify(spec_dict)


@app.route("/docs", methods=["GET"])
def get_swagger_ui():
    return render_template_string(SWAGGER_UI_HTML)


@app.route("/v1/tasks", methods=["POST"])
def create_task():
    if not request.is_json:
        return jsonify({
            "type": "https://api.example.vn/errors/bad-request",
            "title": "Bad Request",
            "status": 400,
            "detail": "Request body phải có định dạng application/json.",
            "instance": "/v1/tasks"
        }), 400, {"Content-Type": "application/problem+json"}

    data = request.get_json()

    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({
            "type": "https://api.example.vn/errors/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Trường 'title' là bắt buộc và không được để trống.",
            "instance": "/v1/tasks"
        }), 422, {"Content-Type": "application/problem+json"}

    priority = data.get("priority", "normal")
    if priority not in ["low", "normal", "high"]:
        return jsonify({
            "type": "https://api.example.vn/errors/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Trường 'priority' chỉ được nhận một trong các giá trị: low, normal, high.",
            "instance": "/v1/tasks"
        }), 422, {"Content-Type": "application/problem+json"}

    due_date = data.get("dueDate")
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "type": "https://api.example.vn/errors/validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": "Trường 'dueDate' không đúng định dạng YYYY-MM-DD (RFC 3339).",
                "instance": "/v1/tasks"
            }), 422, {"Content-Type": "application/problem+json"}

    task_id = str(uuid.uuid4())
    new_task = {
        "id": task_id,
        "title": title.strip(),
        "status": "open",
        "priority": priority,
        "dueDate": due_date,
        "assigneeId": data.get("assigneeId"),
        "createdAt": datetime.now(timezone.utc).isoformat()
    }

    TASKS[task_id] = new_task

    location_url = f"/v1/tasks/{task_id}"
    response = jsonify(new_task)
    response.status_code = 201
    response.headers["Location"] = location_url
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)