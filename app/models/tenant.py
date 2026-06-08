"""Modelo de Tenant (Barbearia)."""
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base


class Tenant(Base):
    """Representa uma barbearia/tenant no sistema."""
    __tablename__ = "tenants"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column("name", String)
    slug = Column("slug", String, unique=True)
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, name, slug, status=True):
        self.name = name
        self.slug = slug
        self.status = status
