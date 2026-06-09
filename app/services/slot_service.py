from datetime import date, datetime, timedelta
from math import ceil
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app.core.database import Session
from app.core.config import settings
from app.core.database import get_session
from app.models import Slot, SlotStatus, User, UserService, WorkSchedule
from app.models.permission import PermissionRole
from app.schemas.slot_schema import SlotBlockSchema
from app.services.appointment_service import get_list_appointment, put_cancel_appointment, find_appointments_in_period
from app.services.permission_service import check_permission_user

time_zone: ZoneInfo = ZoneInfo(settings.TIME_ZONE)

WEEKDAYS_MAPPING: Dict[int, str] = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def get_user_free_slots(
        session: Session,  # type: ignore
        user_id: int, 
        status:SlotStatus
) -> List[Slot]:
    """Obtém todos os slots livres de um barbeiro.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do barbeiro
        status: Status que quer procurar

    Returns:
        List[Slot]: Lista de slots livres
        
    """
    slots = session.query(Slot).filter(
        Slot.user_id == user_id, Slot.status == status
    ).order_by(Slot.date_time_init).all()
    
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")

    return slots

def get_available_start_times(
        service_id: int, 
        user_id: int, 
        tenant_id:int, 
        session: Session # type: ignore
) -> List[datetime]:
    """Obtém os horários disponíveis para um serviço.
    
    Args:
        service_id: ID do serviço
        user_id: ID do barbeiro
        tenant_id: ID do tenant
        session: Sessão do banco de dados
        
    Returns:
        List[datetime]: Lista de horários de início disponíveis
        
    """
    
    service = session.query(UserService).filter(
        UserService.service_id == service_id, 
        UserService.user_id == user_id,
        UserService.tenant_id == tenant_id
    ).first()
    
    if not service:
        
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    required_slots: int = ceil(service.custom_duration / 15)
    free_slots: List[Slot] = get_user_free_slots(session, user_id, SlotStatus.FREE)
    max_index: int = len(free_slots) - required_slots + 1
    available_times: List[datetime] = []

    for index in range(max_index):
        start_time: datetime = free_slots[index].date_time_init
        sequence_valid: bool = True

        for step in range(1, required_slots):
            expected_time: datetime = start_time + timedelta(minutes=15 * step)
            next_time: datetime = free_slots[index + step].date_time_init

            if next_time != expected_time:
                sequence_valid = False
                break

        if sequence_valid:
            available_times.append(start_time)

    return available_times

def block_slots(
        session: Session, # type: ignore 
        current_user: User, 
        slot_block_schema: SlotBlockSchema, 
) -> List[Slot]:
    """Bloqueia slots em um período de tempo.
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuario logado
        slot_block_schema: Schema com dados do bloqueio
        
    Returns:
        List[Slot]: Lista de slots bloqueados
    """
    
    user_id = check_permission_user(
        slot_block_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_SLOTS, 
        PermissionRole.MANAGE_ALL_SLOTS
    )
    appointments = find_appointments_in_period(user_id, current_user, slot_block_schema.init_block, slot_block_schema.end_block, session)

    for appointment in appointments:
        put_cancel_appointment(user_id, appointment.id, session, current_user)

    slots = (session.query(Slot)
    .filter(Slot.date_time_init.between(slot_block_schema.init_block, slot_block_schema.end_block), 
            Slot.user_id == user_id,
            Slot.status != SlotStatus.BLOCKED
    ).all())

    if not slots:
        raise HTTPException(status_code=404, detail="nada encontrado")

    for slot in slots:
        slot.status = SlotStatus.BLOCKED

    return slots

def generate_daily_slots() -> None:
    """Gera slots para os próximos 30 dias baseado na agenda de trabalho."""
    
    session = Session()
    
    try:
        users = session.query(User).all()
        
        
        for user in users:
            work_schedules = session.query(WorkSchedule).filter(
                WorkSchedule.user_id == user.id
            ).all()

            if not work_schedules:
                print(f"{user.name} nao possui horario cadastrado")
                continue

            slots_to_add: List[Slot] = []

            for day_offset in range(30):
                current_date: date = date.today() + timedelta(days=day_offset)
                current_weekday: Optional[str] = WEEKDAYS_MAPPING.get(
                    current_date.weekday()
                )

                for schedule in work_schedules:
                    if schedule.weekday.value != current_weekday:
                        continue

                    if not schedule.is_working:
                        continue

                    work_start: datetime = datetime.combine(
                        current_date, schedule.work_start
                    )
                    work_end: datetime = datetime.combine(
                        current_date, schedule.work_end
                    )

                    slot_exists = session.query(Slot).filter(
                        Slot.date_time_init == work_start, Slot.user_id == user.id
                    ).first()

                    if slot_exists:
                        continue

                    if schedule.lunch_start is None:
                        while work_start < work_end:
                            slot_init: datetime = work_start
                            work_start += timedelta(minutes=15)
                            new_slot: Slot = Slot(
                                user.tenant_id, user.id, slot_init, work_start, "FREE"
                            )
                            slots_to_add.append(new_slot)
                    else:
                        lunch_start: datetime = datetime.combine(
                            current_date, schedule.lunch_start
                        )
                        lunch_end: datetime = datetime.combine(
                            current_date, schedule.lunch_end
                        )

                        while work_start < work_end:
                            if lunch_start <= work_start < lunch_end:
                                work_start += timedelta(minutes=15)
                                continue

                            slot_init: datetime = work_start
                            work_start += timedelta(minutes=15)
                            new_slot: Slot = Slot(
                                user.tenant_id, user.id, slot_init, work_start, "FREE"
                            )
                            slots_to_add.append(new_slot)

            session.add_all(slots_to_add)
        session.commit()
    finally:
        session.close()

def close_expired_slots() -> None:
    """Marca slots expirados como bloqueados."""

    session = Session()

    try:
        expired_slots = session.query(Slot).filter(
            Slot.date_time_init < datetime.now(time_zone), Slot.status == SlotStatus.FREE
        ).all()
        
        for slot in expired_slots:
            print(slot.status)
            slot.status = SlotStatus.BLOCKED

        session.commit()    
    finally:
        session.close()

