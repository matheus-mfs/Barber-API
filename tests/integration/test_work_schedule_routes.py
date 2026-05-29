import pytest
from fastapi.testclient import TestClient
from datetime import time


@pytest.mark.integration
class TestWorkScheduleRoutes:
    """Testes de integração para rotas de horários de trabalho."""

    def test_create_work_schedule_with_valid_data(self, client: TestClient, user, auth_token):
        """Testa criação de horário de trabalho."""
        payload = {
            "work_start": "09:00",
            "work_end": "18:00",
            "lunch_start": "12:00",
            "lunch_end": "13:00",
            "is_working": True
        }
        
        response = client.post(
            "/workschedules/create?weekday=tuesday",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["weekday"] == "tuesday"

    def test_create_work_schedule_without_lunch(self, client: TestClient, user, auth_token):
        """Testa criação sem intervalo de almoço."""
        payload = {
            "work_start": "09:00",
            "work_end": "18:00",
            "lunch_start": None,
            "lunch_end": None,
            "is_working": True
        }
        
        response = client.post(
            "/workschedules/create?weekday=wednesday",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_create_work_schedule_duplicate_weekday(self, client: TestClient, work_schedule_test, auth_token):
        """Testa criação de horário duplicado para mesmo dia."""
        payload = {
            "work_start": "08:00",
            "work_end": "17:00",
            "lunch_start": "12:00",
            "lunch_end": "13:00",
            "is_working": True
        }
        
        response = client.post(
            "/workschedules/create?weekday=monday",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403

    def test_create_work_schedule_without_token(self, client: TestClient):
        """Testa criação sem token."""
        payload = {
            "work_start": "09:00",
            "work_end": "18:00",
            "lunch_start": "12:00",
            "lunch_end": "13:00",
            "is_working": True
        }
        
        response = client.post(
            "/workschedules/create?weekday=tuesday",
            json=payload
        )
        
        assert response.status_code == 403

    def test_list_work_schedules(self, client: TestClient, work_schedule_test, auth_token):
        """Testa listagem de horários."""
        response = client.get(
            "/workschedules/list",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_work_schedule_by_weekday(self, client: TestClient, work_schedule_test, auth_token):
        """Testa busca de horário por dia da semana."""
        response = client.get(
            "/workschedules/search/monday",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["weekday"] == "monday"

    def test_search_work_schedule_not_found(self, client: TestClient, user, auth_token):
        """Testa busca de horário inexistente."""
        response = client.get(
            "/workschedules/search/friday",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_edit_work_schedule(self, client: TestClient, work_schedule_test, auth_token):
        """Testa edição de horário."""
        payload = {
            "work_start": "07:00",
            "work_end": "19:00",
            "lunch_start": "13:00",
            "lunch_end": "14:00"
        }
        
        response = client.put(
            "/workschedules/edit/monday",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["work_start"] == "07:00:00"

    def test_edit_work_schedule_not_found(self, client: TestClient, user, auth_token):
        """Testa edição de horário inexistente."""
        payload = {
            "work_start": "09:00",
            "work_end": "18:00",
            "lunch_start": "12:00",
            "lunch_end": "13:00"
        }
        
        response = client.put(
            "/workschedules/edit/friday",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_block_weekday(self, client: TestClient, work_schedule_test, auth_token):
        """Testa bloqueio de dia da semana."""
        response = client.put(
            "/workschedules/block/monday",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert "weekday" in response.json()

    def test_active_weekday(self, client: TestClient, work_schedule_test, auth_token):
        """Testa ativação de dia da semana."""
        response = client.put(
            "/workschedules/active/monday",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
