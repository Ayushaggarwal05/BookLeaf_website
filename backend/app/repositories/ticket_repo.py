from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote
from backend.app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[SupportTicket]):
    def __init__(self, db: Session):
        super().__init__(SupportTicket, db)

    def get_by_ticket_number(self, ticket_number: str) -> Optional[SupportTicket]:
        stmt = select(SupportTicket).where(SupportTicket.ticket_number == ticket_number)
        return self.db.scalars(stmt).first()

    def get_detail(self, ticket_id: str) -> Optional[SupportTicket]:
        stmt = (
            select(SupportTicket)
            .options(
                selectinload(SupportTicket.messages),
                selectinload(SupportTicket.internal_notes),
            )
            .where(SupportTicket.id == ticket_id)
        )
        return self.db.scalars(stmt).first()

    def list_by_author(self, author_id: str, skip: int = 0, limit: int = 100) -> List[SupportTicket]:
        stmt = (
            select(SupportTicket)
            .where(SupportTicket.author_id == author_id)
            .order_by(SupportTicket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def add_message(self, message: TicketMessage) -> TicketMessage:
        self.db.add(message)
        self.db.flush()
        return message

    def add_internal_note(self, note: TicketInternalNote) -> TicketInternalNote:
        self.db.add(note)
        self.db.flush()
        return note
