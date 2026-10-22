from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TicketInternalNoteBase(BaseModel):
    author_user_id: str
    note_body: str = Field(..., min_length=1)


class TicketInternalNoteCreate(TicketInternalNoteBase):
    pass


class TicketInternalNoteResponse(TicketInternalNoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    created_at: datetime
    updated_at: datetime
