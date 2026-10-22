import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class TicketInternalNote(Base):
    """
    Private staff-only internal notes on a support ticket.
    Strictly segregated from author-visible messages.
    """
    __tablename__ = "ticket_internal_notes"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"NOTE_{uuid.uuid4().hex[:10].upper()}",
    )
    ticket_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    note_body: Mapped[str] = mapped_column(Text, nullable=False)

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

    # Relationships
    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="internal_notes")
    staff_user: Mapped["User"] = relationship("User", back_populates="internal_notes")

    def __repr__(self) -> str:
        return f"<TicketInternalNote id={self.id} ticket_id={self.ticket_id} author_user_id={self.author_user_id}>"
