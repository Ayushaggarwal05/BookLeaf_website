from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.dependencies import AuthenticatedUser, require_author
from backend.app.models.author import Author
from backend.app.models.book import Book
from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.schemas.book import BookResponse
from backend.app.schemas.ticket_message import TicketMessageResponse
from backend.app.schemas.portal import (
    AuthorProfileResponse,
    AuthorRoyaltySummary,
    BookRoyaltyItem,
    AuthorTicketCreate,
    AuthorTicketResponse,
    AuthorTicketDetailResponse,
    AuthorMessageCreate,
)
from backend.app.services.ticket_service import TicketService
from backend.app.services.ai_service import ai_service

router = APIRouter(prefix="/author", tags=["Author Portal (Tenant-Isolated)"])


@router.get("/profile", response_model=AuthorProfileResponse, summary="Get Authenticated Author Profile")
def get_author_profile(
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Retrieve current author profile and aggregated book sales/royalty metrics.
    Strictly scoped to the authenticated author.
    """
    author = db.get(Author, current_author.author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found.")

    books = db.scalars(select(Book).where(Book.author_id == author.id)).all()
    total_copies = sum(b.total_copies_sold for b in books)
    total_earned = sum(b.total_royalty_earned for b in books)
    total_paid = sum(b.royalty_paid for b in books)
    total_pending = sum(b.royalty_pending for b in books)

    return AuthorProfileResponse(
        id=author.id,
        author_id=author.id,
        name=author.name,
        email=author.email,
        phone=author.phone,
        city=author.city,
        joined_date=author.joined_date,
        total_books=len(books),
        total_copies_sold=total_copies,
        total_royalties_earned=Decimal(str(total_earned)),
        total_royalties_paid=Decimal(str(total_paid)),
        total_royalties_pending=Decimal(str(total_pending)),
    )


@router.get("/books", response_model=List[BookResponse], summary="List Author's Books")
def get_author_books(
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    List all books belonging exclusively to the authenticated author.
    Authors cannot view other authors' books via this endpoint.
    """
    books = db.scalars(
        select(Book)
        .where(Book.author_id == current_author.author_id)
        .order_by(Book.title)
    ).all()
    return books


@router.get("/books/{book_id}", response_model=BookResponse, summary="Get Single Book Details")
def get_author_book(
    book_id: str,
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Retrieve specific book details.
    Enforces tenant ownership: Returns 404 if the book does not belong to the author.
    """
    book = db.scalars(
        select(Book).where(
            Book.id == book_id,
            Book.author_id == current_author.author_id,
        )
    ).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book '{book_id}' was not found in your catalog.",
        )
    return book


@router.get("/royalties", response_model=AuthorRoyaltySummary, summary="Get Author Royalties Breakdown")
def get_author_royalties(
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Retrieve author royalty summary across all books in their catalog,
    including cumulative earned, paid, and outstanding balances.
    """
    books = db.scalars(
        select(Book)
        .where(Book.author_id == current_author.author_id)
        .order_by(Book.title)
    ).all()

    items: List[BookRoyaltyItem] = []
    total_copies = 0
    total_earned = Decimal("0.00")
    total_paid = Decimal("0.00")
    total_pending = Decimal("0.00")

    for b in books:
        total_copies += b.total_copies_sold
        total_earned += Decimal(str(b.total_royalty_earned))
        total_paid += Decimal(str(b.royalty_paid))
        total_pending += Decimal(str(b.royalty_pending))

        items.append(
            BookRoyaltyItem(
                book_id=b.id,
                title=b.title,
                isbn=b.isbn,
                genre=b.genre,
                status=b.status,
                mrp=b.mrp,
                royalty_per_copy=b.author_royalty_per_copy,
                total_copies_sold=b.total_copies_sold,
                total_royalty_earned=Decimal(str(b.total_royalty_earned)),
                royalty_paid=Decimal(str(b.royalty_paid)),
                royalty_pending=Decimal(str(b.royalty_pending)),
                last_payout_date=b.last_royalty_payout_date,
            )
        )

    return AuthorRoyaltySummary(
        author_id=current_author.author_id,
        total_books=len(books),
        total_copies_sold=total_copies,
        total_royalty_earned=total_earned,
        total_royalty_paid=total_paid,
        total_royalty_pending=total_pending,
        books=items,
    )


@router.post("/tickets", response_model=AuthorTicketResponse, status_code=status.HTTP_201_CREATED, summary="Create Author Support Ticket")
def create_author_ticket(
    ticket_in: AuthorTicketCreate,
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Create a new support ticket.
    - Scoped strictly to authenticated author identity.
    - Validates that associated book belongs to the author (if provided).
    - Prevents author from manipulating priority, status, or assignment.
    """
    book = None
    book_title = None
    if ticket_in.book_id:
        book = db.scalars(
            select(Book).where(
                Book.id == ticket_in.book_id,
                Book.author_id == current_author.author_id,
            )
        ).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Selected book '{ticket_in.book_id}' is not in your author catalog.",
            )
        book_title = book.title

    ticket_service = TicketService(db)
    ticket_number = ticket_service.generate_ticket_number()

    # AI Triage & Priority Scoring (Non-blocking with safe fallback)
    try:
        triage = ai_service.triage_ticket(
            subject=ticket_in.subject.strip(),
            description=ticket_in.description.strip(),
            author_name=current_author.full_name,
            book_title=book_title,
            book_isbn=book.isbn if book else None,
        )
        assigned_category = triage.category
        assigned_priority = triage.priority_code
        ai_metadata = {
            "category": triage.category,
            "priority": triage.priority,
            "suggested_category": triage.category,
            "suggested_priority": triage.priority,
            "priority_code": triage.priority_code,
            "confidence": triage.confidence,
            "reasoning": triage.reasoning,
            "applicable_policies": getattr(triage, "applicable_policies", []),
            "status": triage.status,
            "model": triage.model,
            "provider": getattr(triage, "provider", triage.model),
            "created_at": triage.created_at,
        }
    except Exception as e:
        assigned_category = ticket_in.category or "General Inquiry"
        assigned_priority = "MEDIUM"
        ai_metadata = {
            "category": assigned_category,
            "priority": "Medium",
            "suggested_category": assigned_category,
            "suggested_priority": "Medium",
            "priority_code": "MEDIUM",
            "status": "unavailable",
            "reason": str(e),
        }

    ticket = SupportTicket(
        ticket_number=ticket_number,
        author_id=current_author.author_id,
        book_id=ticket_in.book_id,
        subject=ticket_in.subject.strip(),
        description=ticket_in.description.strip(),
        category=assigned_category,
        priority=assigned_priority,
        status="OPEN",
        attachments=ticket_in.attachments or [],
        ai_classification=ai_metadata,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return AuthorTicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        author_id=ticket.author_id,
        book_id=ticket.book_id,
        book_title=book_title,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        attachments=ticket.attachments,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
    )


@router.get("/tickets", response_model=List[AuthorTicketResponse], summary="List Author's Support Tickets")
def list_author_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    List tickets submitted by the authenticated author.
    Does not expose tickets from other authors.
    """
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.author_id == current_author.author_id)
        .order_by(SupportTicket.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tickets = db.scalars(stmt).all()

    result: List[AuthorTicketResponse] = []
    for t in tickets:
        book_title = t.book.title if t.book else None
        result.append(
            AuthorTicketResponse(
                id=t.id,
                ticket_number=t.ticket_number,
                author_id=t.author_id,
                book_id=t.book_id,
                book_title=book_title,
                subject=t.subject,
                description=t.description,
                category=t.category,
                priority=t.priority,
                status=t.status,
                attachments=t.attachments or [],
                created_at=t.created_at,
                updated_at=t.updated_at,
                resolved_at=t.resolved_at,
            )
        )
    return result


@router.get("/tickets/{ticket_id}", response_model=AuthorTicketDetailResponse, summary="Get Author Ticket Details and Messages")
def get_author_ticket_detail(
    ticket_id: str,
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Retrieve ticket conversation thread.
    - Enforces tenant ownership: Returns 404 if ticket does not belong to author.
    - Strictly excludes confidential internal admin notes.
    """
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket_detail(ticket_id)

    if not ticket or ticket.author_id != current_author.author_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' was not found.",
        )

    book_title = ticket.book.title if ticket.book else None

    # Transform messages safely
    messages = [
        TicketMessageResponse.model_validate(msg)
        for msg in ticket.messages
    ]

    return AuthorTicketDetailResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        author_id=ticket.author_id,
        book_id=ticket.book_id,
        book_title=book_title,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        attachments=ticket.attachments or [],
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        messages=messages,
    )


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse, status_code=status.HTTP_201_CREATED, summary="Reply to Ticket Conversation")
def post_author_message(
    ticket_id: str,
    message_in: AuthorMessageCreate,
    current_author: AuthenticatedUser = Depends(require_author),
    db: Session = Depends(get_db),
):
    """
    Author replies to an existing ticket conversation.
    - Enforces ownership: Returns 404 if ticket belongs to another author.
    - Automatically sets sender to AUTHOR with verified author credentials.
    """
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket or ticket.author_id != current_author.author_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' was not found.",
        )

    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_type="AUTHOR",
        sender_id=current_author.author_id,
        sender_name=current_author.full_name,
        message_body=message_in.message_body.strip(),
        attachments=message_in.attachments or [],
    )
    db.add(msg)

    # If ticket was waiting on author, transition to IN_PROGRESS
    if ticket.status == "WAITING_ON_AUTHOR":
        ticket.status = "IN_PROGRESS"

    db.commit()
    db.refresh(msg)
    return TicketMessageResponse.model_validate(msg)
