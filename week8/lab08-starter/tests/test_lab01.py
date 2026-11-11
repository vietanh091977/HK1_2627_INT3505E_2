"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

import copy

import pytest
from jsonschema import ValidationError, validate

from tools import get_book_schema


def test_list_books_empty_returns_empty_array(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == []


def test_get_unknown_book_returns_404_not_found(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_without_title_returns_400_with_title_error(client):
    response = client.post("/books", json={"author": "X"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    fields = {e["field"] for e in body.get("errors", [])}
    assert "title" in fields


def test_deleted_book_is_not_found_afterwards(client):
    created = client.post("/books", json={"title": "DDIA", "author": "Kleppmann"})
    assert created.status_code == 201
    book_id = created.get_json()["id"]

    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_response_extra_field_blocked(client):
    schema = get_book_schema()
    created = client.post(
        "/books",
        json={"title": "DDIA", "author": "Kleppmann", "year": 2017, "isbn": "9781449373320"},
    )
    book = client.get(f"/books/{created.get_json()['id']}").get_json()

    validate(book, schema)

    leaked = copy.deepcopy(book)
    leaked["password_hash"] = "abc123"
    with pytest.raises(ValidationError):
        validate(leaked, schema)