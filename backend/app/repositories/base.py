from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing standard CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, item_id: Any) -> Optional[ModelType]:
        return self.db.get(self.model, item_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, obj: ModelType) -> ModelType:
        self.db.flush()
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()
