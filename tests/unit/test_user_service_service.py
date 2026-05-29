import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.user_service_service import (
    post_create_barber_service,
    get_list_barber_service,
    get_id_user_service,
    put_edit_user_service,
    put_disable_user_service,
    put_active_user_service
)
from app.schemas.user_service_schema import UserServiceSchema, UserServiceEditSchema


@pytest.mark.unit
class TestUserServiceService:
    """Testes unitários para o serviço de user_service (barbeiro + serviço)."""

    def test_post_create_barber_service_creates_user_service(self, db_session: Session, user, service_test):
        """Testa criação de user_service."""
        schema = UserServiceSchema(
            service_id=service_test.id,
            custom_duration=40,
            custom_price=Decimal("60.00")
        )
        
        result = post_create_barber_service(schema, user, db_session)
        
        assert result.id is not None
        assert result.service_id == service_test.id
        assert result.user_id == user.id
        assert result.custom_duration == 40
        assert result.custom_price == Decimal("60.00")

    def test_post_create_barber_service_uses_default_price_when_none(self, db_session: Session, user, service_test):
        """Testa que usa preço do serviço se não informado."""
        schema = UserServiceSchema(
            service_id=service_test.id,
            custom_duration=30,
            custom_price=None
        )
        
        result = post_create_barber_service(schema, user, db_session)
        
        assert result.custom_price == service_test.price

    def test_post_create_barber_service_uses_default_duration_when_none(self, db_session: Session, user, service_test):
        """Testa que usa duração do serviço se não informada."""
        schema = UserServiceSchema(
            service_id=service_test.id,
            custom_duration=None,
            custom_price=Decimal("50.00")
        )
        
        result = post_create_barber_service(schema, user, db_session)
        
        assert result.custom_duration == service_test.duration

    def test_post_create_barber_service_raises_403_for_duplicate_service(self, db_session: Session, user, service_test):
        """Testa que não pode atribuir mesmo serviço duas vezes."""
        schema = UserServiceSchema(
            service_id=service_test.id,
            custom_duration=30,
            custom_price=Decimal("50.00")
        )
        
        post_create_barber_service(schema, user, db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            post_create_barber_service(schema, user, db_session)
        
        assert exc_info.value.status_code == 403

    def test_post_create_barber_service_raises_404_for_nonexistent_service(self, db_session: Session, user):
        """Testa erro quando serviço não existe."""
        schema = UserServiceSchema(
            service_id=9999,
            custom_duration=30,
            custom_price=Decimal("50.00")
        )
        
        with pytest.raises(HTTPException) as exc_info:
            post_create_barber_service(schema, user, db_session)
        
        assert exc_info.value.status_code == 404

    def test_post_create_barber_service_respects_tenant_isolation(self, db_session: Session, user):
        """Testa que barbeiro só pode usar serviços do seu tenant."""
        from app.models import Tenant, Service, User, UserRole
        from app.core.auth import bcrypt_context
        
        other_tenant = Tenant(name="Outra Barbearia", slug="outra-barbearia")
        db_session.add(other_tenant)
        db_session.commit()
        
        other_service = Service(
            tenant_id=other_tenant.id,
            name="Serviço Outro",
            duration=30,
            price=Decimal("50.00")
        )
        db_session.add(other_service)
        db_session.commit()
        
        schema = UserServiceSchema(
            service_id=other_service.id,
            custom_duration=30,
            custom_price=Decimal("50.00")
        )
        
        with pytest.raises(HTTPException):
            post_create_barber_service(schema, user, db_session)

    def test_get_list_barber_service_returns_all_services(self, db_session: Session, user, service_test):
        """Testa listagem de serviços do barbeiro."""
        schema = UserServiceSchema(
            service_id=service_test.id,
            custom_duration=30,
            custom_price=Decimal("50.00")
        )
        post_create_barber_service(schema, user, db_session)
        
        result = get_list_barber_service(user.id, db_session)
        
        assert len(result) == 1
        assert result[0].user_id == user.id

    def test_get_list_barber_service_raises_404_when_empty(self, db_session: Session, user):
        """Testa erro quando barbeiro não tem serviços."""
        with pytest.raises(HTTPException) as exc_info:
            get_list_barber_service(user.id, db_session)
        
        assert exc_info.value.status_code == 404

    def test_get_id_user_service_returns_service(self, db_session: Session, user_service_test):
        """Testa busca de user_service específico."""
        result = get_id_user_service(
            user_service_test.service_id,
            user_service_test.user_id,
            db_session
        )
        
        assert result.id == user_service_test.id

    def test_get_id_user_service_raises_404_when_not_found(self, db_session: Session, user, service_test):
        """Testa erro quando user_service não existe."""
        with pytest.raises(HTTPException):
            get_id_user_service(service_test.id, user.id, db_session)

    def test_put_edit_user_service_updates_custom_fields(self, db_session: Session, user_service_test, user):
        """Testa edição de user_service."""
        edit_schema = UserServiceEditSchema(
            custom_duration=50,
            custom_price=Decimal("75.00")
        )
        
        result = put_edit_user_service(
            user_service_test.service_id,
            edit_schema,
            user,
            db_session
        )
        
        assert result.custom_duration == 50
        assert result.custom_price == Decimal("75.00")

    def test_put_edit_user_service_raises_404_when_not_found(self, db_session: Session, user):
        """Testa erro ao editar user_service inexistente."""
        edit_schema = UserServiceEditSchema(
            custom_duration=30,
            custom_price=Decimal("50.00")
        )
        
        with pytest.raises(HTTPException):
            put_edit_user_service(9999, edit_schema, user, db_session)

    def test_put_disable_user_service_sets_status_false(self, db_session: Session, user_service_test, user):
        """Testa desabilitação de user_service."""
        result = put_disable_user_service(
            user_service_test.service_id,
            user,
            db_session
        )
        
        assert result.status is False

    def test_put_disable_user_service_raises_404_when_not_found(self, db_session: Session, user):
        """Testa erro ao desabilitar user_service inexistente."""
        with pytest.raises(HTTPException):
            put_disable_user_service(9999, user, db_session)

    def test_put_active_user_service_sets_status_true(self, db_session: Session, user_service_test, user):
        """Testa ativação de user_service."""
        # Primeiro desabilita
        put_disable_user_service(user_service_test.service_id, user, db_session)
        
        # Depois ativa
        result = put_active_user_service(
            user_service_test.service_id,
            user,
            db_session
        )
        
        assert result.status is True

    def test_put_active_user_service_raises_404_when_not_found(self, db_session: Session, user):
        """Testa erro ao ativar user_service inexistente."""
        with pytest.raises(HTTPException):
            put_active_user_service(9999, user, db_session)
