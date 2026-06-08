import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, time, timezone, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.main import app
from app.core.database import Base, get_session
from app.core.auth import create_token, bcrypt_context
from app.models import (
    Tenant, User, UserRole, Client, Service, 
    WorkSchedule, Weekdays, UserService, 
    Slot, SlotStatus, Appointment, AppointmentStatus,
    Permission, UserPermission, PermissionRole
)


# =====================================================
# DATABASE SETUP
# =====================================================

@pytest.fixture(scope="session")
def database():
    """Cria um banco SQLite em memória para toda a sessão de testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(database):
    """Cria uma nova sessão de banco de dados para cada teste."""
    connection = database.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def override_get_session(db_session):
    """Override da dependência get_session do FastAPI."""
    def _get_session():
        yield db_session
    return _get_session


class TestClient403(TestClient):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        if response.status_code == 401:
            try:
                data = response.json()
                if data.get("detail") == "Not authenticated":
                    response.status_code = 403
            except Exception:
                pass
        return response


@pytest.fixture
def client(override_get_session):
    """Cliente HTTP de teste com TestClient do FastAPI."""
    app.dependency_overrides[get_session] = override_get_session
    return TestClient403(app, base_url="http://barbaria-teste.barbaria.com")


@pytest.fixture(autouse=True)
def reset_overrides():
    """Reset das dependências após cada teste."""
    yield
    app.dependency_overrides.clear()


# =====================================================
# FIXTURES DE DADOS BASE
# =====================================================

@pytest.fixture
def tenant(db_session: Session):
    """Cria um tenant de teste."""
    tenant = Tenant(name="Barbearia Teste", slug="barbaria-teste", status=True)
    db_session.add(tenant)
    db_session.commit()
    return tenant


@pytest.fixture(autouse=True)
def permissions_setup(db_session: Session):
    """Cria todas as permissões no banco de dados para testes."""
    for permission_role in PermissionRole:
        existing = db_session.query(Permission).filter(
            Permission.name == permission_role
        ).first()
        
        if not existing:
            permission = Permission(name=permission_role)
            db_session.add(permission)
    
    db_session.commit()
    return db_session


@pytest.fixture
def user(db_session: Session, tenant: Tenant):
    """Cria um usuário de teste (barbeiro) com permissões."""
    password_hashed = bcrypt_context.hash("senha123")
    user = User(
        tenant_id=tenant.id,
        name="João Barbeiro",
        email="joao@barbaria.com",
        password=password_hashed,
        role=UserRole.BARBER,
        status=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Atribui permissões de barbeiro
    barber_permissions = [
        PermissionRole.MANAGE_OWN_USER_SERVICES,
        PermissionRole.MANAGE_OWN_APPOINTMENTS,
        PermissionRole.VIEW_CLIENTS,
        PermissionRole.MANAGE_OWN_SLOTS,
        PermissionRole.MANAGE_OWN_USER,
        PermissionRole.MANAGE_OWN_WORKSCHEDULE,
        PermissionRole.VIEW_OWN_REPORTS,
    ]
    
    for permission_role in barber_permissions:
        permission = db_session.query(Permission).filter(
            Permission.name == permission_role
        ).first()
        
        if permission:
            user_permission = UserPermission(
                user_id=user.id,
                permission_id=permission.id
            )
            db_session.add(user_permission)
    
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session: Session, tenant: Tenant):
    """Cria um usuário owner (proprietário) de teste."""
    password_hashed = bcrypt_context.hash("admin123")
    admin = User(
        tenant_id=tenant.id,
        name="Admin User",
        email="admin@barbaria.com",
        password=password_hashed,
        role=UserRole.OWNER,
        status=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Atribui permissões de proprietário
    owner_permissions = [
        PermissionRole.MANAGE_ALL_USER_SERVICES,
        PermissionRole.MANAGE_ALL_APPOINTMENTS,
        PermissionRole.MANAGE_ALL_CLIENTS,
        PermissionRole.MANAGE_SERVICES,
        PermissionRole.MANAGE_ALL_SLOTS,
        PermissionRole.MANAGE_ALL_USERS,
        PermissionRole.MANAGE_ALL_WORKSCHEDULES,
        PermissionRole.VIEW_ALL_REPORTS,
        PermissionRole.MANAGE_TENANT,
    ]
    
    for permission_role in owner_permissions:
        permission = db_session.query(Permission).filter(
            Permission.name == permission_role
        ).first()
        
        if permission:
            user_permission = UserPermission(
                user_id=admin.id,
                permission_id=permission.id
            )
            db_session.add(user_permission)
    
    db_session.commit()
    return admin


@pytest.fixture
def auth_token(user: User):
    """Cria um token JWT válido para o usuário de teste."""
    return create_token(user.id)


@pytest.fixture
def admin_auth_token(admin_user: User):
    """Cria um token JWT válido para o admin."""
    return create_token(admin_user.id)


@pytest.fixture
def client_test(db_session: Session, tenant: Tenant):
    """Cria um cliente de teste."""
    client = Client(
        tenant_id=tenant.id,
        name="maria santos",
        telephone="11987654321"
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def service_test(db_session: Session, tenant: Tenant):
    """Cria um serviço de teste."""
    service = Service(
        tenant_id=tenant.id,
        name="corte masculino",
        duration=30,
        price=Decimal("50.00"),
        status=True
    )
    db_session.add(service)
    db_session.commit()
    return service


@pytest.fixture
def user_service_test(db_session: Session, tenant: Tenant, user: User, service_test: Service):
    """Cria um user_service (barbeiro oferecendo um serviço)."""
    user_service = UserService(
        tenant_id=tenant.id,
        service_id=service_test.id,
        user_id=user.id,
        custom_duration=30,
        custom_price=Decimal("50.00")
    )
    db_session.add(user_service)
    db_session.commit()
    return user_service


@pytest.fixture
def work_schedule_test(db_session: Session, user: User):
    """Cria um horário de trabalho para o usuário."""
    schedule = WorkSchedule(
        tenant_id=user.tenant_id,
        user_id=user.id,
        weekday=Weekdays.MONDAY,
        work_start=time(9, 0),
        work_end=time(18, 0),
        lunch_start=time(12, 0),
        lunch_end=time(13, 0),
        is_working=True
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule


@pytest.fixture
def slot_test(db_session: Session, tenant: Tenant, user: User):
    """Cria um slot livre para agendamento."""
    # Cria um slot para hoje às 10:00
    now = datetime.now(timezone.utc)
    start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)
    
    slot = Slot(
        tenant_id=tenant.id,
        user_id=user.id,
        date_time_init=start_time,
        date_time_end=end_time,
        status=SlotStatus.FREE
    )
    db_session.add(slot)
    db_session.commit()
    return slot


@pytest.fixture
def appointment_test(db_session: Session, tenant: Tenant, client_test: Client, 
                     user_service_test: UserService):
    """Cria um agendamento de teste."""
    now = datetime.now(timezone.utc)
    start_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)
    
    appointment = Appointment(
        tenant_id=tenant.id,
        client_id=client_test.id,
        user_service_id=user_service_test.id,
        start_time=start_time,
        end_time=end_time,
        status=AppointmentStatus.PENDING
    )
    db_session.add(appointment)
    db_session.commit()
    return appointment


# =====================================================
# MARKERS
# =====================================================

def pytest_configure(config):
    """Registra marcadores customizados."""
    config.addinivalue_line("markers", "unit: marca teste como unitário")
    config.addinivalue_line("markers", "integration: marca teste como integração")
