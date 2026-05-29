import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.tenant_service import (
    validate_dev_permission,
    get_tenant_by_id,
    create_tenant_service,
    update_tenant_service
)
from app.models import UserRole
from app.schemas.tenant_schema import TenantSchema


@pytest.mark.unit
class TestTenantService:
    """Testes unitários para o serviço de tenants."""

    def test_validate_dev_permission_raises_error_for_non_dev(self, user):
        """Testa que usuário não-dev não pode acessar funções de dev."""
        with pytest.raises(HTTPException) as exc_info:
            validate_dev_permission(user)
        
        assert exc_info.value.status_code == 403
        assert "Acesso negado" in exc_info.value.detail

    def test_validate_dev_permission_allows_dev_user(self):
        """Testa que usuário dev pode acessar."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=1,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        
        # Não deve lançar exceção
        validate_dev_permission(dev_user)

    def test_get_tenant_by_id_requires_dev_permission(self, db_session: Session, user, tenant):
        """Testa que apenas dev pode buscar tenant."""
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_by_id(db_session, tenant.id, user)
        
        assert exc_info.value.status_code == 403

    def test_get_tenant_by_id_returns_tenant(self, db_session: Session, tenant):
        """Testa busca de tenant por ID (com usuário dev)."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=tenant.id,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        result = get_tenant_by_id(db_session, tenant.id, dev_user)
        
        assert result.id == tenant.id
        assert result.name == tenant.name

    def test_get_tenant_by_id_raises_404_when_not_found(self, db_session: Session):
        """Testa exceção quando tenant não existe."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=1,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_by_id(db_session, 9999, dev_user)
        
        assert exc_info.value.status_code == 404

    def test_create_tenant_service_creates_tenant(self, db_session: Session):
        """Testa criação de tenant."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=1,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        schema = TenantSchema(
            name="Nova Barbearia",
            status=True
        )
        
        result = create_tenant_service(db_session, schema, dev_user)
        
        assert result.id is not None
        assert result.name == "Nova Barbearia"
        assert result.slug == "nova-barbearia"
        assert result.status is True

    def test_create_tenant_service_generates_slug(self, db_session: Session):
        """Testa geração automática de slug."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=1,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        schema = TenantSchema(
            name="Barbearia São João da Costa",
            status=True
        )
        
        result = create_tenant_service(db_session, schema, dev_user)
        
        assert "sao-joao" in result.slug

    def test_create_tenant_service_requires_dev_permission(self, db_session: Session, user):
        """Testa que apenas dev pode criar tenant."""
        schema = TenantSchema(
            name="Nova Barbearia",
            status=True
        )
        
        with pytest.raises(HTTPException):
            create_tenant_service(db_session, schema, user)

    def test_update_tenant_service_updates_tenant(self, db_session: Session, tenant):
        """Testa atualização de tenant."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=tenant.id,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        schema = TenantSchema(
            name="Barbearia Atualizada",
            status=False
        )
        
        result = update_tenant_service(db_session, tenant.id, schema, dev_user)
        
        assert result.name == "Barbearia Atualizada"
        assert result.status is False

    def test_update_tenant_service_requires_dev_permission(self, db_session: Session, user, tenant):
        """Testa que apenas dev pode atualizar tenant."""
        schema = TenantSchema(
            name="Novo Nome",
            status=True
        )
        
        with pytest.raises(HTTPException):
            update_tenant_service(db_session, tenant.id, schema, user)

    def test_update_tenant_service_raises_404_when_not_found(self, db_session: Session):
        """Testa exceção ao atualizar tenant inexistente."""
        from app.models import User, UserRole
        from app.core.auth import bcrypt_context
        
        dev_user = User(
            tenant_id=1,
            name="Dev User",
            email="dev@example.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.DEV
        )
        db_session.add(dev_user)
        db_session.commit()
        
        schema = TenantSchema(
            name="Novo Nome",
            status=True
        )
        
        with pytest.raises(HTTPException):
            update_tenant_service(db_session, 9999, schema, dev_user)
