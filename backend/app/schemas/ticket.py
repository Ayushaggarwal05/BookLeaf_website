from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.ticket_message import TicketMessageResponse
from backend.app.schemas.internal_note import TicketInternalNoteResponse


class TicketBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: str = Field("GENERAL_INQUIRY", max_length=100)
    priority: str = Field("MEDIUM", max_length=50)
    status: str = Field("OPEN", max_length=50)
    book_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    ai_classification: Optional[Dict[str, Any]] = None


class TicketCreate(TicketBase):
    author_id: str
    ticket_number: Optional[str] = None


class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    book_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    ai_classification: Optional[Dict[str, Any]] = None
    resolved_at: Optional[datetime] = None


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_number: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class TicketDetailResponse(TicketResponse):
    messages: List[TicketMessageResponse] = []
    internal_notes: List[TicketInternalNoteResponse] = []
