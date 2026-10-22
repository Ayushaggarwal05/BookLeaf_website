from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from backend.app.models.book import Book
from backend.app.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, db: Session):
        super().__init__(Book, db)

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        stmt = select(Book).where(Book.isbn == isbn)
        return self.db.scalars(stmt).first()

    def list_by_author(self, author_id: str) -> List[Book]:
        stmt = select(Book).where(Book.author_id == author_id).order_by(Book.title)
        return list(self.db.scalars(stmt).all())

    def list_with_author(self, skip: int = 0, limit: int = 100) -> List[Book]:
        stmt = (
            select(Book)
            .options(joinedload(Book.author))
            .order_by(Book.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
