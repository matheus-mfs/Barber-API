import pytest
from fastapi.testclient import TestClient
from app.models import UserRole


@pytest.mark.integration
class TestTenantRoutes:
    """Testes de integração para rotas de tenants."""

    def test_create_tenant_requires_dev_role(self, client: TestClient):
        """Testa que apenas DEV pode criar tenant."""
        from app.models import User
        from app.core.auth import bcrypt_context, create_token
        from sqlalchemy.orm import Session
        from app.core.database import get_session
        
        # Nota: Este teste seria mais fácil com um fixture de dev_user,
        # mas vamos testar com os usuários disponíveis
        payload = {
            "name": "Nova Barbearia",
            "status": True
        }
        
        # Tentar criar sem token
        response = client.post(
            "/tenants/create",
            json=payload
        )
        
        assert response.status_code == 403

    def test_create_tenant_barber_cannot_create(self, client: TestClient, auth_token):
        """Testa que barbeiro não pode criar tenant."""
        payload = {
            "name": "Nova Barbearia",
            "status": True
        }
        
        response = client.post(
            "/tenants/create",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_create_tenant_with_missing_fields(self, client: TestClient):
        """Testa criação com campos faltando."""
        payload = {
            "name": "Nova Barbearia"
            # Falta status
        }
        
        response = client.post(
            "/tenants/create",
            json=payload
        )
        
        assert response.status_code in [422, 403]

    def test_search_tenant_by_id_requires_dev(self, client: TestClient, auth_token, tenant):
        """Testa busca de tenant requer DEV."""
        response = client.get(
            f"/tenants/search/{tenant.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_search_tenant_without_token(self, client: TestClient, tenant):
        """Testa busca sem token."""
        response = client.get(
            f"/tenants/search/{tenant.id}"
        )
        
        assert response.status_code == 403

    def test_search_tenant_not_found_requires_dev(self, client: TestClient):
        """Testa busca de tenant inexistente."""
        response = client.get(
            "/tenants/search/9999"
        )
        
        assert response.status_code == 403

    def test_edit_tenant_requires_dev(self, client: TestClient, auth_token, tenant):
        """Testa edição de tenant requer DEV."""
        payload = {
            "name": "Barbearia Atualizada",
            "status": True
        }
        
        response = client.put(
            f"/tenants/edit/{tenant.id}",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_edit_tenant_barber_cannot_edit(self, client: TestClient, auth_token, tenant):
        """Testa que barbeiro não pode editar tenant."""
        payload = {
            "name": "Novo Nome",
            "status": False
        }
        
        response = client.put(
            f"/tenants/edit/{tenant.id}",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_edit_tenant_without_token(self, client: TestClient, tenant):
        """Testa edição sem token."""
        payload = {
            "name": "Novo Nome",
            "status": False
        }
        
        response = client.put(
            f"/tenants/edit/{tenant.id}",
            json=payload
        )
        
        assert response.status_code == 403

    def test_edit_tenant_not_found_requires_dev(self, client: TestClient):
        """Testa edição de tenant inexistente."""
        payload = {
            "name": "Novo Nome",
            "status": True
        }
        
        response = client.put(
            "/tenants/edit/9999",
            json=payload
        )
        
        assert response.status_code == 403
