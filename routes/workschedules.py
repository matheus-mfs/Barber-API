from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from models import User, Weekdays
from schemas import WorkScheduleSchema, WorkScheduleEditSchema
from services.work_schedule_service import (
    create_work_schedule_service,
    list_work_schedules_service,
    get_work_schedule_by_weekday,
    update_work_schedule_service,
    block_weekday_service,
    active_weekday_service
)

router = APIRouter(prefix="/workschedules",tags=["workschedules"])

@router.post("/create")
def create_work_schedule(weekday: Weekdays, work_schedule_schema: WorkScheduleSchema, 
                         current_user: User = Depends(check_token),session: Session = Depends(get_session)):

    create_work_schedule_service(session=session, current_user=current_user, weekday=weekday, work_schedule_schema=work_schedule_schema)

    return {
        "mensagem": "Horario cadastrado"
    }

@router.get("/list")
def list_work_schedules(current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    return list_work_schedules_service(session=session, user_id=current_user.id)

@router.get("/search/{weekday}")
def search_work_schedule(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    return get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=current_user.id)

@router.put("/edit/{weekday}")
def edit_work_schedule(weekday: Weekdays, work_schedule_schema: WorkScheduleEditSchema, 
                       current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    update_work_schedule_service(session=session, weekday=weekday, 
                                 user_id=current_user.id, work_schedule_schema=work_schedule_schema)
    return {
        "mensagem": "Horario atualizado"
    }

@router.put("/block/{weekday}")
def block_weekday(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    block_weekday_service(session=session, weekday=weekday, user_id=current_user.id)

    return {
        "mensagem": "Horario bloqueado"
    }

@router.put("/active/{weekday}")
def active_weekday(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    active_weekday_service(session=session, weekday=weekday, user_id=current_user.id)

    return {
        "mensagem": "Horario liberado"
    }