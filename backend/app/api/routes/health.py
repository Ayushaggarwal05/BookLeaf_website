from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db, check_database_connection

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service Health & Connectivity")
def get_health(db: Session = Depends(get_db)):
    """
    Check application lifecycle and database connectivity status.
    Returns 200 OK when connected, 503 Service Unavailable if database is unreachable.
    """
    db_health = check_database_connection(db)
    is_healthy = db_health.get("connected", False)

    payload = {
        "status": "healthy" if is_healthy else "unhealthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_health,
    }

    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=payload)
