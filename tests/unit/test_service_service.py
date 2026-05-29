import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.service_service import (
    create_new_service,
    list_tenant_services,
    get_service_by_id,
    update_service,
    status_service_by_id
)
from app.models import Service
from app.schemas.service_schema import ServiceSchema, ServiceEditSchema


@pytest.mark.unit
class TestServiceService:
    """Testes unitários para o serviço de serviços."""

    def test_create_new_service_with_valid_data(self, db_session: Session, user, tenant):
        """Testa criação de serviço com dados válidos."""
        schema = ServiceSchema(
            name="Corte Masculino",
            duration=30,
            price=Decimal("50.00"),
            status=True
        )
        
        result = create_new_service(db_session, user, schema)
        
        assert result.id is not None
        assert result.name == "corte masculino"  # normalizado
        assert result.duration == 30
        assert result.price == Decimal("50.00")
        assert result.status is True
        assert result.tenant_id == tenant.id

    def test_create_new_service_normalizes_name(self, db_session: Session, user):
        """Testa normalização do nome para lowercase."""
        schema = ServiceSchema(
            name="  BARBA DESIGN  ",
            duration=20,
            price=Decimal("35.00"),
            status=True
        )
        
        result = create_new_service(db_session, user, schema)
        
        assert result.name == "barba design"

    def test_create_new_service_raises_error_when_duplicate(self, db_session: Session, user):
        """Testa que não pode criar serviço duplicado."""
        schema = ServiceSchema(
            name="Hidratação",
            duration=45,
            price=Decimal("60.00"),
            status=True
        )
        
        create_new_service(db_session, user, schema)
        
        with pytest.raises(HTTPException) as exc_info:
            create_new_service(db_session, user, schema)
        
        assert exc_info.value.status_code == 401
        assert "Servico ja cadastrado" in exc_info.value.detail

    def test_create_new_service_different_tenants_can_have_same_name(self, db_session: Session, user):
        """Testa que serviços de tenants diferentes podem ter mesmo nome."""
        from app.models import Tenant, User, UserRole
        from app.core.auth import bcrypt_context
        
        other_tenant = Tenant(name="Outra Barbearia", slug="outra-barbearia")
        db_session.add(other_tenant)
        db_session.commit()
        
        other_user = User(
            tenant_id=other_tenant.id,
            name="Outro Barbeiro",
            email="outro@email.com",
            password=bcrypt_context.hash("senha123"),
            role=UserRole.BARBER
        )
        db_session.add(other_user)
        db_session.commit()
        
        schema = ServiceSchema(
            name="Corte Masculino",
            duration=30,
            price=Decimal("50.00"),
            status=True
        )
        
        result1 = create_new_service(db_session, user, schema)
        result2 = create_new_service(db_session, other_user, schema)
        
        assert result1.id != result2.id
        assert result1.tenant_id != result2.tenant_id

    def test_list_tenant_services_returns_active_services(self, db_session: Session, user, tenant):
        """Testa listagem de serviços ativos do tenant."""
        schema1 = ServiceSchema(name="Serviço 1", duration=30, price=Decimal("50.00"), status=True)
        schema2 = ServiceSchema(name="Serviço 2", duration=45, price=Decimal("75.00"), status=True)
        
        create_new_service(db_session, user, schema1)
        create_new_service(db_session, user, schema2)
        
        result = list_tenant_services(db_session, tenant.id)
        
        assert len(result) == 2

    def test_list_tenant_services_excludes_inactive_services(self, db_session: Session, user, tenant):
        """Testa que serviços inativos não aparecem na lista."""
        schema_active = ServiceSchema(name="Ativo", duration=30, price=Decimal("50.00"), status=True)
        schema_inactive = ServiceSchema(name="Inativo", duration=30, price=Decimal("50.00"), status=False)
        
        create_new_service(db_session, user, schema_active)
        create_new_service(db_session, user, schema_inactive)
        
        result = list_tenant_services(db_session, tenant.id)
        
        assert len(result) == 1
        assert result[0].name == "ativo"

    def test_list_tenant_services_returns_empty_list_when_no_services(self, db_session: Session, tenant):
        """Testa lista vazia quando não há serviços."""
        result = list_tenant_services(db_session, tenant.id)
        
        assert result == []

    def test_get_service_by_id_returns_service(self, db_session: Session, service_test):
        """Testa busca de serviço por ID."""
        result = get_service_by_id(db_session, service_test.id, service_test.tenant_id)
        
        assert result.id == service_test.id
        assert result.name == service_test.name

    def test_get_service_by_id_raises_404_when_not_found(self, db_session: Session, tenant):
        """Testa exceção quando serviço não existe."""
        with pytest.raises(HTTPException) as exc_info:
            get_service_by_id(db_session, 9999, tenant.id)
        
        assert exc_info.value.status_code == 404
        assert "Nenhum servico encontrado" in exc_info.value.detail

    def test_get_service_by_id_respects_tenant_isolation(self, db_session: Session, service_test):
        """Testa que serviço não é acessível por outro tenant."""
        from app.models import Tenant
        
        other_tenant = Tenant(name="Outra Barbearia", slug="outra-barbearia")
        db_session.add(other_tenant)
        db_session.commit()
        
        with pytest.raises(HTTPException):
            get_service_by_id(db_session, service_test.id, other_tenant.id)

    def test_update_service_with_valid_data(self, db_session: Session, service_test):
        """Testa atualização de serviço."""
        edit_schema = ServiceEditSchema(
            name="Corte Premium",
            duration=45,
            price=Decimal("75.00")
        )
        
        result = update_service(db_session, service_test.id, service_test.tenant_id, edit_schema)
        
        assert result.name == "corte premium"
        assert result.duration == 45
        assert result.price == Decimal("75.00")

    def test_update_service_normalizes_name(self, db_session: Session, service_test):
        """Testa que atualização normaliza o nome."""
        edit_schema = ServiceEditSchema(
            name="  NOVO SERVIÇO  ",
            duration=30,
            price=Decimal("50.00")
        )
        
        result = update_service(db_session, service_test.id, service_test.tenant_id, edit_schema)
        
        assert result.name == "novo serviço"

    def test_update_service_raises_404_when_not_found(self, db_session: Session, tenant):
        """Testa exceção ao atualizar serviço inexistente."""
        edit_schema = ServiceEditSchema(
            name="Novo",
            duration=30,
            price=Decimal("50.00")
        )
        
        with pytest.raises(HTTPException):
            update_service(db_session, 9999, tenant.id, edit_schema)

    def test_status_service_toggles_status(self, db_session: Session, service_test):
        """Testa toggle de status do serviço."""
        initial_status = service_test.status
        
        result = status_service_by_id(db_session, service_test.id, service_test.tenant_id)
        
        assert result.status == (not initial_status)

    def test_status_service_toggle_twice_restores_original(self, db_session: Session, service_test):
        """Testa que toggle duplo restaura o status original."""
        original_status = service_test.status
        
        status_service_by_id(db_session, service_test.id, service_test.tenant_id)
        result = status_service_by_id(db_session, service_test.id, service_test.tenant_id)
        
        assert result.status == original_status

    def test_status_service_raises_404_when_not_found(self, db_session: Session, tenant):
        """Testa exceção ao toggle de serviço inexistente."""
        with pytest.raises(HTTPException):
            status_service_by_id(db_session, 9999, tenant.id)
