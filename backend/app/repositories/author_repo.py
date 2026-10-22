from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from backend.app.models.author import Author
from backend.app.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[Author]):
    def __init__(self, db: Session):
        super().__init__(Author, db)

    def get_by_email(self, email: str) -> Optional[Author]:
        stmt = select(Author).where(Author.email == email)
        return self.db.scalars(stmt).first()

    def get_by_id_with_books(self, author_id: str) -> Optional[Author]:
        stmt = (
            select(Author)
            .options(selectinload(Author.books))
            .where(Author.id == author_id)
        )
        return self.db.scalars(stmt).first()

    def list_with_books(self, skip: int = 0, limit: int = 100) -> List[Author]:
        stmt = (
            select(Author)
            .options(selectinload(Author.books))
            .order_by(Author.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
