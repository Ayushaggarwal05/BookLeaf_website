from fastapi import APIRouter
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.authors import router as authors_router
from backend.app.api.routes.books import router as books_router
from backend.app.api.routes.tickets import router as tickets_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.author_portal import router as author_portal_router
from backend.app.api.routes.admin_portal import router as admin_portal_router

# Legacy Phase 1 router (/api)
api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(authors_router)
api_router.include_router(books_router)
api_router.include_router(tickets_router)

# Production Versioned Router (/api/v1)
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(author_portal_router)
api_v1_router.include_router(admin_portal_router)

__all__ = ["api_router", "api_v1_router"]
