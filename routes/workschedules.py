from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.models import User, Weekdays
from app.schemas.work_schedule import WorkScheduleSchema, WorkScheduleEditSchema
from app.services.work_schedule_service import (
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

    ws = create_work_schedule_service(session=session, current_user=current_user, weekday=weekday, work_schedule_schema=work_schedule_schema)
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

@router.get("/list")
def list_work_schedules(current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    schedules = list_work_schedules_service(session=session, user_id=current_user.id)
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

@router.get("/search/{weekday}")
def search_work_schedule(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    ws = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=current_user.id)
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

@router.put("/edit/{weekday}")
def edit_work_schedule(weekday: Weekdays, work_schedule_schema: WorkScheduleEditSchema, 
                       current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    ws = update_work_schedule_service(session=session, weekday=weekday, 
                                 user_id=current_user.id, work_schedule_schema=work_schedule_schema)
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

@router.put("/block/{weekday}")
def block_weekday(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    work_schedule = block_weekday_service(session=session, weekday=weekday, user_id=current_user.id)
    return {
        "weekday": work_schedule.weekday,
        "is_working": work_schedule.is_working,
        "status": work_schedule.is_working
    }

@router.put("/active/{weekday}")
def active_weekday(weekday: Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    work_schedule = active_weekday_service(session, weekday, current_user)
    return {
        "weekday": work_schedule.weekday,
        "is_working": work_schedule.is_working,
        "status": work_schedule.is_working
    }