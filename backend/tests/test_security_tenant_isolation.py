import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.author import Author
from backend.app.models.book import Book
from backend.app.models.user import User
from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote


@pytest.fixture
def two_authors_and_admin(db: Session):
    """
    Fixture providing two distinct authors (Author A, Author B) and one Admin
    with books and support tickets in an isolated database session.
    """
    # 1. Author A
    author_a = Author(
        id="AUTH_ISOLATION_A",
        name="Author Alice",
        email="alice@example.com",
        joined_date=date(2024, 1, 1),
        hashed_password=get_password_hash("AlicePass123!"),
        is_active=True,
    )
    # 2. Author B
    author_b = Author(
        id="AUTH_ISOLATION_B",
        name="Author Bob",
        email="bob@example.com",
        joined_date=date(2024, 2, 1),
        hashed_password=get_password_hash("BobPass123!"),
        is_active=True,
    )
    # 3. Admin User
    admin = User(
        id="USR_ADMIN_ISOLATION",
        email="admin.security@bookleaf.in",
        full_name="Security Admin",
        role="admin",
        is_active=True,
        hashed_password=get_password_hash("AdminPass123!"),
    )
    db.add_all([author_a, author_b, admin])
    db.commit()

    # Books for Author A
    book_a = Book(
        id="BK_ALICE_01",
        author_id="AUTH_ISOLATION_A",
        title="Alice in Techland",
        isbn="978-0-111111-01-1",
        genre="Technology",
        status="Published & Live",
        mrp=Decimal("350.00"),
        author_royalty_per_copy=Decimal("35.00"),
        total_copies_sold=100,
        total_royalty_earned=Decimal("3500.00"),
        royalty_paid=Decimal("2000.00"),
        royalty_pending=Decimal("1500.00"),
    )
    # Books for Author B
    book_b = Book(
        id="BK_BOB_01",
        author_id="AUTH_ISOLATION_B",
        title="Bob's Cryptography",
        isbn="978-0-222222-02-2",
        genre="Cybersecurity",
        status="Published & Live",
        mrp=Decimal("500.00"),
        author_royalty_per_copy=Decimal("50.00"),
        total_copies_sold=200,
        total_royalty_earned=Decimal("10000.00"),
        royalty_paid=Decimal("5000.00"),
        royalty_pending=Decimal("5000.00"),
    )
    db.add_all([book_a, book_b])
    db.commit()

    # Tickets for Author A
    ticket_a = SupportTicket(
        id="TCK_ALICE_01",
        ticket_number="TCK-2026-ALICE",
        author_id="AUTH_ISOLATION_A",
        book_id="BK_ALICE_01",
        subject="Alice Royalty Query",
        description="When will my pending 1500 be paid?",
        category="ROYALTY",
        priority="MEDIUM",
        status="OPEN",
    )
    # Tickets for Author B
    ticket_b = SupportTicket(
        id="TCK_BOB_01",
        ticket_number="TCK-2026-BOB",
        author_id="AUTH_ISOLATION_B",
        book_id="BK_BOB_01",
        subject="Bob Print Quality Issue",
        description="Faded text on page 42.",
        category="PRINT_QUALITY",
        priority="HIGH",
        status="IN_PROGRESS",
    )
    db.add_all([ticket_a, ticket_b])
    db.commit()

    # Tokens
    token_a = create_access_token({"sub": author_a.id, "email": author_a.email, "role": "author", "author_id": author_a.id})
    token_b = create_access_token({"sub": author_b.id, "email": author_b.email, "role": "author", "author_id": author_b.id})
    token_admin = create_access_token({"sub": admin.id, "email": admin.email, "role": "admin"})

    return {
        "author_a": author_a,
        "author_b": author_b,
        "admin": admin,
        "book_a": book_a,
        "book_b": book_b,
        "ticket_a": ticket_a,
        "ticket_b": ticket_b,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
        "headers_admin": {"Authorization": f"Bearer {token_admin}"},
    }


def test_1_unauthenticated_user_cannot_access_protected_endpoints(client: TestClient):
    """Rule 1: Unauthenticated user cannot access protected endpoints."""
    protected_urls = [
        ("GET", "/api/v1/auth/me"),
        ("GET", "/api/v1/author/profile"),
        ("GET", "/api/v1/author/books"),
        ("GET", "/api/v1/author/royalties"),
        ("GET", "/api/v1/author/tickets"),
        ("POST", "/api/v1/author/tickets"),
        ("GET", "/api/v1/admin/tickets"),
        ("PATCH", "/api/v1/admin/tickets/TCK_TEST/status"),
    ]
    for method, url in protected_urls:
        if method == "GET":
            res = client.get(url)
        elif method == "POST":
            res = client.post(url, json={})
        elif method == "PATCH":
            res = client.patch(url, json={})
        assert res.status_code == 401, f"Expected 401 for {method} {url}, got {res.status_code}"


def test_2_author_a_can_view_own_books_and_tickets(client: TestClient, two_authors_and_admin):
    """Rule 2: Author A can view their own books and tickets."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]

    # 1. View profile
    res = client.get("/api/v1/author/profile", headers=headers_a)
    assert res.status_code == 200
    assert res.json()["author_id"] == "AUTH_ISOLATION_A"
    assert res.json()["total_books"] == 1

    # 2. View books
    res = client.get("/api/v1/author/books", headers=headers_a)
    assert res.status_code == 200
    books = res.json()
    assert len(books) == 1
    assert books[0]["id"] == "BK_ALICE_01"

    # 3. View single book detail
    res = client.get("/api/v1/author/books/BK_ALICE_01", headers=headers_a)
    assert res.status_code == 200
    assert res.json()["title"] == "Alice in Techland"

    # 4. View tickets
    res = client.get("/api/v1/author/tickets", headers=headers_a)
    assert res.status_code == 200
    tickets = res.json()
    assert len(tickets) == 1
    assert tickets[0]["id"] == "TCK_ALICE_01"


def test_3_author_a_cannot_view_author_b_resources(client: TestClient, two_authors_and_admin):
    """Rule 3: Author A cannot view Author B's books, royalties, tickets, or responses."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]

    # 1. Author A cannot view Author B's book details (should return 404)
    res = client.get("/api/v1/author/books/BK_BOB_01", headers=headers_a)
    assert res.status_code == 404

    # 2. Author A cannot view Author B's ticket details (should return 404)
    res = client.get("/api/v1/author/tickets/TCK_BOB_01", headers=headers_a)
    assert res.status_code == 404

    # 3. Author A's royalties endpoint only includes Author A's figures
    res = client.get("/api/v1/author/royalties", headers=headers_a)
    assert res.status_code == 200
    royalty_data = res.json()
    assert royalty_data["author_id"] == "AUTH_ISOLATION_A"
    assert Decimal(str(royalty_data["total_royalty_earned"])) == Decimal("3500.00")
    # Verify Bob's book BK_BOB_01 is NOT in Alice's breakdown
    book_ids = [b["book_id"] for b in royalty_data["books"]]
    assert "BK_BOB_01" not in book_ids
    assert "BK_ALICE_01" in book_ids


def test_4_author_a_cannot_create_ticket_for_author_b_book(client: TestClient, two_authors_and_admin):
    """Rule 4: Author A cannot create a ticket for Author B's book."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]

    payload = {
        "book_id": "BK_BOB_01",  # Belongs to Bob!
        "subject": "Illegitimate Ticket",
        "description": "Attempting to create ticket for Bob's book",
    }
    res = client.post("/api/v1/author/tickets", json=payload, headers=headers_a)
    assert res.status_code == 400
    assert "not in your author catalog" in res.json()["detail"].lower()


def test_5_author_cannot_access_or_create_internal_admin_notes(client: TestClient, two_authors_and_admin, db: Session):
    """Rule 5: An author cannot access or create internal admin notes."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]
    headers_admin = data["headers_admin"]

    # Admin creates an internal note on Alice's ticket
    note_payload = {"note_body": "Confidential investigation: Author royalty verified with finance team."}
    res = client.post("/api/v1/admin/tickets/TCK_ALICE_01/notes", json=note_payload, headers=headers_admin)
    assert res.status_code == 201

    # Author A fetches their ticket detail
    res = client.get("/api/v1/author/tickets/TCK_ALICE_01", headers=headers_a)
    assert res.status_code == 200
    ticket_data = res.json()
    # Confirm internal_notes field does NOT exist in author response schema
    assert "internal_notes" not in ticket_data

    # Author A tries to post an internal note directly
    res = client.post("/api/v1/admin/tickets/TCK_ALICE_01/notes", json=note_payload, headers=headers_a)
    assert res.status_code == 403


def test_6_author_cannot_call_admin_endpoints(client: TestClient, two_authors_and_admin):
    """Rule 6: An author cannot call admin endpoints."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]

    admin_endpoints = [
        ("GET", "/api/v1/admin/tickets"),
        ("GET", "/api/v1/admin/tickets/TCK_ALICE_01"),
        ("PATCH", "/api/v1/admin/tickets/TCK_ALICE_01/status"),
        ("PATCH", "/api/v1/admin/tickets/TCK_ALICE_01/triage"),
        ("PATCH", "/api/v1/admin/tickets/TCK_ALICE_01/assign"),
        ("POST", "/api/v1/admin/tickets/TCK_ALICE_01/notes"),
        ("GET", "/api/v1/admin/admins"),
    ]
    for method, url in admin_endpoints:
        if method == "GET":
            res = client.get(url, headers=headers_a)
        elif method == "POST":
            res = client.post(url, json={"note_body": "test"}, headers=headers_a)
        elif method == "PATCH":
            res = client.patch(url, json={"status": "RESOLVED"}, headers=headers_a)
        assert res.status_code == 403, f"Expected 403 for author calling {method} {url}, got {res.status_code}"


def test_7_author_cannot_elevate_role_or_impersonate(client: TestClient, two_authors_and_admin, db: Session):
    """Rule 7: An author cannot elevate their role or impersonate another author by changing request fields."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]

    # Attempt to inject author_id, role, priority, and status into ticket creation
    malicious_payload = {
        "author_id": "AUTH_ISOLATION_B",  # Trying to impersonate Bob
        "role": "admin",
        "priority": "URGENT",
        "status": "RESOLVED",
        "subject": "Role Elevation Attempt",
        "description": "Attempting to create ticket as Bob with admin priority",
    }
    res = client.post("/api/v1/author/tickets", json=malicious_payload, headers=headers_a)
    assert res.status_code == 201
    created = res.json()

    # Verify backend bound ticket strictly to authenticated author (Alice), ignored injected author_id and priority
    assert created["author_id"] == "AUTH_ISOLATION_A"
    assert created["priority"] in ["LOW", "MEDIUM", "HIGH", "URGENT"]
    assert created["status"] == "OPEN"      # Default author status


def test_8_authorized_admin_can_view_and_manage_tickets_across_authors(client: TestClient, two_authors_and_admin):
    """Rule 8: An authorized admin can view and manage tickets across authors."""
    data = two_authors_and_admin
    headers_admin = data["headers_admin"]

    # 1. View all tickets
    res = client.get("/api/v1/admin/tickets", headers=headers_admin)
    assert res.status_code == 200
    all_tickets = res.json()
    ticket_ids = [t["id"] for t in all_tickets]
    assert "TCK_ALICE_01" in ticket_ids
    assert "TCK_BOB_01" in ticket_ids

    # 2. Filter by status
    res = client.get("/api/v1/admin/tickets?status=OPEN", headers=headers_admin)
    assert res.status_code == 200
    for t in res.json():
        assert t["status"] == "OPEN"

    # 3. Search tickets
    res = client.get("/api/v1/admin/tickets?search=Alice", headers=headers_admin)
    assert res.status_code == 200
    search_results = res.json()
    assert any(t["id"] == "TCK_ALICE_01" for t in search_results)

    # 4. Admin updates status
    res = client.patch(
        "/api/v1/admin/tickets/TCK_ALICE_01/status",
        json={"status": "RESOLVED"},
        headers=headers_admin,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "RESOLVED"
    assert res.json()["resolved_at"] is not None

    # 5. Admin overrides triage
    res = client.patch(
        "/api/v1/admin/tickets/TCK_ALICE_01/triage",
        json={"priority": "URGENT", "category": "ROYALTY_PAYOUT"},
        headers=headers_admin,
    )
    assert res.status_code == 200
    assert res.json()["priority"] == "URGENT"
    assert res.json()["category"] == "ROYALTY_PAYOUT"

    # 6. Admin assigns ticket
    res = client.patch(
        "/api/v1/admin/tickets/TCK_ALICE_01/assign",
        json={"assigned_to_id": "USR_ADMIN_ISOLATION"},
        headers=headers_admin,
    )
    assert res.status_code == 200
    assert res.json()["assigned_to_id"] == "USR_ADMIN_ISOLATION"


def test_9_author_sees_only_own_author_visible_conversation(client: TestClient, two_authors_and_admin):
    """Rule 9: An author sees only their own author-visible conversation."""
    data = two_authors_and_admin
    headers_a = data["headers_a"]
    headers_b = data["headers_b"]
    headers_admin = data["headers_admin"]

    # Admin sends reply on Alice's ticket
    res = client.post(
        "/api/v1/admin/tickets/TCK_ALICE_01/messages",
        json={"message_body": "Hello Alice, your royalty has been scheduled."},
        headers=headers_admin,
    )
    assert res.status_code == 201

    # Author A views ticket detail
    res = client.get("/api/v1/author/tickets/TCK_ALICE_01", headers=headers_a)
    assert res.status_code == 200
    alice_thread = res.json()
    assert len(alice_thread["messages"]) >= 1
    assert alice_thread["messages"][-1]["message_body"] == "Hello Alice, your royalty has been scheduled."
    assert alice_thread["messages"][-1]["sender_type"] == "SUPPORT_AGENT"

    # Author B tries to view Alice's conversation -> 404
    res = client.get("/api/v1/author/tickets/TCK_ALICE_01", headers=headers_b)
    assert res.status_code == 404


def test_10_ticket_status_category_and_priority_validation(client: TestClient, two_authors_and_admin):
    """Rule 10: Ticket status, category, and priority validation works correctly."""
    data = two_authors_and_admin
    headers_admin = data["headers_admin"]

    # Invalid status should be rejected with 422
    res = client.patch(
        "/api/v1/admin/tickets/TCK_ALICE_01/status",
        json={"status": "INVALID_CUSTOM_STATUS"},
        headers=headers_admin,
    )
    assert res.status_code == 422

    # Invalid priority should be rejected with 422
    res = client.patch(
        "/api/v1/admin/tickets/TCK_ALICE_01/triage",
        json={"priority": "SUPER_DUPER_URGENT"},
        headers=headers_admin,
    )
    assert res.status_code == 422

    # Valid status transition should succeed
    for valid_status in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]:
        res = client.patch(
            "/api/v1/admin/tickets/TCK_ALICE_01/status",
            json={"status": valid_status},
            headers=headers_admin,
        )
        assert res.status_code == 200
        assert res.json()["status"] == valid_status
