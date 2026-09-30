from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ProblemError(Exception):
    def __init__(
        self,
        status,
        title,
        detail,
        type="about:blank",
        instance=None
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.instance = instance

        super().__init__(detail)



def make_problem(
    status,
    title,
    detail,
    type="about:blank",
    instance=None
):
    response = {
        "type": type,
        "title": title,
        "status": status,
        "detail": detail
    }

    if instance is not None:
        response["instance"] = instance

    return jsonify(response), status



@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return make_problem(
        status=error.status,
        title=error.title,
        detail=error.detail,
        type=error.type,
        instance=error.instance or request.path
    )



@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return make_problem(
        status=error.code,
        title=error.name,
        detail=error.description,
        type="about:blank",
        instance=request.path
    )



@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Log đầy đủ traceback ở server
    logger.exception("Unhandled exception")

    # Không trả thông tin nội bộ cho client
    return make_problem(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        type="about:blank",
        instance=request.path
    )



@app.get("/resources/<int:resource_id>")
def get_resource(resource_id):

    if resource_id != 1:
        raise ProblemError(
            status=404,
            title="Resource Not Found",
            detail=f"Resource {resource_id} was not found",
            type="https://example.com/problems/resource-not-found",
            instance=request.path
        )

    return jsonify({
        "id": 1,
        "name": "Example Resource"
    })



@app.get("/test-http-error")
def test_http_error():
    from flask import abort

    abort(400, description="Invalid request")



@app.get("/test-500")
def test_500():
    x = 10 / 0

    return jsonify({"result": x})



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)