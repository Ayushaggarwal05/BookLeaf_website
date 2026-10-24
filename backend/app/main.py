import sys
from pathlib import Path

# Ensure project root is in sys.path so 'backend.app...' imports always resolve
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings
from backend.app.core.database import check_database_connection
from backend.app.api.routes import api_router, api_v1_router
from backend.app.api.routes.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bookleaf.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook for startup verification and graceful shutdown."""
    logger.info(f"Starting {settings.APP_NAME} (v{settings.APP_VERSION})...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")

    # Validate database connectivity at startup
    health = check_database_connection()
    if not health.get("connected"):
        logger.error(f"DATABASE STARTUP WARNING: Unable to connect to database: {health.get('error')}")
        if settings.is_production:
            raise RuntimeError(
                f"Production database connection failed on startup: {health.get('error')}"
            )
    else:
        logger.info(f"Database connectivity confirmed. Dialect: {health.get('database')}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_application() -> FastAPI:
    """Application factory for BookLeaf portal."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration with regex fallback for Vercel/Render preview domains
    origins = list(set([settings.FRONTEND_ORIGIN] + settings.ALLOWED_ORIGINS))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"^https://.*\.vercel\.app$|^https://.*\.render\.com$|^http://localhost(:\d+)?$|^http://127\.0\.0\.1(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routes: Root health endpoint and API subrouters
    app.include_router(health_router)
    app.include_router(api_router)
    app.include_router(api_v1_router)

    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Welcome to BookLeaf Author Support & Communication Portal API",
            "docs": "/docs",
            "health": "/health",
            "version": settings.APP_VERSION,
        }

    # Centralized Error Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for error in exc.errors():
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            formatted_errors.append({
                "field": loc,
                "message": error.get("msg"),
                "type": error.get("type"),
            })
        return JSONResponse(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            content={
                "detail": "Invalid request payload or parameters.",
                "errors": formatted_errors,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error executing {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database error occurred while processing your request. Please try again later."
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception processing {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred."
            },
        )

    return app


app = create_application()
