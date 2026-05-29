import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.mark.integration
class TestServiceRoutes:
    """Testes de integração para rotas de serviços."""

    def test_create_service_with_valid_data(self, client: TestClient, tenant, auth_token):
        """Testa criação de serviço com dados válidos."""
        payload = {
            "name": "Novo Serviço",
            "duration": 45,
            "price": "85.00",
            "status": True
        }
        
        response = client.post(
            "/services/create",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert "id_service" in response.json()

    def test_create_service_with_missing_fields(self, client: TestClient, tenant, auth_token):
        """Testa criação com campos faltando."""
        payload = {
            "name": "Novo Serviço"
            # Faltam duration e price
        }
        
        response = client.post(
            "/services/create",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 422

    def test_create_service_without_token(self, client: TestClient, tenant):
        """Testa criação sem token."""
        payload = {
            "name": "Novo Serviço",
            "duration": 45,
            "price": "85.00",
            "status": True
        }
        
        response = client.post(
            "/services/create",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 403

    def test_list_services_returns_services(self, client: TestClient, tenant, service_test):
        """Testa listagem de serviços."""
        response = client.get(
            "/services/list",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    def test_list_services_empty(self, client: TestClient, tenant):
        """Testa listagem quando não há serviços."""
        response = client.get(
            "/services/list",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        # Retorna lista vazia quando não há serviços
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_search_service_by_id(self, client: TestClient, tenant, service_test):
        """Testa busca de serviço por ID."""
        response = client.get(
            f"/services/search/{service_test.id}",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == service_test.id

    def test_search_service_not_found(self, client: TestClient, tenant):
        """Testa busca de serviço inexistente."""
        response = client.get(
            "/services/search/9999",
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 404

    def test_edit_service_with_valid_data(self, client: TestClient, tenant, auth_token, service_test):
        """Testa edição de serviço."""
        payload = {
            "name": "Serviço Atualizado",
            "duration": 60,
            "price": "100.00"
        }
        
        response = client.put(
            f"/services/edit/{service_test.id}",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "serviço atualizado"

    def test_edit_service_not_found(self, client: TestClient, tenant, auth_token):
        """Testa edição de serviço inexistente."""
        payload = {
            "name": "Novo Nome",
            "duration": 30,
            "price": "50.00"
        }
        
        response = client.put(
            "/services/edit/9999",
            json=payload,
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 404

    def test_edit_service_without_token(self, client: TestClient, tenant, service_test):
        """Testa edição sem token."""
        payload = {
            "name": "Novo Nome",
            "duration": 30,
            "price": "50.00"
        }
        
        response = client.put(
            f"/services/edit/{service_test.id}",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 403

    def test_toggle_service_status(self, client: TestClient, tenant, auth_token, service_test):
        """Testa toggle de status do serviço."""
        response = client.put(
            f"/services/active/{service_test.id}",
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        assert "status" in response.json()

    def test_toggle_service_status_not_found(self, client: TestClient, tenant, auth_token):
        """Testa toggle de status em serviço inexistente."""
        response = client.put(
            "/services/active/9999",
            headers={
                "host": f"{tenant.slug}.barbaria.com",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 404
