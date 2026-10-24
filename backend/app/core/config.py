from typing import List, Optional, Any
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine workspace root directory (BookLeaf/)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = BACKEND_DIR.parent
PROJECT_ROOT = WORKSPACE_ROOT


class Settings(BaseSettings):
    """Application settings and environment configuration."""

    model_config = SettingsConfigDict(
        env_file=[str(WORKSPACE_ROOT / ".env"), str(BACKEND_DIR / ".env")],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_NAME: str = "BookLeaf Author Support & Communication Portal"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database configuration (defaults to SQLite in backend directory)
    DATABASE_URL: str = f"sqlite:///{(BACKEND_DIR / 'bookleaf_dev.db').as_posix()}"

    # CORS configuration
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Security and authentication
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Demo Environment Credentials (for test and local dev only)
    DEMO_ADMIN_EMAIL: str = "admin@bookleaf.in"
    DEMO_ADMIN_PASSWORD: str = "Admin@BookLeaf2026!"
    DEMO_AUTHOR_PASSWORD: str = "Author@BookLeaf2026!"

    # AI Integration with Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: int = 30

    # Sample dataset location
    SAMPLE_DATA_PATH: str = "data/bookleaf_sample_data.json"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_allowed_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v or []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            # Default to canonical backend sqlite db
            return f"sqlite:///{(BACKEND_DIR / 'bookleaf_dev.db').as_posix()}"
        v = v.strip()
        # Normalize legacy postgres:// and bare postgresql:// URI to postgresql+psycopg2://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+"):
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif v.startswith("sqlite:///") and not v.startswith("sqlite:///:memory:"):
            # Check if it's a relative path like sqlite:///./bookleaf_dev.db
            sqlite_path_str = v.replace("sqlite:///", "", 1)
            # If path does not contain a drive letter (e.g. C:) or start with /
            if ":" not in sqlite_path_str and not sqlite_path_str.startswith("/"):
                # Clean relative markers
                cleaned = sqlite_path_str.lstrip("./").lstrip(".\\")
                if (BACKEND_DIR / cleaned).is_file():
                    canonical_path = (BACKEND_DIR / cleaned).resolve()
                else:
                    canonical_path = (PROJECT_ROOT / cleaned).resolve()
                v = f"sqlite:///{canonical_path.as_posix()}"
        return v

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def resolved_sample_data_path(self) -> Path:
        """Resolve sample data path with fallback to root or parent directories."""
        candidate = Path(self.SAMPLE_DATA_PATH)
        if candidate.is_file():
            return candidate

        root_candidate = PROJECT_ROOT / self.SAMPLE_DATA_PATH
        if root_candidate.is_file():
            return root_candidate

        alternatives = [
            PROJECT_ROOT / "data" / "bookleaf_sample_data.json",
            PROJECT_ROOT / "data" / "FULLSTACK-SAMPLEDATA (1) (1) (1).json",
            Path("data/bookleaf_sample_data.json"),
        ]
        for alt in alternatives:
            if alt.is_file():
                return alt

        return root_candidate


settings = Settings()
