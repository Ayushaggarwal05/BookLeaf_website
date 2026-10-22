import logging
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.dependencies import AuthenticatedUser
from backend.app.models.author import Author
from backend.app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> Tuple[AuthenticatedUser, str]:
        """
        Authenticate against both Author and User credentials.
        Returns authenticated principal and signed JWT token.
        """
        clean_email = email.strip().lower()

        # 1. Check Author accounts
        author_stmt = select(Author).where(Author.email.ilike(clean_email))
        author = self.db.scalars(author_stmt).first()

        if author:
            if not author.is_active:
                raise ValueError("This author account is inactive. Please contact support.")
            if verify_password(password, author.hashed_password):
                user_principal = AuthenticatedUser(
                    id=author.id,
                    email=author.email,
                    full_name=author.name,
                    role="author",
                    author=author,
                )
                token = create_access_token({
                    "sub": author.id,
                    "email": author.email,
                    "name": author.name,
                    "role": "author",
                    "author_id": author.id,
                })
                return user_principal, token

        # 2. Check Admin / Staff User accounts
        user_stmt = select(User).where(User.email.ilike(clean_email))
        user = self.db.scalars(user_stmt).first()

        if user:
            if not user.is_active:
                raise ValueError("This administrative account is inactive.")
            if verify_password(password, user.hashed_password):
                user_principal = AuthenticatedUser(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role="admin",
                    admin_user=user,
                )
                token = create_access_token({
                    "sub": user.id,
                    "email": user.email,
                    "name": user.full_name,
                    "role": "admin",
                })
                return user_principal, token

        raise ValueError("Invalid email or password.")

    def provision_demo_accounts(self) -> Dict[str, Any]:
        """
        Provision or update demo admin and author credentials safely for development/test.
        Does not overwrite custom passwords if already set.
        """
        summary = {
            "admin_created": False,
            "admin_updated": False,
            "authors_passwords_initialized": 0,
        }

        # 1. Provision Demo Admin
        admin_email = settings.DEMO_ADMIN_EMAIL.lower()
        admin = self.db.scalars(select(User).where(User.email.ilike(admin_email))).first()

        if not admin:
            admin = User(
                id="USR_ADMIN_DEMO",
                email=admin_email,
                full_name="BookLeaf Administrator",
                role="admin",
                is_active=True,
                hashed_password=get_password_hash(settings.DEMO_ADMIN_PASSWORD),
            )
            self.db.add(admin)
            summary["admin_created"] = True
        elif not admin.hashed_password:
            admin.hashed_password = get_password_hash(settings.DEMO_ADMIN_PASSWORD)
            admin.role = "admin"
            summary["admin_updated"] = True

        # 2. Provision default demo password for authors lacking credentials
        authors = self.db.scalars(select(Author)).all()
        for author in authors:
            if not author.hashed_password:
                author.hashed_password = get_password_hash(settings.DEMO_AUTHOR_PASSWORD)
                summary["authors_passwords_initialized"] += 1

        self.db.commit()
        logger.info(
            f"Demo provisioning complete: Admin created={summary['admin_created']}, "
            f"Admin updated={summary['admin_updated']}, Authors initialized={summary['authors_passwords_initialized']}"
        )
        return summary
