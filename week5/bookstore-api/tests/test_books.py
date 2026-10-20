import pytest
from app import create_app
from models import db, Book, Category


@pytest.fixture
def client():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://", "TESTING": True})
    with app.app_context():
        db.create_all()
        tech = Category(name="Tech", slug="tech")
        novel = Category(name="Novel", slug="novel")
        db.session.add_all([tech, novel])
        db.session.flush()
        for i in range(1, 46):
            db.session.add(Book(
                title=f"Book {i % 7}",
                isbn=f"{i:013d}",
                price_vnd=100000 * (1 + i % 4),
                stock=i % 3,
                category_id=tech.id if i % 2 else novel.id))
        db.session.commit()
        yield app.test_client()


def walk(client, query):
    ids, cursor = [], None
    while True:
        url = f"/api/v1/books?strategy=cursor&limit=7&{query}"
        if cursor:
            url += f"&cursor={cursor}"
        body = client.get(url).get_json()
        ids += [b["id"] for b in body["data"]]
        cursor = body["pagination"]["next_cursor"]
        if not body["pagination"]["has_more"]:
            return ids


@pytest.mark.parametrize("sort", ["-id", "price", "-price,title", "title,-price"])
def test_cursor_no_dup_no_skip(client, sort):
    ids = walk(client, f"sort={sort}")
    assert len(ids) == len(set(ids)) == 45

    full = client.get(
        f"/api/v1/books?strategy=offset&limit=100&sort={sort}").get_json()
    assert ids == [b["id"] for b in full["data"]]   # cùng thứ tự với offset


def test_offset_pagination(client):
    r = client.get("/api/v1/books?strategy=offset&offset=40&limit=10").get_json()
    assert len(r["data"]) == 5
    assert r["pagination"]["total"] == 45
    assert r["pagination"]["has_more"] is False


def test_genre_filter_with_total(client):
    r = client.get("/api/v1/books?strategy=offset&genre=tech&limit=100").get_json()
    assert r["pagination"]["total"] == 23
    assert len(walk(client, "genre=tech")) == 23


def test_limit_is_capped(client):
    r = client.get("/api/v1/books?strategy=offset&limit=9999").get_json()
    assert r["pagination"]["limit"] == 100


def test_errors(client):
    assert client.get("/api/v1/books?sort=foo").status_code == 400
    assert client.get("/api/v1/books?strategy=page").status_code == 400
    assert client.get("/api/v1/books?cursor=@@@").status_code == 400


def test_cursor_bound_to_sort(client):
    body = client.get("/api/v1/books?limit=5&sort=price").get_json()
    c = body["pagination"]["next_cursor"]
    r = client.get(f"/api/v1/books?sort=-price&cursor={c}")
    assert r.status_code == 400