from datetime import datetime, timedelta
from math import ceil
from typing import Any, List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.models import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    Slot,
    SlotStatus,
    User,
    UserService,
)

time_zone: ZoneInfo = ZoneInfo(settings.TIME_ZONE)


def post_create_appointment(appointment_schemas: Any, tenant_id: int, session: Session) -> Appointment:
    """Cria um novo agendamento e marca os slots como reservados.
    
    Args:
        appointment_schemas: Schema com dados do agendamento
        tenant_id: ID do tenant
        session: Sessão do banco de dados
        
    Returns:
        Appointment: Agendamento criado
        
    Raises:
        HTTPException: Se o serviço ou slots não forem encontrados
    """
    
    user_service: Optional[UserService] = session.query(UserService).filter(
        UserService.id == appointment_schemas.user_service_id
    ).first()
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    end_time: datetime = appointment_schemas.start_time + timedelta(
        minutes=user_service.custom_duration
    )
    
    appointment: Appointment = Appointment(
        tenant_id,
        appointment_schemas.client_id,
        appointment_schemas.user_service_id,
        appointment_schemas.start_time,
        end_time,
        appointment_schemas.status,
    )
    
    session.add(appointment)
    session.flush()

    required_slots: int = ceil(user_service.custom_duration / 15)
    slots: List[AppointmentSlot] = []
    
    for step in range(required_slots):
        slot_time: datetime = appointment_schemas.start_time + timedelta(
            minutes=15 * step
        )
        slot: Optional[Slot] = session.query(Slot).filter(
            Slot.user_id == user_service.user_id,
            Slot.date_time_init == slot_time,
        ).first()
        
        if not slot:
            raise HTTPException(status_code=404, detail="Horário não encontrado")
        
        slot.status = SlotStatus.BOOKED
        appointment_slot: AppointmentSlot = AppointmentSlot(
            appointment.id, slot.id
        )
        slots.append(appointment_slot)

    session.add_all(slots)
    session.commit()
    
    return appointment

def get_list_appointment(user_id: int, session: Session) -> List[Appointment]:
    """Lista todos os agendamentos de um barbeiro.
    
    Args:
        user_id: ID do barbeiro
        session: Sessão do banco de dados
        
    Returns:
        List[Appointment]: Lista de agendamentos
        
    Raises:
        HTTPException: Se nenhum agendamento for encontrado
    """
    
    appointments: List[Appointment] = (
        session.query(Appointment)
        .join(UserService, Appointment.user_service_id == UserService.id)
        .filter(UserService.user_id == user_id)
        .all()
    )
    
    if not appointments:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointments


def get_today_appointment(user_id: int, session: Session) -> List[Appointment]:
    """Lista agendamentos de hoje de um barbeiro.
    
    Args:
        user_id: ID do barbeiro
        session: Sessão do banco de dados
        
    Returns:
        List[Appointment]: Lista de agendamentos de hoje
        
    Raises:
        HTTPException: Se nenhum agendamento for encontrado
    """
    
    today: Any = datetime.now(time_zone).date()
    
    appointments: List[Appointment] = (
        session.query(Appointment)
        .join(UserService, Appointment.user_service_id == UserService.id)
        .filter(
            UserService.user_id == user_id,
            func.date(Appointment.start_time) == today,
        ).all()
    )

    if not appointments:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointments


def get_search_appointment_id(appointment_id: int, session: Session) -> Appointment:
    """Busca um agendamento específico.
    
    Args:
        appointment_id: ID do agendamento
        session: Sessão do banco de dados
        
    Returns:
        Appointment: Agendamento encontrado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado
    """
    
    appointment = session.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointment


def put_cancel_appointment(appointment_id: int, session: Session) -> Appointment:
    """Cancela um agendamento.
    
    Args:
        appointment_id: ID do agendamento
        session: Sessão do banco de dados
        
    Returns:
        Appointment: Agendamento cancelado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado
    """
    appointment = session.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    appointment.status = AppointmentStatus.CANCELLED
    session.commit()
    
    return appointment
