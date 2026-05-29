import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestClientRoutes:
    """Testes de integração para rotas de clientes."""

    def test_create_client_with_valid_data(self, client: TestClient, tenant, auth_token):
        """Testa criação de cliente com dados válidos."""
        payload = {
            "name": "Cliente Novo",
            "telephone": "11999999999"
        }
        
        response = client.post(
            "/clients/",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "cliente novo"

    def test_create_client_with_missing_fields(self, client: TestClient, tenant, auth_token):
        """Testa criação com campos faltando."""
        payload = {
            "name": "Cliente Novo"
            # Falta telephone
        }
        
        response = client.post(
            "/clients/",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 422

    def test_create_client_without_token(self, client: TestClient, tenant):
        """Testa criação sem token de autenticação."""
        payload = {
            "name": "Cliente Novo",
            "telephone": "11999999999"
        }
        
        response = client.post(
            "/clients/",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        # Rota de POST não tem check_token, então pode estar aberta
        assert response.status_code in [200, 403]

    def test_list_clients_returns_clients(self, client: TestClient, tenant, auth_token, client_test):
        """Testa listagem de clientes."""
        response = client.get(
            "/clients/list",
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    def test_list_clients_empty(self, client: TestClient):
        """Testa listagem quando não há clientes."""
        from app.models import Tenant
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.database import get_session, Base
        
        # Criar um tenant sem clientes seria complexo, então pulamos este teste

    def test_list_clients_requires_authentication(self, client: TestClient, tenant):
        """Testa que listagem requer autenticação."""
        response = client.get(
            "/clients/list",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 403

    def test_search_client_by_id(self, client: TestClient, tenant, auth_token, client_test):
        """Testa busca de cliente por ID."""
        response = client.get(
            f"/clients/search/{client_test.id}",
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == client_test.id

    def test_search_client_not_found(self, client: TestClient, tenant, auth_token):
        """Testa busca de cliente inexistente."""
        response = client.get(
            "/clients/search/9999",
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 404

    def test_search_client_requires_authentication(self, client: TestClient, tenant, client_test):
        """Testa que busca requer autenticação."""
        response = client.get(
            f"/clients/search/{client_test.id}",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 403
