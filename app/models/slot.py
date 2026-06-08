"""Modelos de Slot (Horários)."""
import enum
from datetime import timezone, datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Boolean, UniqueConstraint
from app.core.database import Base


class SlotStatus(enum.Enum):
    """Status de um slot de horário."""
    FREE = "free"
    BOOKED = "booked"
    BLOCKED = "blocked"


class Slot(Base):
    """Representa um slot de horário disponível para agendamento."""
    __tablename__ = "slots"

    __table_args__ = (
        UniqueConstraint("user_id", "date_time_init", name="uq_user_slot"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    date_time_init = Column("date_time_init", DateTime)
    date_time_end = Column("date_time_end", DateTime)
    status = Column("status", Enum(SlotStatus), default=SlotStatus.FREE)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, user_id, date_time_init, date_time_end, status=SlotStatus.FREE):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.date_time_init = date_time_init
        self.date_time_end = date_time_end
        self.status = status
