from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Numeric, Time, Enum, UniqueConstraint
from core.database import Base
from datetime import timezone, datetime
import enum



class Tenant(Base):
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

class UserRole(enum.Enum):
    BARBER = "barber"
    ADMIN = "admin"
    DEV = "dev"

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    email = Column("email", String, nullable=False)
    password = Column("password", String)
    role = Column("role", Enum(UserRole), default=UserRole.BARBER) # Barbeiro ou Admin
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, email, password, role=UserRole.BARBER, status=True):
        self.tenant_id = tenant_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status

class Client(Base):
    __tablename__ = "clients"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False )
    name = Column("name", String)
    telephone = Column("telephone", String)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, telephone):
        self.tenant_id = tenant_id
        self.name = name
        self.telephone = telephone

class Service(Base):
    __tablename__ = "services"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    duration = Column("duration", Integer)
    price = Column("price", Numeric(10,2))
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, duration, price, status=True):
        self.tenant_id = tenant_id
        self.name = name
        self.duration = duration
        self.price = price
        self.status = status

class SlotStatus(enum.Enum):
    FREE = "free"
    BOOKED = "booked"
    BLOCKED = "blocked"

class Slot(Base):
    __tablename__ = "slots"

    __table_args__ = (
        UniqueConstraint("user_id", "date_time_init", name="uq_user_slot"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
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

class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    client_id = Column("client_id", Integer, ForeignKey("clients.id"), nullable=False)
    service_id = Column("service_id", Integer, ForeignKey("services.id"), nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column("slot_id", Integer, ForeignKey("slots.id"), nullable=False)
    status = Column("status", Enum(AppointmentStatus), default=AppointmentStatus.PENDING) 
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, client_id, service_id, user_id, slot_id, status=AppointmentStatus.PENDING):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.service_id = service_id
        self.user_id = user_id
        self.slot_id = slot_id
        self.status = status

class Weekdays(enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class WorkSchedule(Base):
    __tablename__ = "workschedules"

    __table_args__ = (
        UniqueConstraint("user_id", "weekday", name="uq_user_weekday"),
    )

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    weekday = Column("weekday", Enum(Weekdays))
    work_start = Column("work_start", Time)
    work_end = Column("work_end", Time)
    lunch_start = Column("lunch_start", Time)
    lunch_end = Column("lunch_end", Time)
    is_working = Column("is_working", Boolean, default=True)

    def __init__(self, user_id, weekday, work_start, work_end, lunch_start, lunch_end, is_working=True):
        self.user_id = user_id
        self.weekday = weekday
        self.work_start = work_start
        self.work_end = work_end
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.is_working = is_working

        
# iniciar o alembic: poetry run alembic init alembic

# criar a migração: poetry run alembic revision --autogenerate -m "menssagem"

# executar a migração: poetry run alembic upgrade head

