import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


@pytest.mark.integration
class TestSlotRoutes:
    """Testes de integração para rotas de slots."""

    def test_get_availability_slots(self, client: TestClient, user_service_test):
        """Testa busca de horários disponíveis."""
        response = client.get(
            f"/slots/availability?service_id={user_service_test.service_id}&user_id={user_service_test.user_id}",
        )
        
        # Pode retornar lista vazia ou com horários
        assert response.status_code in [200, 404]

    def test_get_availability_slots_invalid_service(self, client: TestClient, user):
        """Testa busca com serviço inexistente."""
        response = client.get(
            f"/slots/availability?service_id=9999&user_id={user.id}",
        )
        
        assert response.status_code == 404

    def test_block_slots_requires_auth(self, client: TestClient, auth_token):
        """Testa bloqueio de slots."""
        now = datetime.now(timezone.utc)
        start = now.replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        payload = {
            "init_block": start.isoformat(),
            "end_block": end.isoformat()
        }
        
        response = client.put(
            "/slots/block",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Pode retornar lista vazia ou slots bloqueados
        assert response.status_code in [200, 404]

    def test_block_slots_without_token(self, client: TestClient):
        """Testa bloqueio sem token."""
        now = datetime.now(timezone.utc)
        start = now.replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        payload = {
            "init_block": start.isoformat(),
            "end_block": end.isoformat()
        }
        
        response = client.put(
            "/slots/block",
            json=payload
        )
        
        assert response.status_code == 403

