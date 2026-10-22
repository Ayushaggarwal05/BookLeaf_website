from backend.app.repositories.base import BaseRepository
from backend.app.repositories.author_repo import AuthorRepository
from backend.app.repositories.book_repo import BookRepository
from backend.app.repositories.ticket_repo import TicketRepository

__all__ = [
    "BaseRepository",
    "AuthorRepository",
    "BookRepository",
    "TicketRepository",
]
