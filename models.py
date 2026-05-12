from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Numeric
from core.database import Base
from datetime import timezone, datetime

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column("name", String)
    status = Column("status", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, name, status=True):
        self.name = name
        self.status = status

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    name = Column("name", String)
    email = Column("email", String, unique=True, nullable=False)
    password = Column("password", String)
    role = Column("role", String) # Barbeiro ou Admin
    status = Column("status", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, email, password, role, status=True, admin=False):
        self.tenant_id = tenant_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status
        self.admin = admin

class Client(Base):
    __tablename__ = "clients"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer, ForeignKey("tenants.id"), nullable=False )
    name = Column("name", String)
    telephone = Column("telephone", String)
    email = Column("email", String, unique=True, nullable=False)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, name, telephone, email):
        self.tenant_id = tenant_id
        self.name = name
        self.telephone = telephone
        self.email = email

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

class Slot(Base):
    __tablename__ = "slots"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    date_time_init = Column("date_time_init", DateTime)
    date_time_end = Column("date_time_end", DateTime)
    status = Column("status", String, default="FREE") #(FREE, BOOKED, BLOCKED)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, user_id, date_time_init, date_time_end, status="FREE"):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.date_time_init = date_time_init
        self.date_time_end = date_time_end
        self.status = status

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    tenant_id = Column("tenant_id", Integer,  ForeignKey("tenants.id"), nullable=False)
    client_id = Column("client_id", Integer, ForeignKey("clients.id"), nullable=False)
    service_id = Column("service_id", Integer, ForeignKey("services.id"), nullable=False)
    slot_id = Column("slot_id", Integer, ForeignKey("slots.id"), nullable=False)
    status = Column("status", String, default="PENDING") #(PENDING, CONFIRMED, COMPLETED, CANCELLED)
    created_at = Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, tenant_id, client_id, service_id, slot_id, status="PENDING"):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.service_id = service_id
        self.slot_id = slot_id
        self.status = status
        