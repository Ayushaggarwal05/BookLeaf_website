from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.ticket_service import TicketService
from backend.app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketDetailResponse,
)
from backend.app.schemas.ticket_message import TicketMessageCreate, TicketMessageResponse
from backend.app.schemas.internal_note import (
    TicketInternalNoteCreate,
    TicketInternalNoteResponse,
)

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, summary="Create Ticket")
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket associated with an author and optional book."""
    service = TicketService(db)
    try:
        return service.create_ticket(ticket_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/{ticket_id}", response_model=TicketDetailResponse, summary="Get Ticket Details")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve full ticket thread with author-visible messages and private internal notes."""
    service = TicketService(db)
    ticket = service.get_ticket_detail(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' was not found.",
        )
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse, summary="Update Ticket")
def update_ticket(ticket_id: str, ticket_in: TicketUpdate, db: Session = Depends(get_db)):
    """Update ticket attributes such as status, priority, or assignment."""
    service = TicketService(db)
    updated = service.update_ticket(ticket_id, ticket_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' was not found.",
        )
    return updated


@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse, status_code=status.HTTP_201_CREATED, summary="Add Message")
def add_message(ticket_id: str, msg_in: TicketMessageCreate, db: Session = Depends(get_db)):
    """Post an author-visible message to the ticket conversation."""
    service = TicketService(db)
    try:
        return service.add_message(ticket_id, msg_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/{ticket_id}/notes", response_model=TicketInternalNoteResponse, status_code=status.HTTP_201_CREATED, summary="Add Internal Note")
def add_internal_note(ticket_id: str, note_in: TicketInternalNoteCreate, db: Session = Depends(get_db)):
    """Add a private staff-only internal note to the ticket."""
    service = TicketService(db)
    try:
        return service.add_internal_note(ticket_id, note_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
