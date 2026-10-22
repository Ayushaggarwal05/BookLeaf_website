import logging
from dataclasses import dataclass
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.author import Author
from backend.app.models.user import User

logger = logging.getLogger(__name__)

security_bearer = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Unified security principal representing an authenticated author or admin."""
    id: str
    email: str
    full_name: str
    role: str  # "author" or "admin"
    author: Optional[Author] = None
    admin_user: Optional[User] = None

    @property
    def is_author(self) -> bool:
        return self.role == "author"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def author_id(self) -> Optional[str]:
        return self.author.id if self.author else None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """
    Extract and validate JWT Bearer token and fetch authenticating database record.
    Rejects forged roles and frontend-supplied IDs.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as exc:
        logger.warning(f"JWT validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")
    email: Optional[str] = payload.get("email")

    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = role.lower()

    if role == "author":
        author = db.get(Author, user_id)
        if not author:
            author = db.query(Author).filter(Author.email == email).first()

        if not author:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Author account not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not getattr(author, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Author account is deactivated.",
            )
        return AuthenticatedUser(
            id=author.id,
            email=author.email,
            full_name=author.name,
            role="author",
            author=author,
        )

    elif role in ("admin", "support_agent"):
        user = db.get(User, user_id)
        if not user:
            user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin user account not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin user account is deactivated.",
            )
        return AuthenticatedUser(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role="admin",
            admin_user=user,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unknown user role.",
        )


def require_author(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Dependency that enforces author role."""
    if not current_user.is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Author privileges required.",
        )
    return current_user


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Dependency that enforces admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required.",
        )
    return current_user
