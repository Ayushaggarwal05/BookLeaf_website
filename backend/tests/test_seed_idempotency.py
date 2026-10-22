from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.author import Author
from backend.app.models.book import Book
from backend.app.models.ticket import SupportTicket
from backend.app.services.seed_service import import_sample_data


def test_seed_first_run_and_idempotency(db: Session):
    """
    Test that running seed once imports all records,
    and running it a second time updates in place without duplicates.
    """
    # 1. First run
    summary_1 = import_sample_data(db)
    assert summary_1["status"] == "success"
    assert summary_1["authors_inserted"] == 10
    assert summary_1["books_inserted"] == 18
    assert summary_1["authors_updated"] == 0
    assert summary_1["books_updated"] == 0

    authors_count = db.query(Author).count()
    books_count = db.query(Book).count()
    assert authors_count == 10
    assert books_count == 18

    # 2. Second run
    summary_2 = import_sample_data(db)
    assert summary_2["status"] == "success"
    assert summary_2["authors_inserted"] == 0
    assert summary_2["books_inserted"] == 0
    assert summary_2["authors_updated"] == 10
    assert summary_2["books_updated"] == 18

    # Ensure counts have not changed
    assert db.query(Author).count() == 10
    assert db.query(Book).count() == 18


def test_seed_preserves_user_created_tickets(db: Session):
    """
    Test that seeding never removes or damages user-created tickets.
    """
    # Seed initial data
    import_sample_data(db)

    # Create a user ticket for author AUTH001
    ticket = SupportTicket(
        id="TCK_TEST_PRESERVE",
        ticket_number="TCK-2026-PRESERVE",
        author_id="AUTH001",
        book_id="BK001",
        subject="Royalty clarification",
        description="Please confirm the pending payout schedule.",
        category="ROYALTY",
        priority="HIGH",
        status="OPEN",
    )
    db.add(ticket)
    db.commit()

    # Re-run seed
    import_sample_data(db)

    # Verify ticket still exists intact
    persisted_ticket = db.get(SupportTicket, "TCK_TEST_PRESERVE")
    assert persisted_ticket is not None
    assert persisted_ticket.subject == "Royalty clarification"
    assert persisted_ticket.status == "OPEN"
    assert persisted_ticket.author_id == "AUTH001"
