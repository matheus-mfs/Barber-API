from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.models import User, Weekdays
from app.schemas.work_schedule import WorkScheduleSchema, WorkScheduleEditSchema, WorkScheduleStatusSchema
from app.services.work_schedule_service import (
    create_work_schedule_service,
    list_work_schedules_service,
    get_work_schedule_by_weekday,
    update_work_schedule_service,
    status_weekday_service
)

router = APIRouter(prefix="/workschedules",tags=["workschedules"])

@router.post("/create")
def create_work_schedule(
    work_schedule_schema: WorkScheduleSchema, 
    current_user: User = Depends(check_token),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Criar horario de trabalho"""

    ws = create_work_schedule_service(session, current_user, work_schedule_schema)
    return {
        "id": ws.id,
        "user_id": ws.user_id,
        "weekday": ws.weekday,
        "work_start": ws.work_start.isoformat() if ws.work_start else None,
        "work_end": ws.work_end.isoformat() if ws.work_end else None,
        "lunch_start": ws.lunch_start.isoformat() if ws.lunch_start else None,
        "lunch_end": ws.lunch_end.isoformat() if ws.lunch_end else None,
        "is_working": ws.is_working
    }

@router.get("/list/{user_id}")
def list_work_schedules(
    user_id: int,
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """Lista horarios de trabalho"""

    schedules = list_work_schedules_service(session, user_id)
    return [{
        "id": ws.id,
        "user_id": ws.user_id,
        "weekday": ws.weekday,
        "work_start": ws.work_start.isoformat() if ws.work_start else None,
        "work_end": ws.work_end.isoformat() if ws.work_end else None,
        "lunch_start": ws.lunch_start.isoformat() if ws.lunch_start else None,
        "lunch_end": ws.lunch_end.isoformat() if ws.lunch_end else None,
        "is_working": ws.is_working
    } for ws in schedules]

@router.get("/search/{weekday}/user/{user_id}")
def search_work_schedule(
    weekday: Weekdays, 
    user_id: int ,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Buscar horarios de um determinado dia"""
    
    ws = get_work_schedule_by_weekday(session, weekday, user_id)
    return {
        "id": ws.id,
        "user_id": ws.user_id,
        "weekday": ws.weekday,
        "work_start": ws.work_start.isoformat() if ws.work_start else None,
        "work_end": ws.work_end.isoformat() if ws.work_end else None,
        "lunch_start": ws.lunch_start.isoformat() if ws.lunch_start else None,
        "lunch_end": ws.lunch_end.isoformat() if ws.lunch_end else None,
        "is_working": ws.is_working
    }

@router.put("/edit/")
def edit_work_schedule(
    work_schedule_schema: WorkScheduleEditSchema, 
    current_user: User = Depends(check_token), 
    session: Session = Depends(get_session)
)-> Dict[str, Any]:
    """Editar horario de um determinado dia"""
    
    ws = update_work_schedule_service(session, current_user, work_schedule_schema)
    return {
        "id": ws.id,
        "user_id": ws.user_id,
        "weekday": ws.weekday,
        "work_start": ws.work_start.isoformat() if ws.work_start else None,
        "work_end": ws.work_end.isoformat() if ws.work_end else None,
        "lunch_start": ws.lunch_start.isoformat() if ws.lunch_start else None,
        "lunch_end": ws.lunch_end.isoformat() if ws.lunch_end else None,
        "is_working": ws.is_working
    }

@router.put("/status/")
def status_weekday(
    work_schedule_status_schema: WorkScheduleStatusSchema,
    current_user: User = Depends(check_token), 
    session: Session = Depends(get_session)
)-> Dict[str, Any]:
    """Ativar/Desativar um dia da semana"""
    
    work_schedule = status_weekday_service(session, current_user, work_schedule_status_schema)
    return {
        "weekday": work_schedule.weekday,
        "is_working": work_schedule.is_working,
    }