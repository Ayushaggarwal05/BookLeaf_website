from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    joined_date: date


class AuthorCreate(AuthorBase):
    author_id: Optional[str] = Field(
        None,
        description="Optional custom or stable identifier (e.g. AUTH001)",
    )


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    joined_date: Optional[date] = None


class AuthorResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def author_id(self) -> str:
        return self.id


from backend.app.schemas.book import BookResponse  # noqa: E402


class AuthorDetailResponse(AuthorResponse):
    books: List[BookResponse] = []
