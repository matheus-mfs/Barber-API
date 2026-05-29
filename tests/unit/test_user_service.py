import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.user_service import (
    validate_admin,
    validate_user_exists,
    get_user_by_id,
    list_users_service,
    update_user_service,
    disable_user_service,
    active_user_service
)
from app.models import User, UserRole
from app.schemas.user_schema import UserEditSchema
from app.core.auth import bcrypt_context


@pytest.mark.unit
class TestUserService:
    """Testes unitários para o serviço de usuários."""

    def test_validate_admin_raises_error_for_barber(self, user):
        """Testa que barbeiro não pode executar ações admin."""
        with pytest.raises(HTTPException) as exc_info:
            validate_admin(user.role)
        
        assert exc_info.value.status_code == 400
        assert "Acesso negado" in exc_info.value.detail

    def test_validate_admin_allows_admin_user(self, admin_user):
        """Testa que admin pode executar ações."""
        # Não deve lançar exceção
        validate_admin(admin_user.role)

    def test_validate_user_exists_raises_error_for_none(self):
        """Testa validação com usuário None."""
        with pytest.raises(HTTPException) as exc_info:
            validate_user_exists(None)
        
        assert exc_info.value.status_code == 404
        assert "Usuario nao encontrado" in exc_info.value.detail

    def test_validate_user_exists_raises_error_for_empty_list(self):
        """Testa validação com lista vazia."""
        with pytest.raises(HTTPException):
            validate_user_exists([])

    def test_validate_user_exists_allows_valid_user(self, user):
        """Testa que usuário válido não lança exceção."""
        # Não deve lançar exceção
        validate_user_exists(user)

    def test_get_user_by_id_returns_user(self, db_session: Session, user):
        """Testa busca de usuário por ID."""
        result = get_user_by_id(db_session, user.id, user.tenant_id)
        
        assert result.id == user.id
        assert result.email == user.email

    def test_get_user_by_id_raises_404_when_not_found(self, db_session: Session, tenant):
        """Testa exceção quando usuário não existe."""
        with pytest.raises(HTTPException) as exc_info:
            get_user_by_id(db_session, 9999, tenant.id)
        
        assert exc_info.value.status_code == 404

    def test_list_users_service_returns_all_users(self, db_session: Session, tenant, user, admin_user):
        """Testa listagem de todos os usuários do tenant."""
        result = list_users_service(db_session, tenant.id)
        
        assert len(result) == 2
        emails = {u.email for u in result}
        assert user.email in emails
        assert admin_user.email in emails

    def test_list_users_service_raises_404_when_empty(self, db_session: Session):
        """Testa exceção quando não há usuários."""
        from app.models import Tenant
        
        empty_tenant = Tenant(name="Tenant Vazio", slug="tenant-vazio")
        db_session.add(empty_tenant)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            list_users_service(db_session, empty_tenant.id)
        
        assert exc_info.value.status_code == 404

    def test_update_user_service_updates_name_and_email(self, db_session: Session, user):
        """Testa atualização de usuário."""
        edit_schema = UserEditSchema(
            name="João Silva Atualizado",
            email="joao.novo@barbaria.com"
        )
        
        result = update_user_service(db_session, user.id, edit_schema, user)
        
        assert result.name == "João Silva Atualizado"
        assert result.email == "joao.novo@barbaria.com"

    def test_update_user_service_barber_cannot_update_other_user(self, db_session: Session, user, admin_user):
        """Testa que barbeiro não pode atualizar outro usuário."""
        edit_schema = UserEditSchema(
            name="Nome Novo",
            email="novo@email.com"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            update_user_service(db_session, admin_user.id, edit_schema, user)
        
        assert exc_info.value.status_code == 400
        assert "Acesso negado" in exc_info.value.detail

    def test_update_user_service_barber_can_update_own_profile(self, db_session: Session, user):
        """Testa que barbeiro pode atualizar seu próprio perfil."""
        edit_schema = UserEditSchema(
            name="Nome Atualizado",
            email="novo@email.com"
        )
        
        result = update_user_service(db_session, user.id, edit_schema, user)
        
        assert result.name == "Nome Atualizado"
        assert result.email == "novo@email.com"

    def test_update_user_service_admin_can_update_any_user(self, db_session: Session, user, admin_user):
        """Testa que admin pode atualizar qualquer usuário."""
        edit_schema = UserEditSchema(
            name="Nome Novo",
            email="novo@email.com"
        )
        
        result = update_user_service(db_session, user.id, edit_schema, admin_user)
        
        assert result.name == "Nome Novo"
        assert result.email == "novo@email.com"

    def test_update_user_service_raises_404_when_not_found(self, db_session: Session, admin_user):
        """Testa exceção ao atualizar usuário inexistente."""
        edit_schema = UserEditSchema(
            name="Nome",
            email="email@email.com"
        )
        
        with pytest.raises(HTTPException):
            update_user_service(db_session, 9999, edit_schema, admin_user)

    def test_disable_user_service_sets_status_false(self, db_session: Session, user, admin_user):
        """Testa desabilitação de usuário."""
        result = disable_user_service(db_session, user.id, admin_user)
        
        assert result.status is False

    def test_disable_user_service_only_admin_can_disable(self, db_session: Session, user, admin_user):
        """Testa que apenas admin pode desabilitar usuário."""
        with pytest.raises(HTTPException):
            disable_user_service(db_session, admin_user.id, user)

    def test_disable_user_service_raises_404_when_not_found(self, db_session: Session, admin_user):
        """Testa exceção ao desabilitar usuário inexistente."""
        with pytest.raises(HTTPException):
            disable_user_service(db_session, 9999, admin_user)

    def test_active_user_service_sets_status_true(self, db_session: Session, user, admin_user):
        """Testa ativação de usuário."""
        # Primeiro desabilita
        disable_user_service(db_session, user.id, admin_user)
        
        # Depois ativa
        result = active_user_service(db_session, user.id, admin_user)
        
        assert result.status is True

    def test_active_user_service_only_admin_can_activate(self, db_session: Session, user, admin_user):
        """Testa que apenas admin pode ativar usuário."""
        disable_user_service(db_session, admin_user.id, admin_user)
        
        with pytest.raises(HTTPException):
            active_user_service(db_session, admin_user.id, user)

    def test_active_user_service_raises_404_when_not_found(self, db_session: Session, admin_user):
        """Testa exceção ao ativar usuário inexistente."""
        with pytest.raises(HTTPException):
            active_user_service(db_session, 9999, admin_user)
