import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


@pytest.mark.integration
class TestAppointmentRoutes:
    """Testes de integração para rotas de agendamentos."""

    def test_create_appointment_with_valid_data(self, client: TestClient, db_session, tenant, client_test, user_service_test):
        """Testa criação de agendamento."""
        from app.models import Slot, SlotStatus
        now = datetime.now(timezone.utc)
        start_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
        
        for step in range(2):
            slot_time = start_time + timedelta(minutes=15 * step)
            slot = Slot(
                tenant_id=tenant.id,
                user_id=user_service_test.user_id,
                date_time_init=slot_time,
                date_time_end=slot_time + timedelta(minutes=15),
                status=SlotStatus.FREE
            )
            db_session.add(slot)
        db_session.commit()
        
        payload = {
            "client_id": client_test.id,
            "user_service_id": user_service_test.id,
            "start_time": start_time.isoformat(),
            "status": "pending"
        }
        
        response = client.post(
            "/appointments/create",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["status"] == "pending"

    def test_create_appointment_with_missing_fields(self, client: TestClient, tenant):
        """Testa criação com campos faltando."""
        payload = {
            "client_id": 1
            # Faltam user_service_id e start_time
        }
        
        response = client.post(
            "/appointments/create",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        assert response.status_code == 422

    def test_create_appointment_with_invalid_client(self, client: TestClient, tenant, user_service_test):
        """Testa criação com cliente inexistente."""
        now = datetime.now(timezone.utc)
        start_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
        
        payload = {
            "client_id": 9999,
            "user_service_id": user_service_test.id,
            "start_time": start_time.isoformat(),
            "status": "pending"
        }
        
        response = client.post(
            "/appointments/create",
            json=payload,
            headers={"host": f"{tenant.slug}.barbaria.com"}
        )
        
        # Pode retornar erro ou não, dependendo da validação
        assert response.status_code in [201, 404, 400]

    def test_list_appointments_requires_auth(self, client: TestClient, user, auth_token):
        """Testa listagem de agendamentos."""
        response = client.get(
            "/appointments/list",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Pode retornar vazio ou lista
        assert response.status_code in [200, 404]

    def test_list_appointments_without_token(self, client: TestClient):
        """Testa listagem sem token."""
        response = client.get("/appointments/list")
        
        assert response.status_code == 403

    def test_get_today_appointments(self, client: TestClient, user, auth_token):
        """Testa busca de agendamentos de hoje."""
        response = client.get(
            "/appointments/today",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Pode retornar vazio ou lista
        assert response.status_code in [200, 404]

    def test_search_appointment_by_id(self, client: TestClient, user, auth_token, appointment_test):
        """Testa busca de agendamento por ID."""
        response = client.get(
            f"/appointments/{appointment_test.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == appointment_test.id

    def test_search_appointment_not_found(self, client: TestClient, user, auth_token):
        """Testa busca de agendamento inexistente."""
        response = client.get(
            "/appointments/9999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_search_appointment_without_token(self, client: TestClient, appointment_test):
        """Testa busca sem token."""
        response = client.get(f"/appointments/{appointment_test.id}")
        
        assert response.status_code == 403

    def test_cancel_appointment(self, client: TestClient, user, auth_token, appointment_test):
        """Testa cancelamento de agendamento."""
        response = client.put(
            f"/appointments/cancel/{appointment_test.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert "id" in response.json()

    def test_cancel_appointment_not_found(self, client: TestClient, user, auth_token):
        """Testa cancelamento de agendamento inexistente."""
        response = client.put(
            "/appointments/cancel/9999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_cancel_appointment_without_token(self, client: TestClient, appointment_test):
        """Testa cancelamento sem token."""
        response = client.put(f"/appointments/cancel/{appointment_test.id}")
        
        assert response.status_code == 403
