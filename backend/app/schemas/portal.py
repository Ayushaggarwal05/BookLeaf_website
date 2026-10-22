from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.book import BookResponse
from backend.app.schemas.ticket_message import TicketMessageResponse
from backend.app.schemas.internal_note import TicketInternalNoteResponse


# -----------------------------------------------------------------------------
# Author Portal Schemas
# -----------------------------------------------------------------------------

class AuthorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    author_id: str
    name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    joined_date: date
    total_books: int = 0
    total_copies_sold: int = 0
    total_royalties_earned: Decimal = Decimal("0.00")
    total_royalties_paid: Decimal = Decimal("0.00")
    total_royalties_pending: Decimal = Decimal("0.00")


class BookRoyaltyItem(BaseModel):
    book_id: str
    title: str
    isbn: str
    genre: str
    status: str
    mrp: Optional[Decimal] = None
    royalty_per_copy: Optional[Decimal] = None
    total_copies_sold: int = 0
    total_royalty_earned: Decimal = Decimal("0.00")
    royalty_paid: Decimal = Decimal("0.00")
    royalty_pending: Decimal = Decimal("0.00")
    last_payout_date: Optional[date] = None


class AuthorRoyaltySummary(BaseModel):
    author_id: str
    total_books: int
    total_copies_sold: int
    total_royalty_earned: Decimal
    total_royalty_paid: Decimal
    total_royalty_pending: Decimal
    books: List[BookRoyaltyItem] = []


class AuthorTicketCreate(BaseModel):
    """
    Author support ticket creation payload.
    Security: Authors cannot set priority, status, assignment, or internal AI fields.
    """
    book_id: Optional[str] = Field(None, description="Optional associated book ID from author's catalog")
    subject: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    category: str = Field("GENERAL_INQUIRY", max_length=100)
    attachments: List[Any] = Field(default_factory=list, description="Attachment metadata (filename, size, url)")


class AuthorTicketResponse(BaseModel):
    """Author-facing ticket summary without confidential operational metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_number: str
    author_id: str
    book_id: Optional[str] = None
    book_title: Optional[str] = None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    attachments: List[Any] = []
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class AuthorTicketDetailResponse(AuthorTicketResponse):
    """
    Author-facing ticket details.
    Strictly excludes internal admin notes (tenant isolation).
    """
    messages: List[TicketMessageResponse] = []


class AuthorMessageCreate(BaseModel):
    """Author response message to an existing ticket."""
    message_body: str = Field(..., min_length=1, max_length=5000)
    attachments: List[Any] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Admin Portal Schemas
# -----------------------------------------------------------------------------

class AdminAuthorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None


class AdminBookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    isbn: str
    genre: str
    status: str


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    role: str


class AdminTicketResponse(BaseModel):
    """Complete administrative view of a ticket including author and book references."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_number: str
    author_id: str
    book_id: Optional[str] = None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_to_id: Optional[str] = None
    attachments: List[Any] = []
    ai_classification: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    author: Optional[AdminAuthorSummary] = None
    book: Optional[AdminBookSummary] = None
    assigned_to: Optional[AdminUserSummary] = None


class AdminTicketDetailResponse(AdminTicketResponse):
    """Administrative ticket view with both public messages and private notes."""
    messages: List[TicketMessageResponse] = []
    internal_notes: List[TicketInternalNoteResponse] = []


class AdminStatusUpdate(BaseModel):
    """Admin-only status transition."""
    status: str = Field(..., pattern="^(OPEN|IN_PROGRESS|WAITING_ON_AUTHOR|RESOLVED|CLOSED)$")


class AdminTriageUpdate(BaseModel):
    """Admin-only override of AI classification and priority."""
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|URGENT)$")
    ai_classification: Optional[Dict[str, Any]] = None


class AdminAssignUpdate(BaseModel):
    """Admin-only ticket assignment."""
    assigned_to_id: Optional[str] = Field(None, description="Admin user ID to assign, or null to unassign")


class AdminInternalNoteCreate(BaseModel):
    """Private internal admin note."""
    note_body: str = Field(..., min_length=1, max_length=10000)


class AdminMessageCreate(BaseModel):
    """Admin reply visible to author."""
    message_body: str = Field(..., min_length=1, max_length=10000)
    attachments: List[Any] = Field(default_factory=list)


class AiDraftResponse(BaseModel):
    """AI-generated author draft response for operational review."""
    draft_response: str
    suggested_category: str
    suggested_priority: str
    priority_code: str
    confidence: float
    reasoning: str
    relevant_policies: List[str] = []
    status: str
    model: str
    error_message: Optional[str] = None
    created_at: str


class AiTriageResponse(BaseModel):
    """AI triage classification and priority scoring output."""
    category: str
    priority: str
    priority_code: str
    confidence: float
    reasoning: str
    status: str
    model: str
    created_at: str
