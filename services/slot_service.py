from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from core.config import settings
from core.database import get_session
from fastapi import HTTPException, Depends
from models import Slot, User, WorkSchedule, SlotStatus, UserRole, UserService
from zoneinfo import ZoneInfo
from math import ceil
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


def generate_user_slots(session: Session, user:User):

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

    slots = session.query(Slot).filter(Slot.user_id == user_id, Slot.status == SlotStatus.FREE).order_by(Slot.date_time_init).all()
    
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

def get_available_start_times(service_id, user_id, session):

    service = (session.query(UserService).filter(UserService.service_id == service_id, UserService.user_id == user_id).first())

    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    required_slots = ceil(service.custom_duration / 15)
    free_slots = get_user_free_slots(session, user_id)
    max_index = len(free_slots) - required_slots + 1
    available_times = []

    for index in range(max_index):

        start_time = free_slots[index].date_time_init
        sequence_valid = True

        for step in range(1, required_slots):

            expected_time = start_time + timedelta(minutes=15 * step)
            next_time = free_slots[index + step].date_time_init

            if next_time != expected_time:
                sequence_valid = False
                break

        if sequence_valid:
            available_times.append(start_time)

    return available_times

    # service = session.query(UserService).filter(UserService.service_id==service_id, UserService.user_id==user_id).first()

    # if not service:
    #     raise HTTPException(status_code=404, detail="Nao encontrado")
    
    # amount_slots = ceil(service.custom_duration / 15)
    # print(amount_slots)
    # slots_free = get_user_free_slots(session, user_id)
    # max_index = len(slots_free)-(amount_slots-1)  # evita index overflow ao verificar os próximos slots
    # counter = 0
    # time_free = []

    # while counter < max_index:
    #     index=counter
    #     start_time = slots_free[index].date_time_init 
    #     matching_slots = 0
        
    #     for aux in range(1,amount_slots):
    #         if start_time == (slots_free[index+aux].date_time_init - timedelta(minutes=(15*aux))):
    #             matching_slots+=1
    #         if matching_slots==amount_slots-1:
    #             print(start_time)
    #             time_free.append(start_time)
      
    #     counter +=1
    # return time_free

        # if start_time == (slots_free[index+1].date_time_init - timedelta(minutes=15)) and start_time == (slots_free[index+2].date_time_init - timedelta(minutes=30)) :
        #     print(start_time)