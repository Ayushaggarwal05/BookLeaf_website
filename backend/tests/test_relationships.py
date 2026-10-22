import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.author import Author
from backend.app.models.book import Book
from backend.app.models.user import User
from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote


def test_author_book_relationship(db: Session):
    """Test Author to Book 1-to-many relationship and back-population."""
    author = Author(
        id="AUTH_REL_01",
        name="Relationship Author",
        email="rel.author@example.com",
        joined_date=date(2024, 1, 1),
    )
    book1 = Book(
        id="BK_REL_01",
        author_id="AUTH_REL_01",
        title="Book One",
        isbn="978-0-123456-01-0",
        genre="Fiction",
        mrp=Decimal("299.00"),
        author_royalty_per_copy=Decimal("30.00"),
        total_copies_sold=10,
        total_royalty_earned=Decimal("300.00"),
        status="Published & Live",
    )
    book2 = Book(
        id="BK_REL_02",
        author_id="AUTH_REL_01",
        title="Book Two",
        isbn="978-0-123456-02-7",
        genre="Fiction",
        mrp=Decimal("399.00"),
        status="In Production",
    )
    author.books.extend([book1, book2])
    db.add(author)
    db.commit()

    reloaded = db.get(Author, "AUTH_REL_01")
    assert len(reloaded.books) == 2
    assert reloaded.books[0].author.name == "Relationship Author"


def test_ticket_conversations_and_internal_notes_segregation(db: Session):
    """
    Test that author-visible messages and internal notes are stored and retrieved
    via separate models and relationships.
    """
    author = Author(
        id="AUTH_TICK_01",
        name="Support Author",
        email="support.author@example.com",
        joined_date=date(2024, 1, 1),
    )
    staff = User(
        id="USR_STAFF_01",
        email="staff@bookleaf.in",
        full_name="Agent Smith",
        role="SUPPORT_AGENT",
    )
    db.add_all([author, staff])
    db.commit()

    ticket = SupportTicket(
        id="TCK_THREAD_01",
        ticket_number="TCK-2026-THREAD",
        author_id="AUTH_TICK_01",
        subject="Printing Issue",
        description="Pages 20-25 are faded.",
        category="PRINT_QUALITY",
        priority="HIGH",
        status="OPEN",
        assigned_to_id="USR_STAFF_01",
    )
    db.add(ticket)
    db.commit()

    # Add author-visible reply
    public_msg = TicketMessage(
        id="MSG_01",
        ticket_id="TCK_THREAD_01",
        sender_type="SUPPORT_AGENT",
        sender_id="USR_STAFF_01",
        sender_name="Agent Smith",
        message_body="We have initiated a replacement copy for you.",
    )
    # Add private internal note
    private_note = TicketInternalNote(
        id="NOTE_01",
        ticket_id="TCK_THREAD_01",
        author_user_id="USR_STAFF_01",
        note_body="Print partner Repro India contacted. Job batch #4401 investigated.",
    )
    db.add_all([public_msg, private_note])
    db.commit()

    reloaded_ticket = db.get(SupportTicket, "TCK_THREAD_01")
    assert len(reloaded_ticket.messages) == 1
    assert reloaded_ticket.messages[0].sender_type == "SUPPORT_AGENT"
    assert reloaded_ticket.messages[0].message_body == "We have initiated a replacement copy for you."

    assert len(reloaded_ticket.internal_notes) == 1
    assert reloaded_ticket.internal_notes[0].author_user_id == "USR_STAFF_01"
    assert "Print partner" in reloaded_ticket.internal_notes[0].note_body


def test_foreign_key_violation_raises_integrity_error(db: Session):
    """Test that inserting a book with a non-existent author fails foreign key constraint."""
    book = Book(
        id="BK_ORPHAN",
        author_id="NON_EXISTENT_AUTHOR",
        title="Orphan Book",
        isbn="978-0-000000-00-0",
        genre="Mystery",
        status="Draft",
    )
    db.add(book)
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()
