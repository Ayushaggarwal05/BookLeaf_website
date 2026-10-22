from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Date, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class Author(Base):
    """Author entity representing registered authors in the BookLeaf portal."""
    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Matches stable author_id (e.g. AUTH001)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    joined_date: Mapped[date] = mapped_column(Date, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=func.true(), nullable=False)

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
    books: Mapped[List["Book"]] = relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Book.title",
    )
    tickets: Mapped[List["SupportTicket"]] = relationship(
        "SupportTicket",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def author_id(self) -> str:
        """Alias for compatibility with dataset field naming."""
        return self.id

    def __repr__(self) -> str:
        return f"<Author id={self.id} name='{self.name}' email='{self.email}'>"
