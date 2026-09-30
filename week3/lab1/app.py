from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

POSTS = [
    {
        "id": 1,
        "title": "Title 1",
        "content": "Content 1",
        "author_id": 1
    },
    {
        "id": 2,
        "title": "Title 2",
        "content": "Content 2",
        "author_id": 2
    }
]


# GET /api/v1/posts
@app.get("/api/v1/posts")
def list_posts():
    return jsonify(POSTS), 200


# GET /api/v1/posts/<id>
@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return jsonify(post), 200

    return jsonify({"error": "post not found"}), 404


# POST /api/v1/posts
@app.post("/api/v1/posts")
def create_post():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")

    if not title or not content or author_id is None:
        return jsonify({"error": "title, content and author_id are required"}), 400

    post = {
        "id": max([p["id"] for p in POSTS], default=0) + 1,
        "title": title,
        "content": content,
        "author_id": author_id
    }

    POSTS.append(post)

    return jsonify(post), 201


# PUT /api/v1/posts/<id>
@app.put("/api/v1/posts/<int:post_id>")
def replace_post(post_id):
    data = request.get_json(silent=True) or {}

    for post in POSTS:
        if post["id"] == post_id:

            if "title" not in data or "content" not in data:
                return jsonify({"error": "title and content are required"}), 400

            post["title"] = data["title"]
            post["content"] = data["content"]

            if "author_id" in data:
                post["author_id"] = data["author_id"]

            return jsonify(post), 200

    return jsonify({"error": "post not found"}), 404


# PATCH /api/v1/posts/<id>
@app.patch("/api/v1/posts/<int:post_id>")
def update_post(post_id):
    data = request.get_json(silent=True) or {}

    for post in POSTS:
        if post["id"] == post_id:

            if "title" in data:
                post["title"] = data["title"]

            if "content" in data:
                post["content"] = data["content"]

            if "author_id" in data:
                post["author_id"] = data["author_id"]

            return jsonify(post), 200

    return jsonify({"error": "post not found"}), 404


# DELETE /api/v1/posts/<id>
@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    for i, post in enumerate(POSTS):
        if post["id"] == post_id:
            deleted = POSTS.pop(i)

            return jsonify({"message": "post deleted", "post": deleted}), 200

    return jsonify({"error": "post not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)