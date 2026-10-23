from datetime import datetime, timezone, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, or_, and_

from backend.app.core.database import get_db
from backend.app.core.dependencies import AuthenticatedUser, require_admin
from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote
from backend.app.models.user import User
from backend.app.models.author import Author
from backend.app.schemas.ticket_message import TicketMessageResponse
from backend.app.schemas.internal_note import TicketInternalNoteResponse
from backend.app.schemas.portal import (
    AdminTicketResponse,
    AdminTicketDetailResponse,
    AdminStatusUpdate,
    AdminTriageUpdate,
    AdminAssignUpdate,
    AdminInternalNoteCreate,
    AdminMessageCreate,
    AdminUserSummary,
    AiDraftResponse,
    AiTriageResponse,
)
from backend.app.services.ai_service import ai_service

router = APIRouter(prefix="/admin", tags=["Admin Portal (Cross-Author Operations)"])


@router.get("/tickets", response_model=List[AdminTicketResponse], summary="List All Tickets with Filters & Search")
def list_all_tickets_admin(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH, URGENT)"),
    assigned_to_id: Optional[str] = Query(None, description="Filter by assigned admin ID"),
    date_from: Optional[date] = Query(None, description="Filter by created date from (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter by created date to (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by subject, description, ticket number, or author name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Administrative queue listing tickets across all authors.
    Supports multi-attribute filtering, search, and pagination.
    """
    stmt = (
        select(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.book),
            joinedload(SupportTicket.assigned_to),
        )
    )

    conditions = []

    if status_filter:
        statuses = [s.strip().upper() for s in status_filter.split(",") if s.strip()]
        if len(statuses) == 1:
            conditions.append(SupportTicket.status == statuses[0])
        elif len(statuses) > 1:
            conditions.append(SupportTicket.status.in_(statuses))

    if category:
        conditions.append(SupportTicket.category == category)


    if priority:
        conditions.append(SupportTicket.priority == priority.upper())

    if assigned_to_id:
        conditions.append(SupportTicket.assigned_to_id == assigned_to_id)

    if date_from:
        conditions.append(SupportTicket.created_at >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        conditions.append(SupportTicket.created_at <= datetime.combine(date_to, datetime.max.time()))

    if search and search.strip():
        term = f"%{search.strip()}%"
        conditions.append(
            or_(
                SupportTicket.ticket_number.ilike(term),
                SupportTicket.subject.ilike(term),
                SupportTicket.description.ilike(term),
                SupportTicket.author.has(Author.name.ilike(term)),
                SupportTicket.author.has(Author.email.ilike(term)),
            )
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
    tickets = db.scalars(stmt).unique().all()
    return tickets


@router.get("/tickets/{ticket_id}", response_model=AdminTicketDetailResponse, summary="Get Full Administrative Ticket Details")
def get_ticket_detail_admin(
    ticket_id: str,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Retrieve full ticket lifecycle details, author profile, public message thread,
    and confidential internal notes.
    """
    stmt = (
        select(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.book),
            joinedload(SupportTicket.assigned_to),
            selectinload(SupportTicket.messages),
            selectinload(SupportTicket.internal_notes),
        )
        .where(SupportTicket.id == ticket_id)
    )
    ticket = db.scalars(stmt).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' was not found.",
        )
    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=AdminTicketResponse, summary="Update Ticket Status")
def update_ticket_status(
    ticket_id: str,
    status_update: AdminStatusUpdate,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Admin-only status transition (OPEN, IN_PROGRESS, RESOLVED, CLOSED).
    Updates resolved_at timestamp when resolved.
    """
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    new_status = status_update.status.upper()
    ticket.status = new_status
    if new_status in ("RESOLVED", "CLOSED") and not ticket.resolved_at:
        ticket.resolved_at = datetime.now(timezone.utc)
    elif new_status in ("OPEN", "IN_PROGRESS", "WAITING_ON_AUTHOR"):
        ticket.resolved_at = None

    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/tickets/{ticket_id}/triage", response_model=AdminTicketResponse, summary="Override Category & Priority")
def triage_ticket(
    ticket_id: str,
    triage_in: AdminTriageUpdate,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin override for AI classification, priority, and category."""
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    if triage_in.category:
        ticket.category = triage_in.category
    if triage_in.priority:
        ticket.priority = triage_in.priority.upper()

    ai_meta = dict(ticket.ai_classification or {})
    ai_meta["admin_override"] = True
    ai_meta["admin_overridden_at"] = datetime.now(timezone.utc).isoformat()
    if triage_in.ai_classification is not None:
        ai_meta.update(triage_in.ai_classification)
    ticket.ai_classification = ai_meta

    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/tickets/{ticket_id}/assign", response_model=AdminTicketResponse, summary="Assign Ticket to Staff")
def assign_ticket(
    ticket_id: str,
    assign_in: AdminAssignUpdate,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Assign ticket to an admin or unassign."""
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    if assign_in.assigned_to_id:
        assignee = db.get(User, assign_in.assigned_to_id)
        if not assignee or not assignee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Staff user '{assign_in.assigned_to_id}' not found or inactive.",
            )
        ticket.assigned_to_id = assignee.id
    else:
        ticket.assigned_to_id = None

    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/tickets/{ticket_id}/notes", response_model=TicketInternalNoteResponse, status_code=status.HTTP_201_CREATED, summary="Add Private Internal Note")
def add_internal_note(
    ticket_id: str,
    note_in: AdminInternalNoteCreate,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Add a private internal note to a ticket thread.
    Exclusively visible to administrators; authors cannot view internal notes.
    """
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    note = TicketInternalNote(
        ticket_id=ticket.id,
        author_user_id=current_admin.id,
        note_body=note_in.note_body.strip(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse, status_code=status.HTTP_201_CREATED, summary="Send Author-Visible Reply")
def post_admin_message(
    ticket_id: str,
    msg_in: AdminMessageCreate,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Admin sends a message visible to the author on the public ticket thread.
    Automatically sets ticket status to WAITING_ON_AUTHOR if currently OPEN or IN_PROGRESS.
    """
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_type="SUPPORT_AGENT",
        sender_id=current_admin.id,
        sender_name=current_admin.full_name,
        message_body=msg_in.message_body.strip(),
        attachments=msg_in.attachments or [],
    )
    db.add(msg)

    # Set ticket to WAITING_ON_AUTHOR if in progress
    if ticket.status in ("OPEN", "IN_PROGRESS"):
        ticket.status = "WAITING_ON_AUTHOR"

    db.commit()
    db.refresh(msg)
    return msg


@router.get("/admins", response_model=List[AdminUserSummary], summary="List Administrative Users")
def list_admin_users(
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List administrative users available for assignment."""
    users = db.scalars(
        select(User)
        .where(User.is_active == True)
        .order_by(User.full_name)
    ).all()
    return users


@router.post("/tickets/{ticket_id}/ai-draft", response_model=AiDraftResponse, summary="Generate AI Response Draft using Knowledge Base")
def generate_ticket_ai_draft(
    ticket_id: str,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    On-demand AI author response draft generation.
    - Grounded strictly in official BookLeaf Knowledge Base policies.
    - Incorporates verified author, book, and ticket context.
    - Caches draft on ticket metadata to control costs on repeated viewings.
    """
    stmt = (
        select(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.book),
            selectinload(SupportTicket.messages),
        )
        .where(SupportTicket.id == ticket_id)
    )
    ticket = db.scalars(stmt).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    author = ticket.author
    book = ticket.book

    messages_payload = [
        {"sender_type": m.sender_type, "message_body": m.message_body}
        for m in (ticket.messages or [])
    ]

    draft_result = ai_service.generate_draft_response(
        ticket_subject=ticket.subject,
        ticket_description=ticket.description,
        ticket_category=ticket.category,
        ticket_priority=ticket.priority,
        author_name=author.name if author else "Author",
        author_email=author.email if author else None,
        author_city=author.city if author else None,
        book_title=book.title if book else None,
        book_isbn=book.isbn if book else None,
        book_status=book.status if book else None,
        existing_messages=messages_payload,
    )

    # Cache AI draft in ai_classification on the ticket to avoid redundant billing
    if draft_result.status == "success":
        ai_meta = dict(ticket.ai_classification or {})
        ai_meta["draft_response"] = draft_result.draft_response
        ai_meta["suggested_category"] = draft_result.suggested_category
        ai_meta["suggested_priority"] = draft_result.suggested_priority
        ai_meta["priority_code"] = draft_result.priority_code
        ai_meta["confidence"] = draft_result.confidence
        ai_meta["reasoning"] = draft_result.reasoning
        ai_meta["relevant_policies"] = draft_result.relevant_policies
        ai_meta["last_draft_model"] = draft_result.model
        ai_meta["last_draft_generated_at"] = draft_result.created_at
        ticket.ai_classification = ai_meta
        db.commit()
        db.refresh(ticket)

    return AiDraftResponse(
        draft_response=draft_result.draft_response,
        suggested_category=draft_result.suggested_category,
        suggested_priority=draft_result.suggested_priority,
        priority_code=draft_result.priority_code,
        confidence=draft_result.confidence,
        reasoning=draft_result.reasoning,
        relevant_policies=draft_result.relevant_policies,
        status=draft_result.status,
        model=draft_result.model,
        error_message=draft_result.error_message,
        created_at=draft_result.created_at,
    )


@router.post("/tickets/{ticket_id}/ai-triage", response_model=AiTriageResponse, summary="Run On-Demand Gemini AI Triage Analysis")
def run_ticket_ai_triage(
    ticket_id: str,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    On-demand Gemini LLM ticket classification and priority assessment.
    - Evaluates author query against official BookLeaf operational departments.
    - Replaces initial Tier 1 keyword triage with deep Gemini 2.5 Flash reasoning.
    - Caches suggested category and priority on ticket record for administrative review.
    """
    stmt = (
        select(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.book),
            selectinload(SupportTicket.messages),
        )
        .where(SupportTicket.id == ticket_id)
    )
    ticket = db.scalars(stmt).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    author = ticket.author
    book = ticket.book

    triage_result = ai_service.triage_ticket(
        subject=ticket.subject,
        description=ticket.description,
        author_name=author.name if author else None,
        book_title=book.title if book else None,
        book_isbn=book.isbn if book else None,
    )

    # Cache Gemini AI triage in ai_classification on ticket
    ai_meta = dict(ticket.ai_classification or {})
    ai_meta["category"] = triage_result.category
    ai_meta["priority"] = triage_result.priority
    ai_meta["suggested_category"] = triage_result.category
    ai_meta["suggested_priority"] = triage_result.priority
    ai_meta["priority_code"] = triage_result.priority_code
    ai_meta["confidence"] = triage_result.confidence
    ai_meta["reasoning"] = triage_result.reasoning
    ai_meta["status"] = triage_result.status
    ai_meta["model"] = triage_result.model
    ai_meta["provider"] = triage_result.provider or triage_result.model
    ai_meta["applicable_policies"] = triage_result.applicable_policies
    ai_meta["triage_analyzed_at"] = triage_result.created_at
    ai_meta["error_message"] = triage_result.error_message
    ticket.ai_classification = ai_meta
    db.commit()
    db.refresh(ticket)

    return AiTriageResponse(
        category=triage_result.category,
        priority=triage_result.priority,
        priority_code=triage_result.priority_code,
        confidence=triage_result.confidence,
        reasoning=triage_result.reasoning,
        status=triage_result.status,
        model=triage_result.model,
        created_at=triage_result.created_at,
        applicable_policies=triage_result.applicable_policies,
        error_message=triage_result.error_message,
    )


@router.post("/tickets/{ticket_id}/apply-ai-triage", response_model=AdminTicketResponse, summary="Apply AI Suggested Triage to Ticket")
def apply_ai_triage(
    ticket_id: str,
    current_admin: AuthenticatedUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Applies the AI's suggested category and priority to the ticket record.
    """
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' was not found.")

    ai_meta = ticket.ai_classification or {}
    sug_cat = ai_meta.get("suggested_category")
    sug_pri_code = ai_meta.get("priority_code") or ai_meta.get("suggested_priority")

    if sug_cat:
        ticket.category = sug_cat
    if sug_pri_code:
        from backend.app.services.knowledge_base import PRIORITY_CODE_MAP
        ticket.priority = PRIORITY_CODE_MAP.get(sug_pri_code, sug_pri_code).upper()

    ai_meta = dict(ai_meta)
    ai_meta["applied_by_admin"] = current_admin.full_name
    ai_meta["applied_at"] = datetime.now(timezone.utc).isoformat()
    ticket.ai_classification = ai_meta

    db.commit()
    db.refresh(ticket)
    return ticket
