"""Database base class and configuration."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all database models."""

    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active = Column(Boolean, default=True, nullable=False)
