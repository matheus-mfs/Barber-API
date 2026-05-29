import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import time

from app.services.work_schedule_service import (
    get_work_schedule_by_weekday,
    create_work_schedule_service,
    list_work_schedules_service,
    update_work_schedule_service
)
from app.models import Weekdays
from app.schemas.work_schedule import WorkScheduleSchema


@pytest.mark.unit
class TestWorkScheduleService:
    """Testes unitários para o serviço de horários de trabalho."""

    def test_get_work_schedule_by_weekday_returns_schedule(self, db_session: Session, work_schedule_test):
        """Testa busca de horário por dia da semana."""
        result = get_work_schedule_by_weekday(
            db_session, 
            Weekdays.MONDAY, 
            work_schedule_test.user_id
        )
        
        assert result.id == work_schedule_test.id
        assert result.weekday == Weekdays.MONDAY

    def test_get_work_schedule_by_weekday_raises_404_when_not_found(self, db_session: Session, user):
        """Testa exceção quando horário não existe."""
        with pytest.raises(HTTPException) as exc_info:
            get_work_schedule_by_weekday(db_session, Weekdays.FRIDAY, user.id)
        
        assert exc_info.value.status_code == 404

    def test_create_work_schedule_service_creates_schedule(self, db_session: Session, user):
        """Testa criação de horário de trabalho."""
        schema = WorkScheduleSchema(
            work_start=time(8, 0),
            work_end=time(17, 0),
            lunch_start=time(12, 0),
            lunch_end=time(13, 0),
            is_working=True
        )
        
        result = create_work_schedule_service(
            db_session, 
            user, 
            Weekdays.TUESDAY, 
            schema
        )
        
        assert result.user_id == user.id
        assert result.weekday == Weekdays.TUESDAY
        assert result.work_start == time(8, 0)
        assert result.work_end == time(17, 0)

    def test_create_work_schedule_service_raises_error_for_duplicate_weekday(self, db_session: Session, work_schedule_test, user):
        """Testa que não pode criar horário duplicado para mesmo dia."""
        schema = WorkScheduleSchema(
            work_start=time(9, 0),
            work_end=time(18, 0),
            lunch_start=time(12, 0),
            lunch_end=time(13, 0),
            is_working=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_work_schedule_service(
                db_session, 
                user, 
                work_schedule_test.weekday, 
                schema
            )
        
        assert exc_info.value.status_code == 403
        assert "ja cadastrado" in exc_info.value.detail

    def test_create_work_schedule_service_without_lunch_break(self, db_session: Session, user):
        """Testa criação de horário sem intervalo de almoço."""
        schema = WorkScheduleSchema(
            work_start=time(9, 0),
            work_end=time(18, 0),
            lunch_start=None,
            lunch_end=None,
            is_working=True
        )
        
        result = create_work_schedule_service(
            db_session, 
            user, 
            Weekdays.WEDNESDAY, 
            schema
        )
        
        assert result.lunch_start is None
        assert result.lunch_end is None

    def test_list_work_schedules_service_returns_all_schedules(self, db_session: Session, user):
        """Testa listagem de todos os horários do usuário."""
        # Cria múltiplos horários
        for weekday in [Weekdays.MONDAY, Weekdays.TUESDAY, Weekdays.WEDNESDAY]:
            schema = WorkScheduleSchema(
                work_start=time(9, 0),
                work_end=time(18, 0),
                lunch_start=time(12, 0),
                lunch_end=time(13, 0),
                is_working=True
            )
            create_work_schedule_service(db_session, user, weekday, schema)
        
        result = list_work_schedules_service(db_session, user.id)
        
        assert len(result) == 3

    def test_list_work_schedules_service_raises_404_when_empty(self, db_session: Session, user):
        """Testa exceção quando usuário não tem horários."""
        with pytest.raises(HTTPException) as exc_info:
            list_work_schedules_service(db_session, user.id)
        
        assert exc_info.value.status_code == 404

    def test_update_work_schedule_service_updates_times(self, db_session: Session, work_schedule_test):
        """Testa atualização de horário."""
        edit_schema = WorkScheduleSchema(
            work_start=time(7, 0),
            work_end=time(19, 0),
            lunch_start=time(13, 0),
            lunch_end=time(14, 0),
            is_working=True
        )
        
        result = update_work_schedule_service(
            db_session,
            work_schedule_test.weekday,
            work_schedule_test.user_id,
            edit_schema
        )
        
        assert result.work_start == time(7, 0)
        assert result.work_end == time(19, 0)
        assert result.lunch_start == time(13, 0)
        assert result.lunch_end == time(14, 0)

    def test_update_work_schedule_service_raises_404_when_not_found(self, db_session: Session, user):
        """Testa exceção ao atualizar horário inexistente."""
        schema = WorkScheduleSchema(
            work_start=time(9, 0),
            work_end=time(18, 0),
            lunch_start=time(12, 0),
            lunch_end=time(13, 0),
            is_working=True
        )
        
        with pytest.raises(HTTPException):
            update_work_schedule_service(
                db_session,
                Weekdays.FRIDAY,
                user.id,
                schema
            )
