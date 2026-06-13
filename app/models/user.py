"""Modelo de User (Usuário)."""
import enum
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.permission import PermissionRole


class UserRole(enum.Enum):
    """Roles de usuário no sistema."""
    BARBER = "barber"
    OWNER = "owner"
    DEV = "dev"


class User(Base):
    """Representa um usuário (barbeiro ou dono) no sistema."""
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    email = Column("email", String, nullable=False)
    password = Column("password", String)
    role = Column("role", Enum(UserRole), default=UserRole.BARBER)
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tenant = relationship("Tenant")
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")
    user_services = relationship("UserService", back_populates="user")

    def __init__(self, tenant_id, name, email, password, role=UserRole.BARBER, status=True):
        self.tenant_id = tenant_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status



