"""Modelos de WorkSchedule (Horário de Trabalho)."""
import enum
from sqlalchemy import Column, Integer, ForeignKey, Enum, Time, Boolean, UniqueConstraint
from app.core.database import Base


class Weekdays(enum.Enum):
    """Dias da semana."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class WorkSchedule(Base):
    """Representa o horário de trabalho de um usuário em um dia da semana."""
    __tablename__ = "workschedules"

    __table_args__ = (
        UniqueConstraint("user_id", "weekday", name="uq_user_weekday"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    weekday = Column("weekday", Enum(Weekdays))
    work_start = Column("work_start", Time)
    work_end = Column("work_end", Time)
    lunch_start = Column("lunch_start", Time)
    lunch_end = Column("lunch_end", Time)
    is_working = Column("is_working", Boolean, default=True)

    def __init__(self,tenant_id, user_id, weekday, work_start, work_end, lunch_start, lunch_end, is_working=True):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.weekday = weekday
        self.work_start = work_start
        self.work_end = work_end
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.is_working = is_working
