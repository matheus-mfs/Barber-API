from datetime import date, datetime, timedelta
from math import ceil
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.models import Slot, SlotStatus, User, UserService, WorkSchedule

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


def get_user_free_slots(session: Session, user_id: int) -> List[Slot]:
    """Obtém todos os slots livres de um barbeiro.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do barbeiro
        
    Returns:
        List[Slot]: Lista de slots livres
        
    Raises:
        HTTPException: Se nenhum slot livre for encontrado
    """
    slots = session.query(Slot).filter(
        Slot.user_id == user_id, Slot.status == SlotStatus.FREE
    ).order_by(Slot.date_time_init).all()
    
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")

    return slots


def get_available_start_times(service_id: int, user_id: int, session: Session) -> List[datetime]:
    """Obtém os horários disponíveis para um serviço.
    
    Args:
        service_id: ID do serviço
        user_id: ID do barbeiro
        session: Sessão do banco de dados
        
    Returns:
        List[datetime]: Lista de horários de início disponíveis
        
    Raises:
        HTTPException: Se o serviço não for encontrado
    """
    
    service = session.query(UserService).filter(
        UserService.service_id == service_id, UserService.user_id == user_id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    required_slots: int = ceil(service.custom_duration / 15)
    free_slots: List[Slot] = get_user_free_slots(session, user_id)
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


def block_slots(session: Session, user_id: int, init_block: datetime, end_block: datetime) -> List[Slot]:
    """Bloqueia slots em um período de tempo.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do barbeiro
        init_block: Horário de início do bloqueio
        end_block: Horário de término do bloqueio
        
    Returns:
        List[Slot]: Lista de slots bloqueados
    """
    
    current_time: datetime = init_block
    blocked_slots: List[Slot] = []
    
    while current_time < end_block:
        slot = session.query(Slot).filter(
            Slot.date_time_init == current_time, Slot.user_id == user_id
        ).first()
        
        if slot:
            slot.status = SlotStatus.BLOCKED
            blocked_slots.append(slot)
        
        current_time += timedelta(minutes=15)

    session.commit()
    
    return blocked_slots

def generate_user_slots(session: Session, user: User) -> None:
    """Gera slots para os próximos 30 dias baseado na agenda de trabalho.
    
    Args:
        session: Sessão do banco de dados
        user: Usuário barbeiro
        
    Raises:
        HTTPException: Se nenhuma agenda de trabalho for encontrada
    """
    
    work_schedules = session.query(WorkSchedule).filter(
        WorkSchedule.user_id == user.id
    ).all()

    if not work_schedules:
        raise HTTPException(
            status_code=404, detail="Horario de trabalho nao encontrado"
        )

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

def complete_expired_slots(session: Session) -> None:
    """Marca slots expirados como bloqueados.
    
    Args:
        session: Sessão do banco de dados
    """
    
    expired_slots = session.query(Slot).filter(
        Slot.date_time_init < datetime.now(time_zone), Slot.status == SlotStatus.FREE
    ).all()
    
    for slot in expired_slots:
        slot.status = SlotStatus.BLOCKED

    session.commit()


def get_user_slots(session: Session, user_id: int) -> List[Slot]:
    """Obtém todos os slots de um barbeiro.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do barbeiro
        
    Returns:
        List[Slot]: Lista de slots
        
    Raises:
        HTTPException: Se nenhum slot for encontrado
    """
    
    slots= session.query(Slot).filter(
        Slot.user_id == user_id
    ).all()
    
    if not slots:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")

    return slots


def get_barber_free_slots(session: Session, current_user: User, user_id: int) -> List[Slot]:
    """Obtém slots livres de um barbeiro.
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        user_id: ID do barbeiro
        
    Returns:
        List[Slot]: Lista de slots livres
        
    Raises:
        HTTPException: Se nenhum slot livre for encontrado
    """
    
    slots= session.query(Slot).filter(
        Slot.user_id == user_id, Slot.status == SlotStatus.FREE
    ).all()
    
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")

    return slots

