from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


class TicketMessageBase(BaseModel):
    sender_type: str = Field(
        ...,
        description="One of 'AUTHOR', 'SUPPORT_AGENT', 'SYSTEM'",
    )
    sender_id: Optional[str] = None
    sender_name: str = Field(..., min_length=1, max_length=255)
    message_body: str = Field(..., min_length=1)
    attachments: List[Any] = Field(default_factory=list)


class TicketMessageCreate(TicketMessageBase):
    pass


class TicketMessageResponse(TicketMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    created_at: datetime
    updated_at: datetime
