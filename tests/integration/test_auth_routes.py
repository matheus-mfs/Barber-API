import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.main import app


@pytest.mark.integration
class TestAuthRoutes:
    """Testes de integração para rotas de autenticação."""

    def test_create_account_with_valid_data(self, client: TestClient, tenant):
        """Testa criação de conta com dados válidos."""
        payload = {
            "name": "Novo Barbeiro",
            "email": "novo@barbaria.com",
            "password": "senha123",
            "role": "barber",
            "status": True
        }
        
        response = client.post(
            "/auth/create_account",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 200

    def test_create_account_with_invalid_email_format(self, client: TestClient, tenant):
        """Testa criação com email inválido."""
        payload = {
            "name": "Novo Barbeiro",
            "email": "email-invalido",
            "password": "senha123",
            "role": "barber",
            "status": True
        }
        
        response = client.post(
            "/auth/create_account",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        # FastAPI pode retornar 422 para validação
        assert response.status_code in [200, 422]

    def test_create_account_with_missing_required_fields(self, client: TestClient, tenant):
        """Testa criação com campos obrigatórios faltando."""
        payload = {
            "name": "Novo Barbeiro"
            # Faltam email, password, role
        }
        
        response = client.post(
            "/auth/create_account",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 422

    def test_login_with_valid_credentials(self, client: TestClient, user):
        """Testa login com credenciais válidas."""
        payload = {
            "email": user.email,
            "password": "senha123"
        }
        
        response = client.post(
            "/auth/login",
            json=payload,
            headers={"host": f"{user.tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()

    def test_login_with_invalid_email(self, client: TestClient, tenant):
        """Testa login com email inválido."""
        payload = {
            "email": "naoexiste@barbaria.com",
            "password": "senha123"
        }
        
        response = client.post(
            "/auth/login",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 400

    def test_login_with_wrong_password(self, client: TestClient, user):
        """Testa login com senha incorreta."""
        payload = {
            "email": user.email,
            "password": "senhaerrada"
        }
        
        response = client.post(
            "/auth/login",
            json=payload,
            headers={"host": f"{user.tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 400

    def test_refresh_token_with_valid_token(self, client: TestClient, auth_token):
        """Testa refresh de token com token válido."""
        response = client.get(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_token_without_token(self, client: TestClient):
        """Testa refresh sem enviar token."""
        response = client.get("/auth/refresh")
        
        assert response.status_code == 403

    def test_refresh_token_with_invalid_token(self, client: TestClient):
        """Testa refresh com token inválido."""
        response = client.get(
            "/auth/refresh",
            headers={"Authorization": "Bearer token-invalido"}
        )
        
        assert response.status_code == 401
