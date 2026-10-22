from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, computed_field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=1, max_length=50)
    genre: str = Field(..., min_length=1, max_length=100)
    publication_date: Optional[date] = None
    status: str = Field("Published & Live", max_length=100)
    mrp: Optional[Decimal] = None
    author_royalty_per_copy: Optional[Decimal] = None
    total_copies_sold: int = Field(0, ge=0)
    total_royalty_earned: Decimal = Field(default=Decimal("0.00"), ge=0)
    royalty_paid: Decimal = Field(default=Decimal("0.00"), ge=0)
    royalty_pending: Decimal = Field(default=Decimal("0.00"))
    last_royalty_payout_date: Optional[date] = None
    print_partner: Optional[str] = None
    available_on: List[str] = Field(default_factory=list)


class BookCreate(BookBase):
    book_id: Optional[str] = Field(
        None,
        description="Optional custom or stable identifier (e.g. BK001)",
    )
    author_id: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    publication_date: Optional[date] = None
    status: Optional[str] = None
    mrp: Optional[Decimal] = None
    author_royalty_per_copy: Optional[Decimal] = None
    total_copies_sold: Optional[int] = None
    total_royalty_earned: Optional[Decimal] = None
    royalty_paid: Optional[Decimal] = None
    royalty_pending: Optional[Decimal] = None
    last_royalty_payout_date: Optional[date] = None
    print_partner: Optional[str] = None
    available_on: Optional[List[str]] = None


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    author_id: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def book_id(self) -> str:
        return self.id
