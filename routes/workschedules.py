from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from models import User, WorkSchedule, Weekdays
from schemas import WorkScheduleSchema, WorkScheduleEditSchema

router = APIRouter(prefix="/workschedules", tags=["workschedules"])



@router.post("/create")
def create_works_chedules(weekday:Weekdays, work_schedule_schema:WorkScheduleSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    work_schedule = WorkSchedule(current_user.id, weekday, work_schedule_schema.work_start, 
                                work_schedule_schema.work_end, work_schedule_schema.lunch_start,
                                work_schedule_schema.lunch_end, work_schedule_schema.is_working)
    
    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday==work_schedule_schema.weekday, WorkSchedule.user_id==current_user.id).first()

    if weekday_search:
        raise HTTPException(status_code=403, detail="Dia da semana ja cadastrado")
    
    session.add(work_schedule)
    session.commit()

    return {"mensagem":"Horario cadastrado"}


@router.get("/list")
def list_work_schedules(current_user: User = Depends(check_token), session: Session = Depends(get_session)):

    work_schedules = session.query(WorkSchedule).filter(WorkSchedule.user_id==current_user.id).all()

    if not work_schedules:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")
    
    return work_schedules

@router.get("/search/{weekday}")
def search_work_schedule(weekday:Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday==weekday, WorkSchedule.user_id==current_user.id).first()
    
    if not weekday_search:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")
    
    return weekday_search

@router.put("/edit/{weekday}")
def edit_work_schedule(weekday:Weekdays, work_schedule_schema:WorkScheduleEditSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday==weekday, WorkSchedule.user_id==current_user.id).first()
    
    if not weekday_search:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")
    
    weekday_search.work_start = work_schedule_schema.work_start
    weekday_search.work_end = work_schedule_schema.work_end
    weekday_search.lunch_start = work_schedule_schema.lunch_start
    weekday_search.lunch_end = work_schedule_schema.lunch_end

    session.commit()

    return{"mensagem":"Horario atualizado"}

@router.put("/block/{weekday}")
def block_weekday(weekday:Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday==weekday, WorkSchedule.user_id==current_user.id).first()
    
    if not weekday_search:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")
    
    weekday_search.is_working = False
    
    session.commit()
    return{"mensagem":"Horario Bloqueado"}

@router.put("/active/{weekday}")
def active_weekday(weekday:Weekdays, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday==weekday, WorkSchedule.user_id==current_user.id).first()
    
    if not weekday_search:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")
    
    weekday_search.is_working = True
    
    session.commit()
    return{"mensagem":"Horario Liberado"}