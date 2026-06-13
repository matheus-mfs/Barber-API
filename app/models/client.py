"""Modelo de Client (Cliente)."""
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """Representa um cliente da barbearia."""
    __tablename__ = "clients"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    telephone = Column("telephone", String)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    appointments = relationship("Appointment", back_populates="client")
    

    def __init__(self, tenant_id, name, telephone):
        self.tenant_id = tenant_id
        self.name = name
        self.telephone = telephone
