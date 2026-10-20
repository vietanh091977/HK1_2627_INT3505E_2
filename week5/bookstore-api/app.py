import random

import click
from flask import Flask, jsonify
from sqlalchemy import func, select
from werkzeug.exceptions import HTTPException

from models import Author, Book, BookAuthor, Category, Review, User, db


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///bookstore.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config:
        app.config.update(config)
    app.json.sort_keys = False

    db.init_app(app)

    from routes.books import bp as books_bp

    app.register_blueprint(books_bp)

    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok"})
    
    @app.errorhandler(HTTPException)
    def http_error(e):
        return (
            jsonify(
                {
                    "error": e.name.lower().replace(" ", "_"),
                    "message": e.description,
                }
            ),
            e.code,
        )

    with app.app_context():
        db.create_all()

    register_cli(app)
    return app


# Seed data
GENRES = [
    ("tech", "Technology"),
    ("novel", "Novel"),
    ("science", "Science"),
    ("history", "History"),
    ("kids", "Kids"),
]
AUTHOR_NAMES = [
    "Robert C. Martin", "Martin Fowler", "Kent Beck", "Nguyen Nhat Anh",
    "Yuval Noah Harari", "Carl Sagan", "Eric Evans", "To Hoai",
]
TITLES = [
    "Clean Code", "Refactoring", "Domain-Driven Design", "Sapiens",
    "Cosmos", "De Men Phieu Luu Ky", "Test Driven Development",
    "API Design Patterns", "Mat Biec", "Pragmatic Programmer",
]
PRICES = [90000, 120000, 150000, 200000, 250000, 450000]
STOCKS = [0, 0, 3, 10, 25]


def seed_data(count: int = 60) -> bool:
    if db.session.scalar(select(func.count(Book.id))):
        return False

    rnd = random.Random(42)

    cats = [Category(slug=s, name=n) for s, n in GENRES]
    authors = [Author(name=n, bio=f"Bio of {n}") for n in AUTHOR_NAMES]
    users = [
        User(email=f"user{i}@example.com", display_name=f"User {i}")
        for i in range(1, 4)
    ]
    db.session.add_all(cats + authors + users)
    db.session.flush()

    books = []
    for i in range(1, count + 1):
        b = Book(
            title=rnd.choice(TITLES),
            isbn=str(9780000000000 + i),
            price_vnd=rnd.choice(PRICES),
            stock=rnd.choice(STOCKS),
            category_id=rnd.choice(cats).id,
            description=f"Description of book {i}",
        )
        for n, a in enumerate(rnd.sample(authors, rnd.randint(1, 2))):
            b.author_links.append(BookAuthor(author=a, role="lead" if n == 0 else "co"))
        books.append(b)
    db.session.add_all(books)
    db.session.flush()

    for b in books[:20]:
        for u in users:
            db.session.add(
                Review(book_id=b.id, user_id=u.id, rating=rnd.randint(1, 5))
            )
    db.session.commit()
    return True


def register_cli(app: Flask):
    @app.cli.command("seed")
    @click.option("--count", default=60, show_default=True, help="Số sách mẫu")
    def seed_cmd(count):
        click.echo(
            f"Seeded {count} books." if seed_data(count) else "DB đã có dữ liệu, bỏ qua."
        )

    @app.cli.command("reset-db")
    def reset_cmd():
        db.drop_all()
        db.create_all()
        click.echo("Database reset.")


if __name__ == "__main__":
    create_app().run(debug=True)