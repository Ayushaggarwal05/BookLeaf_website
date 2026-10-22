from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.services.seed_service import import_sample_data
from backend.app.models.user import User


def test_authors_and_books_api_endpoints(client: TestClient, db: Session):
    """Test authors and books listing and detail retrieval via REST API."""
    import_sample_data(db)

    # 1. List authors
    res = client.get("/api/authors")
    assert res.status_code == 200
    authors = res.json()
    assert len(authors) == 10
    first_author_id = authors[0]["id"]

    # 2. Get specific author detail with books
    res = client.get(f"/api/authors/{first_author_id}")
    assert res.status_code == 200
    author_detail = res.json()
    assert author_detail["id"] == first_author_id
    assert "books" in author_detail
    assert len(author_detail["books"]) >= 1

    # 3. List books with author filter
    res = client.get(f"/api/books?author_id={first_author_id}")
    assert res.status_code == 200
    books = res.json()
    assert len(books) == len(author_detail["books"])
    for b in books:
        assert b["author_id"] == first_author_id

    # 4. Get specific book detail
    book_id = books[0]["id"]
    res = client.get(f"/api/books/{book_id}")
    assert res.status_code == 200
    book_data = res.json()
    assert book_data["id"] == book_id
    assert "isbn" in book_data


def test_tickets_lifecycle_api(client: TestClient, db: Session):
    """Test full ticket flow: creation, author messages, internal notes, and updates."""
    import_sample_data(db)

    # Create staff user for notes
    staff = User(
        id="USR_STAFF_TEST",
        email="agent@bookleaf.in",
        full_name="Agent Sharma",
        role="SUPPORT_AGENT",
    )
    db.add(staff)
    db.commit()

    # 1. Create a support ticket
    ticket_payload = {
        "author_id": "AUTH001",
        "book_id": "BK001",
        "subject": "Missing Q3 Royalty Statement",
        "description": "I have not received my royalty statement for Q3 2025.",
        "category": "ROYALTY",
        "priority": "HIGH",
        "status": "OPEN",
    }
    res = client.post("/api/tickets", json=ticket_payload)
    assert res.status_code == 201
    created_ticket = res.json()
    ticket_id = created_ticket["id"]
    assert created_ticket["subject"] == "Missing Q3 Royalty Statement"
    assert created_ticket["ticket_number"].startswith("TCK-")

    # 2. Add an author-visible reply
    message_payload = {
        "sender_type": "SUPPORT_AGENT",
        "sender_id": "USR_STAFF_TEST",
        "sender_name": "Agent Sharma",
        "message_body": "Hello Priya, we are generating your Q3 statement now.",
    }
    res = client.post(f"/api/tickets/{ticket_id}/messages", json=message_payload)
    assert res.status_code == 201
    message_data = res.json()
    assert message_data["ticket_id"] == ticket_id

    # 3. Add private internal staff note
    note_payload = {
        "author_user_id": "USR_STAFF_TEST",
        "note_body": "Checked payouts table. Payout was sent on 2025-10-15 via NEFT.",
    }
    res = client.post(f"/api/tickets/{ticket_id}/notes", json=note_payload)
    assert res.status_code == 201
    note_data = res.json()
    assert note_data["ticket_id"] == ticket_id

    # 4. Get ticket detail with messages and internal notes
    res = client.get(f"/api/tickets/{ticket_id}")
    assert res.status_code == 200
    ticket_detail = res.json()
    assert len(ticket_detail["messages"]) == 1
    assert len(ticket_detail["internal_notes"]) == 1

    # 5. Update ticket status
    update_payload = {"status": "RESOLVED"}
    res = client.patch(f"/api/tickets/{ticket_id}", json=update_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "RESOLVED"
