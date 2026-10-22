import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class User(Base):
    """System user representing internal staff, admins, or support agents."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"USR_{uuid.uuid4().hex[:10].upper()}",
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="SUPPORT_AGENT")
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    assigned_tickets = relationship(
        "SupportTicket",
        back_populates="assigned_to",
        foreign_keys="SupportTicket.assigned_to_id",
    )
    internal_notes = relationship(
        "TicketInternalNote",
        back_populates="staff_user",
        foreign_keys="TicketInternalNote.author_user_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
