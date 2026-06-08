"""Modelos de Permission (Permissões)."""
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PermissionRole(enum.Enum):
    """Roles de permissão no sistema."""
    # USER SERVICE - Catálogo Próprio
    MANAGE_OWN_USER_SERVICES = "manage_own_user_services"
    
    # USER SERVICE - Todos
    MANAGE_ALL_USER_SERVICES = "manage_all_user_services"
    
    # APPOINTMENT - Próprio
    MANAGE_OWN_APPOINTMENTS = "manage_own_appointments"
    
    # APPOINTMENT - Todos
    MANAGE_ALL_APPOINTMENTS = "manage_all_appointments"
    
    # CLIENT
    VIEW_CLIENTS = "view_clients"
    MANAGE_ALL_CLIENTS = "manage_all_clients"
    
    # SERVICES (Barbearia)
    MANAGE_SERVICES = "manage_services"
    
    # SLOTS - Próprio
    MANAGE_OWN_SLOTS = "manage_own_slots"
    
    # SLOTS - Todos
    MANAGE_ALL_SLOTS = "manage_all_slots"
    
    # USER
    MANAGE_OWN_USER = "manage_own_user"
    MANAGE_ALL_USERS = "manage_all_users"
    
    # WORKSCHEDULES - Próprio
    MANAGE_OWN_WORKSCHEDULE = "manage_own_workschedule"
    
    # WORKSCHEDULES - Todos
    MANAGE_ALL_WORKSCHEDULES = "manage_all_workschedules"

    # PERMISSIONS 
    MANAGE_PERMISSIONS = "manage_permissions"
    
    # REPORTS
    VIEW_OWN_REPORTS = "view_own_reports"
    VIEW_ALL_REPORTS = "view_all_reports"
    
    # TENANT
    MANAGE_TENANT = "manage_tenant"


class Permission(Base):
    """Representa uma permissão no sistema."""
    __tablename__ = "permissions"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column("name", Enum(PermissionRole), unique=True)
    
    # Relationships
    users = relationship(
        "User",
        secondary="user_permissions",
        back_populates="permissions"
    )

    def __init__(self, name):
        self.name = name


class UserPermission(Base):
    """Relacionamento entre User e Permission."""
    __tablename__ = "user_permissions"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column("permission_id", Integer, ForeignKey("permissions.id"), nullable=False)

    def __init__(self, user_id, permission_id):
        self.user_id = user_id
        self.permission_id = permission_id
