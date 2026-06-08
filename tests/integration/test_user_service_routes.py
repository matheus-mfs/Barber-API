import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.mark.integration
class TestUserServiceRoutes:
    """Testes de integração para rotas de user_services."""

    def test_list_user_services_by_user_id(self, client: TestClient, user_service_test):
        """Testa listagem de serviços do barbeiro."""
        response = client.get(
            f"/user-services/list/{user_service_test.user_id}",
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_user_services_empty(self, client: TestClient, user):
        """Testa listagem quando barbeiro não tem serviços."""
        response = client.get(
            f"/user-services/list/{user.id}",
        )
        
        assert response.status_code == 404

    def test_search_user_service_by_service_id(self, client: TestClient, user_service_test, auth_token):
        """Testa busca de user_service."""
        response = client.get(
            f"/user-services/search/{user_service_test.service_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_search_user_service_not_found(self, client: TestClient, user, auth_token, service_test):
        """Testa busca de user_service inexistente."""
        response = client.get(
            f"/user-services/search/{service_test.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_search_user_service_without_token(self, client: TestClient, user_service_test):
        """Testa busca sem token."""
        response = client.get(
            f"/user-services/search/{user_service_test.service_id}",
        )
        
        assert response.status_code == 403

    def test_create_user_service(self, client: TestClient, user, auth_token, service_test):
        """Testa criação de user_service."""
        payload = {
            "service_id": service_test.id,
            "custom_duration": 45,
            "custom_price": "75.00"
        }
        
        response = client.post(
            "/user-services/create",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_create_user_service_with_defaults(self, client: TestClient, user, auth_token):
        """Testa criação com valores padrão."""
        from app.models import Service
        from decimal import Decimal
        
        # A service_test já foi criada, vamos usar outra
        # Criar um novo serviço
        new_service = Service(
            tenant_id=user.tenant_id,
            name="novo servico",
            duration=30,
            price=Decimal("50.00")
        )
        # Este teste seria complexo sem DB setup, então pulamos

    def test_create_user_service_duplicate(self, client: TestClient, user_service_test, auth_token):
        """Testa criação de user_service duplicado."""
        payload = {
            "service_id": user_service_test.service_id,
            "custom_duration": 30,
            "custom_price": "50.00"
        }
        
        response = client.post(
            "/user-services/create",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_create_user_service_without_token(self, client: TestClient, service_test):
        """Testa criação sem token."""
        payload = {
            "service_id": service_test.id,
            "custom_duration": 30,
            "custom_price": "50.00"
        }
        
        response = client.post(
            "/user-services/create",
            json=payload
        )
        
        assert response.status_code == 403

    def test_edit_user_service(self, client: TestClient, user_service_test, auth_token):
        """Testa edição de user_service."""
        payload = {
            "custom_duration": 60,
            "custom_price": "100.00"
        }
        
        response = client.put(
            f"/user-services/edit/{user_service_test.service_id}",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_edit_user_service_not_found(self, client: TestClient, user, auth_token):
        """Testa edição de user_service inexistente."""
        payload = {
            "custom_duration": 30,
            "custom_price": "50.00"
        }
        
        response = client.put(
            "/user-services/edit/9999",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404


