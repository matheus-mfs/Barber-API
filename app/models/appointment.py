"""Modelos de Appointment (Agendamentos)."""
import enum
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from app.core.database import Base


class AppointmentStatus(enum.Enum):
    """Status de um agendamento."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    """Representa um agendamento de cliente com barbeiro."""
    __tablename__ = "appointments"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    client_id = Column("client_id", Integer, ForeignKey("clients.id"), nullable=False)
    user_service_id = Column("user_service_id", Integer, ForeignKey("user_services.id"), nullable=False)
    start_time = Column("start_time", DateTime, nullable=False)
    end_time = Column("end_time", DateTime, nullable=False)
    status = Column("status", Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, client_id, user_service_id, start_time, end_time, status=AppointmentStatus.PENDING):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.user_service_id = user_service_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status


class AppointmentSlot(Base):
    """Relacionamento entre Appointment e Slot."""
    __tablename__ = "appointment_slots"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    appointment_id = Column("appointment_id", Integer, ForeignKey("appointments.id"), nullable=False)
    slot_id = Column("slot_id", Integer, ForeignKey("slots.id"), nullable=False, unique=True)

    def __init__(self, appointment_id, slot_id):
        self.appointment_id = appointment_id
        self.slot_id = slot_id
