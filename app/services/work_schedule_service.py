from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import WorkSchedule, Slot
from app.services.slot_service import generate_user_slots


weekdays = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}


def get_work_schedule_by_weekday(session: Session, weekday: str, user_id: int) -> Optional[WorkSchedule]:
    """Recupera um horário de trabalho pelo dia da semana e ID do usuário.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para recuperar o horário de trabalho (ex: "monday")
        user_id: O ID do usuário cujo horário de trabalho será recuperado

    Return:
        Objeto WorkSchedule se encontrado, caso contrário None
    """

    work_schedule = session.query(WorkSchedule).filter(WorkSchedule.weekday == weekday, WorkSchedule.user_id == user_id).first()

    if not work_schedule:
        raise HTTPException(status_code=404,detail="Nenhum horario cadastrado")

    return work_schedule

def create_work_schedule_service(session: Session, current_user: int, weekday: str, work_schedule_schema) -> WorkSchedule:
    """Cria um novo horário de trabalho para o dia da semana e usuário especificados.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        current_user: O ID do usuário atual que está criando o horário de trabalho
        weekday: O dia da semana para criar o horário de trabalho (ex: "monday")
        work_schedule_schema: Schema contendo os detalhes do horário de trabalho

    Returns:
        O objeto WorkSchedule criado
    """

    weekday_search = session.query(WorkSchedule).filter(WorkSchedule.weekday == weekday, WorkSchedule.user_id == current_user.id).first()
    
    if weekday_search:
        raise HTTPException(status_code=403, detail="Dia da semana ja cadastrado")

    work_schedule = WorkSchedule(current_user.id, weekday, work_schedule_schema.work_start, work_schedule_schema.work_end,
                                 work_schedule_schema.lunch_start, work_schedule_schema.lunch_end, work_schedule_schema.is_working)

    session.add(work_schedule)
    session.commit()

    return work_schedule

def list_work_schedules_service(session: Session, user_id: int) -> List[WorkSchedule]:
    """Recupera todos os horários de trabalho do usuário especificado.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        user_id: O ID do usuário cujos horários de trabalho serão recuperados

    Return:
        Lista de objetos WorkSchedule se encontrados, caso contrário lança HTTPException
    """

    work_schedules = session.query(WorkSchedule).filter(WorkSchedule.user_id == user_id).all()

    if not work_schedules:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")

    return work_schedules

def update_work_schedule_service(session: Session, weekday: str, user_id: int, work_schedule_schema) -> WorkSchedule:
    """Atualiza um horário de trabalho existente para o dia da semana e usuário especificados.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para atualizar o horário de trabalho (ex: "monday")
        user_id: O ID do usuário cujo horário de trabalho será atualizado
        work_schedule_schema: Schema contendo os detalhes atualizados do horário de trabalho
    
    Return:
        O objeto WorkSchedule atualizado
    """

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user_id)

    work_schedule.work_start = work_schedule_schema.work_start
    work_schedule.work_end = work_schedule_schema.work_end
    work_schedule.lunch_start = work_schedule_schema.lunch_start
    work_schedule.lunch_end = work_schedule_schema.lunch_end

    session.commit()
    return work_schedule

def block_weekday_service(session: Session, weekday: str, user_id: int) -> WorkSchedule:
    """Bloqueia um dia da semana específico para o usuário e remove os slots relacionados.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para desativar (ex: "monday")
        user: Objeto do usuário cujo horário de trabalho será desativado
    
    Return: 
        O objeto WorkSchedule atualizado
    """

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user_id)
    work_schedule.is_working = False
    
    slots = session.query(Slot).filter(Slot.user_id == user_id).all()

    for slot in slots:
        date_slot = (slot.date_time_init.date())
        weekday_slot = weekdays.get(date_slot.weekday())
        if weekday_slot == weekday.value:
            session.delete(slot)

    session.commit()
    return work_schedule

def active_weekday_service(session: Session, weekday: str, user) -> WorkSchedule:
    """Ativa um dia da semana específico para o usuário e gera os slots do usuário.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para ativar (ex: "monday")
        user: Objeto do usuário cujo horário de trabalho será ativado
    
    Return: 
        O objeto WorkSchedule atualizado
    """

    work_schedule = get_work_schedule_by_weekday(session=session, weekday=weekday, user_id=user.id)
    work_schedule.is_working = True

    generate_user_slots(session, user)
    return work_schedule