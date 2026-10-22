from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials required to authenticate."""
    email: EmailStr = Field(..., description="User or author registered email address")
    password: str = Field(..., min_length=1, description="Account password")


class TokenResponse(BaseModel):
    """Bearer access token with user identification and authorized role."""
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    email: str
    name: str
    author_id: Optional[str] = None


class CurrentUserResponse(BaseModel):
    """Authenticated principal profile."""
    id: str
    email: str
    full_name: str
    role: str
    author_id: Optional[str] = None
