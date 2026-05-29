import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.client_service import (
    create_new_client,
    list_tenant_clients,
    get_client_by_id
)
from app.models import Client
from app.schemas.client_schema import ClientSchema


@pytest.mark.unit
class TestClientService:
    """Testes unitários para o serviço de clientes."""

    def test_create_new_client_with_valid_data(self, db_session: Session, tenant):
        """Testa criação de cliente com dados válidos."""
        client_schema = ClientSchema(name="João Silva", telephone="11999999999")
        
        result = create_new_client(db_session, tenant.id, client_schema)
        
        assert result.id is not None
        assert result.name == "joão silva"  # normalizado
        assert result.telephone == "11999999999"  # apenas dígitos
        assert result.tenant_id == tenant.id


    def test_create_new_client_returns_existing_client(self, db_session: Session, tenant):
        """Testa que criar cliente duplicado retorna o existente."""
        client_schema = ClientSchema(name="Ana Costa", telephone="21987654321")
        
        # Cria primeiro cliente
        first = create_new_client(db_session, tenant.id, client_schema)
        
        # Tenta criar novamente
        second = create_new_client(db_session, tenant.id, client_schema)
        
        assert first.id == second.id

    def test_create_new_client_with_empty_name(self, db_session: Session, tenant):
        """Testa criação com nome vazio."""
        client_schema = ClientSchema(name="   ", telephone="11999999999")
        
        result = create_new_client(db_session, tenant.id, client_schema)
        
        # Nome fica vazio após strip
        assert result.name == ""

    def test_list_tenant_clients_returns_clients(self, db_session: Session, tenant):
        """Testa listagem de clientes do tenant."""
        client1 = ClientSchema(name="Cliente 1", telephone="11999999999")
        client2 = ClientSchema(name="Cliente 2", telephone="11888888888")
        
        create_new_client(db_session, tenant.id, client1)
        create_new_client(db_session, tenant.id, client2)
        
        result = list_tenant_clients(db_session, tenant.id)
        
        assert len(result) == 2
        assert result[0].name == "cliente 1"
        assert result[1].name == "cliente 2"

    def test_list_tenant_clients_raises_404_when_empty(self, db_session: Session, tenant):
        """Testa que lançar exceção quando não há clientes."""
        with pytest.raises(HTTPException) as exc_info:
            list_tenant_clients(db_session, tenant.id)
        
        assert exc_info.value.status_code == 404
        assert "Sem clientes cadastrados" in exc_info.value.detail

    def test_list_tenant_clients_returns_only_tenant_clients(self, db_session: Session, tenant):
        """Testa que lista apenas clientes do tenant específico."""
        from app.models import Tenant
        
        other_tenant = Tenant(name="Outra Barbearia", slug="outra-barbearia")
        db_session.add(other_tenant)
        db_session.commit()
        
        client1 = ClientSchema(name="Cliente Tenant 1", telephone="11999999999")
        client2 = ClientSchema(name="Cliente Outra", telephone="11888888888")
        
        create_new_client(db_session, tenant.id, client1)
        create_new_client(db_session, other_tenant.id, client2)
        
        result = list_tenant_clients(db_session, tenant.id)
        
        assert len(result) == 1
        assert result[0].name == "cliente tenant 1"

    def test_get_client_by_id_returns_client(self, db_session: Session, client_test):
        """Testa busca de cliente por ID."""
        result = get_client_by_id(db_session, client_test.id, client_test.tenant_id)
        
        assert result.id == client_test.id
        assert result.name == client_test.name

    def test_get_client_by_id_raises_404_when_not_found(self, db_session: Session, tenant):
        """Testa exceção quando cliente não existe."""
        with pytest.raises(HTTPException) as exc_info:
            get_client_by_id(db_session, 9999, tenant.id)
        
        assert exc_info.value.status_code == 404
        assert "Cliente nao encontrado" in exc_info.value.detail

    def test_get_client_by_id_respects_tenant_isolation(self, db_session: Session, client_test, tenant):
        """Testa que cliente não é acessível por outro tenant."""
        from app.models import Tenant
        
        other_tenant = Tenant(name="Outra Barbearia", slug="outra-barbearia")
        db_session.add(other_tenant)
        db_session.commit()
        
        with pytest.raises(HTTPException):
            get_client_by_id(db_session, client_test.id, other_tenant.id)

    def test_get_client_by_id_with_nonexistent_tenant(self, db_session: Session):
        """Testa busca com tenant inexistente."""
        with pytest.raises(HTTPException):
            get_client_by_id(db_session, 1, 9999)
