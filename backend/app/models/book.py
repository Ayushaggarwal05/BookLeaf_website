from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from sqlalchemy import String, Date, DateTime, Integer, Numeric, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class Book(Base):
    """
    Book entity preserving all publishing, production, distribution,
    and financial royalty metrics from the BookLeaf dataset.
    
    Royalty Calculation Documentation:
    ----------------------------------
    - total_royalty_earned = total_copies_sold * author_royalty_per_copy
      (Reflects cumulative earned royalties across all sales channels)
    - royalty_pending = total_royalty_earned - royalty_paid
      (Reflects balance awaiting scheduled payout to the author)
    Both fields are stored as Decimal (Numeric 12,2) for exact financial accounting.
    """
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Matches stable book_id (e.g. BK001)
    author_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("authors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. "Published & Live"

    # Monetary & Commercial Metrics (Stored as Numeric/Decimal to avoid float inaccuracy)
    mrp: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    author_royalty_per_copy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    total_copies_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_royalty_earned: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    royalty_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    royalty_pending: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    last_royalty_payout_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Production & Distribution Channels
    print_partner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    available_on: Mapped[List[Any]] = mapped_column(JSON, nullable=False, default=list)

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
    author: Mapped["Author"] = relationship("Author", back_populates="books")
    tickets: Mapped[List["SupportTicket"]] = relationship(
        "SupportTicket",
        back_populates="book",
    )

    @property
    def book_id(self) -> str:
        """Alias for compatibility with dataset field naming."""
        return self.id

    def calculate_expected_royalty(self) -> Decimal:
        """Calculate expected total royalty earned from sales count and royalty rate."""
        if self.author_royalty_per_copy is not None:
            return Decimal(self.total_copies_sold) * Decimal(self.author_royalty_per_copy)
        return Decimal("0.00")

    def calculate_expected_pending(self) -> Decimal:
        """Calculate expected outstanding royalty balance."""
        return self.total_royalty_earned - self.royalty_paid

    def __repr__(self) -> str:
        return f"<Book id={self.id} title='{self.title}' isbn='{self.isbn}' author_id={self.author_id}>"
