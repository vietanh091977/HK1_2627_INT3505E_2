from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

db = SQLAlchemy()


# Category  (1:N Book)
class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}



# Book  (N:1 Category, N:M Author, 1:N Review)
class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    price_vnd: Mapped[int] = mapped_column(nullable=False, default=0)
    stock: Mapped[int] = mapped_column(nullable=False, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), index=True
    )

    category: Mapped[Optional[Category]] = relationship(
        back_populates="books", lazy="selectin"
    )
    author_links: Mapped[list["BookAuthor"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", lazy="selectin"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_books_price_id", "price_vnd", "id"),
        Index("ix_books_title_id", "title", "id"),
        Index("ix_books_stock_id", "stock", "id"),
    )

    @property
    def authors(self):
        return [link.author for link in self.author_links]

    def to_dict(self, fields=None):
        full = {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "description": self.description,
            "category": self.category.to_dict() if self.category else None,
            "authors": [
                {"id": l.author_id, "name": l.author.name, "role": l.role}
                for l in self.author_links
            ],
            "price": {"amount": self.price_vnd, "currency": "VND"},
            "inStock": self.stock > 0,
        }
        if fields is None:
            return full
        return {k: v for k, v in full.items() if k in fields}


# Author  (N:M Book)
class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    book_links: Mapped[list["BookAuthor"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class BookAuthor(db.Model):
    __tablename__ = "book_authors"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="co")

    book: Mapped[Book] = relationship(back_populates="author_links")
    author: Mapped[Author] = relationship(
        back_populates="book_links", lazy="joined"
    )

    __table_args__ = (
        CheckConstraint("role IN ('lead','co','ed')", name="ck_book_authors_role"),
    )

    def to_dict(self):
        return {
            "bookId": f"book_{self.book_id}",
            "authorId": self.author_id,
            "role": self.role,
        }


# User  (1:N Review)
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")

    def to_dict(self):
        return {"id": f"user_{self.id}", "displayName": self.display_name}


# Review  (N:1 Book, N:1 User)
class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    book: Mapped[Book] = relationship(back_populates="reviews")
    user: Mapped[User] = relationship(back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating"),
    )

    def to_dict(self):
        return {
            "id": f"review_{self.id}",
            "bookId": f"book_{self.book_id}",
            "userId": f"user_{self.user_id}",
            "rating": self.rating,
            "comment": self.comment,
        }