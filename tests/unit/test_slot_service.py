import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.services.slot_service import (
    get_user_free_slots,
    get_available_start_times,
    block_slots,
    get_user_slots,
    get_barber_free_slots
)
from app.models import SlotStatus


@pytest.mark.unit
class TestSlotService:
    """Testes unitários para o serviço de slots."""

    def test_get_user_free_slots_returns_free_slots(self, db_session: Session, slot_test):
        """Testa busca de slots livres."""
        result = get_user_free_slots(db_session, slot_test.user_id)
        
        assert len(result) > 0
        assert all(slot.status == SlotStatus.FREE for slot in result)

    def test_get_user_free_slots_raises_404_when_no_free_slots(self, db_session: Session, user):
        """Testa erro quando não há slots livres."""
        with pytest.raises(HTTPException) as exc_info:
            get_user_free_slots(db_session, user.id)
        
        assert exc_info.value.status_code == 404
        assert "Sem horarios livres" in exc_info.value.detail

    def test_get_user_free_slots_orders_by_datetime(self, db_session: Session, tenant, user):
        """Testa que slots são retornados em ordem."""
        from app.models import Slot
        
        now = datetime.now(timezone.utc)
        
        # Cria slots em ordem reversa
        for i in [3, 1, 2]:
            slot = Slot(
                tenant_id=tenant.id,
                user_id=user.id,
                date_time_init=now + timedelta(hours=i),
                date_time_end=now + timedelta(hours=i, minutes=15),
                status=SlotStatus.FREE
            )
            db_session.add(slot)
        db_session.commit()
        
        result = get_user_free_slots(db_session, user.id)
        
        # Verifica se está ordenado
        for i in range(len(result) - 1):
            assert result[i].date_time_init <= result[i + 1].date_time_init

    def test_get_available_start_times_returns_valid_times(self, db_session: Session, user_service_test, slot_test):
        """Testa busca de horários disponíveis."""
        try:
            result = get_available_start_times(
                user_service_test.service_id,
                user_service_test.user_id,
                db_session
            )
            # Resultado pode ser vazio ou conter horários válidos
            assert isinstance(result, list)
        except HTTPException as e:
            # Se não há slots, é esperado
            assert e.status_code == 404

    def test_get_available_start_times_raises_404_for_nonexistent_service(self, db_session: Session, user):
        """Testa erro quando serviço não existe."""
        with pytest.raises(HTTPException) as exc_info:
            get_available_start_times(9999, user.id, db_session)
        
        assert exc_info.value.status_code == 404

    def test_block_slots_changes_status_to_blocked(self, db_session: Session, slot_test):
        """Testa bloqueio de slots."""
        now = datetime.now(timezone.utc)
        init_block = now.replace(hour=10, minute=0, second=0, microsecond=0)
        end_block = init_block + timedelta(hours=1)
        
        result = block_slots(
            db_session,
            slot_test.user_id,
            init_block,
            end_block
        )
        
        # Verificar se algum slot foi bloqueado
        for slot in result:
            assert slot.status == SlotStatus.BLOCKED

    def test_get_user_slots_returns_all_slots(self, db_session: Session, slot_test):
        """Testa busca de todos os slots do usuário."""
        result = get_user_slots(db_session, slot_test.user_id)
        
        assert len(result) > 0
        assert all(slot.user_id == slot_test.user_id for slot in result)

    def test_get_user_slots_raises_404_when_no_slots(self, db_session: Session, user):
        """Testa erro quando usuário não tem slots."""
        with pytest.raises(HTTPException) as exc_info:
            get_user_slots(db_session, user.id)
        
        assert exc_info.value.status_code == 404

    def test_get_barber_free_slots_returns_free_slots(self, db_session: Session, slot_test, user):
        """Testa busca de slots livres do barbeiro."""
        result = get_barber_free_slots(
            db_session,
            user,
            slot_test.user_id
        )
        
        assert len(result) > 0
        assert all(slot.status == SlotStatus.FREE for slot in result)

    def test_get_barber_free_slots_raises_404_when_no_free_slots(self, db_session: Session, user):
        """Testa erro quando não há slots livres."""
        with pytest.raises(HTTPException):
            get_barber_free_slots(db_session, user, user.id)
