"""Modelos de Service (Serviços)."""
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric, UniqueConstraint
from app.core.database import Base


class Service(Base):
    """Representa um serviço oferecido pela barbearia."""
    __tablename__ = "services"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    duration = Column("duration", Integer)
    price = Column("price", Numeric(10, 2))
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, duration, price, status=True):
        self.tenant_id = tenant_id
        self.name = name
        self.duration = duration
        self.price = price
        self.status = status


class UserService(Base):
    """Representa um serviço customizado por um barbeiro."""
    __tablename__ = "user_services"

    __table_args__ = (
        UniqueConstraint("tenant_id", "service_id", "user_id", name="uq_barber_service"),
    )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    service_id = Column("service_id", Integer, ForeignKey("services.id"), nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    custom_duration = Column("custom_duration", Integer)
    custom_price = Column("custom_price", Numeric(10, 2))
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, service_id, user_id, custom_duration, custom_price):
        self.tenant_id = tenant_id
        self.service_id = service_id
        self.user_id = user_id
        self.custom_duration = custom_duration
        self.custom_price = custom_price
