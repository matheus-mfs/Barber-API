from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.schedule import WorkSchedule
from app.models.slot import Slot, SlotStatus
from app.models.permission import PermissionRole
from app.models.user import User
from app.schemas.work_schedule import WorkScheduleSchema, WorkScheduleStatusSchema, WorkScheduleEditSchema
from app.services.permission_service import check_permission_user
from app.services.slot_service import generate_user_slots, get_user_free_slots
from app.services.user_service import get_user_by_id


weekdays = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}


def get_work_schedule_by_weekday(
        session: Session, 
        weekday: str, 
        user_id: Optional[int] = None,
) -> Optional[WorkSchedule]:
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


def create_work_schedule_service(
        session: Session, 
        current_user: User, 
        work_schedule_schema=WorkScheduleSchema,
) -> WorkSchedule:
    """Cria um novo horário de trabalho para o dia da semana e usuário especificados.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        current_user: O ID do usuário atual que está criando o horário de trabalho
        weekday: O dia da semana para criar o horário de trabalho (ex: "monday")
        work_schedule_schema: Schema contendo os detalhes do horário de trabalho

    Returns:
        O objeto WorkSchedule criado
    """

    user_id = check_permission_user(
        work_schedule_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_WORKSCHEDULE, 
        PermissionRole.MANAGE_ALL_WORKSCHEDULES
    )
    weekday_search = (session.query(WorkSchedule)
                      .filter(WorkSchedule.weekday==work_schedule_schema.weekday,
                              WorkSchedule.user_id==user_id).first()
    )
    if weekday_search:
        raise HTTPException(status_code=403, detail="Dia da semana ja cadastrado")

    work_schedule = WorkSchedule(
        current_user.tenant_id,
        user_id, 
        work_schedule_schema.weekday, 
        work_schedule_schema.work_start, 
        work_schedule_schema.work_end,
        work_schedule_schema.lunch_start, 
        work_schedule_schema.lunch_end, 
        work_schedule_schema.is_working
    )

    session.add(work_schedule)
    session.commit()

    return work_schedule


def list_work_schedules_service(
        session: Session, 
        user_id: int
) -> List[WorkSchedule]:
    """Recupera todos os horários de trabalho do usuário especificado.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        user_id: O ID do usuário cujos horários de trabalho serão recuperados

    Return:
        Lista de objetos WorkSchedule se encontrados, caso contrário lança HTTPException
    """
    print("oi")
    work_schedules = session.query(WorkSchedule).filter(WorkSchedule.user_id == user_id).all()

    if not work_schedules:
        raise HTTPException(status_code=404, detail="Nenhum horario cadastrado")

    return work_schedules

def update_work_schedule_service(
        session: Session, 
        current_user: User, 
        work_schedule_schema: WorkScheduleEditSchema,
) -> WorkSchedule:
    """Atualiza um horário de trabalho existente para o dia da semana e usuário especificados.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para atualizar o horário de trabalho (ex: "monday")
        user_id: O ID do usuário cujo horário de trabalho será atualizado
        work_schedule_schema: Schema contendo os detalhes atualizados do horário de trabalho
    
    Return:
        O objeto WorkSchedule atualizado
    """
    
    user_id = check_permission_user(
        work_schedule_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_WORKSCHEDULE, 
        PermissionRole.MANAGE_ALL_WORKSCHEDULES
    )

    work_schedule = get_work_schedule_by_weekday(
        session, 
        work_schedule_schema.weekday,  
        user_id
    )

    work_schedule.work_start = work_schedule_schema.work_start
    work_schedule.work_end = work_schedule_schema.work_end
    work_schedule.lunch_start = work_schedule_schema.lunch_start
    work_schedule.lunch_end = work_schedule_schema.lunch_end

    session.commit()
    return work_schedule


def status_weekday_service(
        session: Session, 
        current_user: User,
        work_schedule_status_schema: WorkScheduleStatusSchema,
) -> WorkSchedule:
    """Ativa um dia da semana específico para o usuário e gera os slots do usuário.

    Args:
        session: Sessão do banco de dados SQLAlchemy
        weekday: O dia da semana para ativar (ex: "monday")
        user: Objeto do usuário cujo horário de trabalho será ativado
    
    Return: 
        O objeto WorkSchedule atualizado
    """
    
    user_id = check_permission_user(
        work_schedule_status_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_WORKSCHEDULE, 
        PermissionRole.MANAGE_ALL_WORKSCHEDULES
    )

    work_schedule = get_work_schedule_by_weekday(
        session, 
        work_schedule_status_schema.weekday, 
        user_id
    )

    if work_schedule.is_working:
        
        work_schedule.is_working = False
        
        slots = get_user_free_slots(session, user_id, SlotStatus.FREE)
        
        if not slots:
            session.commit()
            return work_schedule
        print("apagar 2")
        for slot in slots:
            date_slot = (slot.date_time_init.date())
            weekday_slot = weekdays.get(date_slot.weekday())
            if weekday_slot == work_schedule_status_schema.weekday.value:
                session.delete(slot)
        
    else:
        
        work_schedule.is_working = True
        user = get_user_by_id(session, user_id, current_user.tenant_id)
        generate_user_slots(session, user)
    
    session.commit()
    return work_schedule