import uuid
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class TicketMessage(Base):
    """
    Author-visible communication message on a support ticket thread.
    Can be authored by the author, a support representative, or an automated system bot.
    """
    __tablename__ = "ticket_messages"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"MSG_{uuid.uuid4().hex[:10].upper()}",
    )
    ticket_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # "AUTHOR", "SUPPORT_AGENT", "SYSTEM"
    sender_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )  # References author_id or user_id
    sender_name: Mapped[str] = mapped_column(String(255), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[List[Any]] = mapped_column(JSON, nullable=False, default=list)

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

    # Relationship
    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="messages")

    def __repr__(self) -> str:
        return f"<TicketMessage id={self.id} ticket_id={self.ticket_id} sender_type={self.sender_type}>"
