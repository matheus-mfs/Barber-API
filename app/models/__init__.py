"""Models do Barber API.

Este módulo exporta todos os modelos SQLAlchemy de forma centralizada.
"""

# Base
from app.models.base import Base

# Tenant
from app.models.tenant import Tenant

# User & Roles
from app.models.user import User, UserRole

# Permission & Roles
from app.models.permission import Permission, PermissionRole, UserPermission

# Service
from app.models.service import Service, UserService

# Schedule
from app.models.schedule import WorkSchedule, Weekdays

# Client
from app.models.client import Client

# Slot
from app.models.slot import Slot, SlotStatus

# Appointment
from app.models.appointment import Appointment, AppointmentStatus, AppointmentSlot

__all__ = [
    # Base
    "Base",
    
    # Tenant
    "Tenant",
    
    # User
    "User",
    "UserRole",
    
    # Permission
    "Permission",
    "PermissionRole",
    "UserPermission",
    
    # Service
    "Service",
    "UserService",
    
    # Schedule
    "WorkSchedule",
    "Weekdays",
    
    # Client
    "Client",
    
    # Slot
    "Slot",
    "SlotStatus",
    
    # Appointment
    "Appointment",
    "AppointmentStatus",
    "AppointmentSlot",
]
