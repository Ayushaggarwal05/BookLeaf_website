import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class SupportTicket(Base):
    """
    Support ticket created by or on behalf of an author.
    Includes rich metadata, optional book association, status lifecycle,
    and AI-assisted triage metadata.
    """
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"TCK_{uuid.uuid4().hex[:10].upper()}",
    )
    ticket_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    author_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("authors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    book_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("books.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Ticket Content
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        default="GENERAL_INQUIRY",
    )  # e.g., ROYALTY, PRINT_QUALITY, DISTRIBUTION, COVER_DESIGN, EDITING, GENERAL_INQUIRY
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="MEDIUM",
        index=True,
    )  # LOW, MEDIUM, HIGH, URGENT
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OPEN",
        index=True,
    )  # OPEN, IN_PROGRESS, WAITING_ON_AUTHOR, RESOLVED, CLOSED

    # Assignment & Lifecycle
    assigned_to_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Attachments Metadata
    attachments: Mapped[List[Any]] = mapped_column(JSON, default=list, server_default="[]", nullable=False)

    # AI Classification Metadata
    ai_classification: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )  # e.g., {"suggested_category": "ROYALTY", "confidence": 0.94, "urgency": "HIGH", "sentiment": "URGENT"}

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    author: Mapped["Author"] = relationship("Author", back_populates="tickets")
    book: Mapped[Optional["Book"]] = relationship("Book", back_populates="tickets")
    assigned_to: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_tickets",
        foreign_keys=[assigned_to_id],
    )
    messages: Mapped[List["TicketMessage"]] = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.created_at",
    )
    internal_notes: Mapped[List["TicketInternalNote"]] = relationship(
        "TicketInternalNote",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketInternalNote.created_at",
    )

    def __repr__(self) -> str:
        return f"<SupportTicket id={self.id} number={self.ticket_number} status={self.status}>"
