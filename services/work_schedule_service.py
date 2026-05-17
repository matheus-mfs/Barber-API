from fastapi import HTTPException
from models import WorkSchedule

def get_work_schedule_by_weekday(session, weekday, user_id):

    work_schedule = session.query(WorkSchedule).filter(WorkSchedule.weekday == weekday, WorkSchedule.user_id == user_id).first()

    if not work_schedule:
        raise HTTPException(status_code=404,detail="Nenhum horario cadastrado")

    return work_schedule

def create_work_schedule_service(session, current_user, weekday, work_schedule_schema):

    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday == weekday, WorkSchedule.user_id == current_user.id).first()
    
    if weekday_search:
        raise HTTPException(status_code=403, detail="Dia da semana ja cadastrado")

    work_schedule = WorkSchedule(current_user.id, weekday, work_schedule_schema.work_start, work_schedule_schema.work_end,
                                 work_schedule_schema.lunch_start, work_schedule_schema.lunch_end, work_schedule_schema.is_working)

    session.add(work_schedule)
    session.commit()

    return work_schedule

def list_work_schedules_service(session, user_id):

    work_schedules = session.query(WorkSchedule).filter(WorkSchedule.user_id == user_id).all()

    if not work_schedules:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")

    return work_schedules

def update_work_schedule_service(session, weekday, user_id, work_schedule_schema):

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user_id)

    work_schedule.work_start = work_schedule_schema.work_start
    work_schedule.work_end = work_schedule_schema.work_end
    work_schedule.lunch_start = work_schedule_schema.lunch_start
    work_schedule.lunch_end = work_schedule_schema.lunch_end

    session.commit()

def block_weekday_service(session, weekday, user_id):

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user_id)

    work_schedule.is_working = False

    session.commit()

def active_weekday_service(session, weekday, user_id):

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user_id)

    work_schedule.is_working = True

    session.commit()