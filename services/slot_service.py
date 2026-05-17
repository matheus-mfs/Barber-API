from datetime import date, datetime, timedelta
from core.config import settings
from fastapi import HTTPException
from models import Slot, WorkSchedule, SlotStatus, UserRole
from zoneinfo import ZoneInfo
time_zone = ZoneInfo(settings.TIME_ZONE)


weekdays = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}


def generate_user_slots(session, user):

    work_schedule = session.query(WorkSchedule).filter(WorkSchedule.user_id == user.id).all()

    if not work_schedule:
        raise HTTPException(status_code=404, detail="Horario de trabalho nao encontrado")

    slots_to_add = []

    for cont in range(0, 30):

        current_date = date.today() + timedelta(days=cont)
        current_weekday = weekdays.get(current_date.weekday())

        for schedule in work_schedule:
            if schedule.weekday.value != current_weekday:
                continue

            if not schedule.is_working:
                continue

            work_start = datetime.combine(current_date, schedule.work_start)
            work_end = datetime.combine(current_date, schedule.work_end)

            slot_exists = session.query(Slot).filter(Slot.date_time_init == work_start, 
                                                     Slot.user_id == user.id).first()

            if slot_exists:
                continue

            if schedule.lunch_start is None:
                while work_start < work_end:
                    init = work_start
                    work_start += timedelta(minutes=15)
                    slot = Slot(user.tenant_id, user.id, init, work_start,"FREE")
                    slots_to_add.append(slot)
            else:
                lunch_start = datetime.combine(current_date, schedule.lunch_start)
                lunch_end = datetime.combine(current_date, schedule.lunch_end)

                while work_start < work_end:
                    if work_start >= lunch_start and work_start < lunch_end:
                        work_start += timedelta(minutes=15)
                        continue

                    init = work_start
                    work_start += timedelta(minutes=15)
                    slot = Slot(user.tenant_id, user.id, init, work_start, "FREE" )
                    slots_to_add.append(slot)

    session.add_all(slots_to_add)
    session.commit()

def complete_expired_slots(session):

    slots = session.query(Slot).filter(Slot.date_time_init < datetime.now(time_zone),Slot.status == SlotStatus.FREE).all()

    for slot in slots:
        slot.status = SlotStatus.BLOCKED

    session.commit()

def get_user_slots(session, user_id):

    slots = session.query(Slot).filter(Slot.user_id == user_id).all()

    if not slots:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")

    return slots

def get_user_free_slots(session, user_id):

    slots = session.query(Slot).filter(Slot.user_id == user_id,Slot.status == SlotStatus.FREE).all()
    
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")

    return slots

def get_barber_free_slots(session, current_user, user_id):

    if current_user.role == UserRole.BARBER:
        raise HTTPException(status_code=401, detail="Acesso negado")

    slots = session.query(Slot).filter(Slot.user_id == user_id, Slot.status == SlotStatus.FREE).all()

    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")

    return slots

def block_slots(session, user_id, init_block, end_block):

    current_time = init_block

    while current_time < end_block:
        slot = session.query(Slot).filter(Slot.date_time_init == current_time, Slot.user_id == user_id).first()
        if slot:
            slot.status = SlotStatus.BLOCKED
        current_time += timedelta(minutes=15)

    session.commit()