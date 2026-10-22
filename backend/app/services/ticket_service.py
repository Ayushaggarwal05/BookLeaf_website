import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote
from backend.app.models.author import Author
from backend.app.models.book import Book
from backend.app.models.user import User
from backend.app.repositories.ticket_repo import TicketRepository
from backend.app.schemas.ticket import TicketCreate, TicketUpdate
from backend.app.schemas.ticket_message import TicketMessageCreate
from backend.app.schemas.internal_note import TicketInternalNoteCreate


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TicketRepository(db)

    def generate_ticket_number(self) -> str:
        """Generate human-readable ticket number like TCK-2026-XXXX."""
        year = datetime.now(timezone.utc).year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"TCK-{year}-{suffix}"

    def create_ticket(self, data: TicketCreate) -> SupportTicket:
        """Create a new support ticket after validating author and book associations."""
        author = self.db.get(Author, data.author_id)
        if not author:
            raise ValueError(f"Author with ID '{data.author_id}' does not exist.")

        if data.book_id:
            book = self.db.get(Book, data.book_id)
            if not book:
                raise ValueError(f"Book with ID '{data.book_id}' does not exist.")
            if book.author_id != data.author_id:
                raise ValueError(f"Book '{data.book_id}' is not authored by '{data.author_id}'.")

        ticket_number = data.ticket_number or self.generate_ticket_number()

        ticket = SupportTicket(
            ticket_number=ticket_number,
            author_id=data.author_id,
            book_id=data.book_id,
            subject=data.subject,
            description=data.description,
            category=data.category,
            priority=data.priority,
            status=data.status,
            assigned_to_id=data.assigned_to_id,
            ai_classification=data.ai_classification,
        )
        self.repo.create(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_ticket_detail(self, ticket_id: str) -> Optional[SupportTicket]:
        return self.repo.get_detail(ticket_id)

    def list_author_tickets(self, author_id: str, skip: int = 0, limit: int = 100) -> List[SupportTicket]:
        return self.repo.list_by_author(author_id, skip=skip, limit=limit)

    def update_ticket(self, ticket_id: str, data: TicketUpdate) -> Optional[SupportTicket]:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)

        if data.status in ["RESOLVED", "CLOSED"] and not ticket.resolved_at:
            ticket.resolved_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def add_message(self, ticket_id: str, message_in: TicketMessageCreate) -> TicketMessage:
        """Add an author-visible reply to the ticket thread."""
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with ID '{ticket_id}' not found.")

        msg = TicketMessage(
            ticket_id=ticket_id,
            sender_type=message_in.sender_type,
            sender_id=message_in.sender_id,
            sender_name=message_in.sender_name,
            message_body=message_in.message_body,
            attachments=message_in.attachments,
        )
        self.repo.add_message(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def add_internal_note(self, ticket_id: str, note_in: TicketInternalNoteCreate) -> TicketInternalNote:
        """Add a staff-only private note to the ticket."""
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with ID '{ticket_id}' not found.")

        staff_user = self.db.get(User, note_in.author_user_id)
        if not staff_user:
            raise ValueError(f"Staff user with ID '{note_in.author_user_id}' not found.")

        note = TicketInternalNote(
            ticket_id=ticket_id,
            author_user_id=note_in.author_user_id,
            note_body=note_in.note_body,
        )
        self.repo.add_internal_note(note)
        self.db.commit()
        self.db.refresh(note)
        return note
