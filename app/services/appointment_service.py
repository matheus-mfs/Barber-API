from datetime import datetime, timedelta
from math import ceil
from typing import Any, List, Optional
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
from app.core.config import settings
from app.core.dependencies import permission_required
from app.models import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    Slot,
    SlotStatus,
    UserService,
)
from app.models.client import Client
from app.models.permission import PermissionRole
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.appointment_schema import AppointmentSchemas
from app.services.permission_service import check_permission_user
from app.services.whatsapp_service import send_message

time_zone: ZoneInfo = ZoneInfo(settings.TIME_ZONE)


def post_create_appointment(
        appointment_schemas: AppointmentSchemas, 
        tenant_id: int, 
        session: Session
) -> Appointment:
    """Cria um novo agendamento e marca os slots como reservados.
    
    Args:
        appointment_schemas: Schema com dados do agendamento
        tenant_id: ID do tenant
        session: Sessão do banco de dados
        
    Returns:
        Appointment: Agendamento criado
        
    """
    
    user_service: Optional[UserService] = (session.query(UserService)
        .filter(UserService.id == appointment_schemas.user_service_id).first()
    )
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    end_time: datetime = appointment_schemas.start_time + timedelta(minutes=user_service.custom_duration)
    notify_at: datetime = appointment_schemas.start_time - timedelta(hours=1)

    appointment: Appointment = Appointment(
        tenant_id,
        appointment_schemas.client_id,
        appointment_schemas.user_service_id,
        appointment_schemas.start_time,
        end_time,
        notify_at,        
        
    )
    
    session.add(appointment)
    session.flush()

    post_create_appointment_slot(user_service.custom_duration, appointment.start_time, session, appointment)

    return appointment

def post_create_appointment_slot(duration_service:int, start_time:datetime, session:Session, appointment:Appointment):
    slots: List[AppointmentSlot] = []

    required_slots: int = ceil(duration_service / 15)

    user_service = (session.query(UserService)
                    .filter(UserService.id == appointment.user_service_id).first()
        )
    
    for step in range(required_slots):
        slot_time: datetime = start_time + timedelta(
            minutes=15 * step
        )
        slot: Optional[Slot] = session.query(Slot).filter(
            Slot.user_id == user_service.user_id,
            Slot.date_time_init == slot_time,
        ).first()
        
        if not slot:
            raise HTTPException(status_code=404, detail="Horário não encontrado")
        
        slot.status = SlotStatus.BOOKED
        appointment_slot: AppointmentSlot = AppointmentSlot(appointment.id, slot.id)
        slots.append(appointment_slot)

    session.add_all(slots)

    session.commit()
    

def get_list_appointment(
        current_user: User, 
        session: Session, 
        user_id: Optional[int] = None
) -> List[Appointment]:
    """Lista todos os agendamentos de um barbeiro.
    
    Args:
        current_user: Usuario logado
        session: Sessão do banco de dados
        user_id: ID do barbeiro

    Returns:
        List[Appointment]: Lista de agendamentos
        
    """
    
    user_id = check_permission_user(
        user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_APPOINTMENTS, 
        PermissionRole.MANAGE_ALL_APPOINTMENTS
    )

    appointments: List[Appointment] = (session.query(Appointment)
        .join(UserService, Appointment.user_service_id == UserService.id)
        .filter(UserService.user_id == user_id)
        .all()
    )
    
    if not appointments:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointments

def get_today_appointment(
        current_user: User, 
        session: Session, 
        user_id: Optional[int] = None
) -> List[Appointment]:
    """Lista agendamentos de hoje de um barbeiro.
    
    Args:
        current_user: Usuario logado
        session: Sessão do banco de dados
        user_id: ID do barbeiro
        
    Returns:
        List[Appointment]: Lista de agendamentos de hoje
        
    """
    
    user_id = check_permission_user(
        user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_APPOINTMENTS, 
        PermissionRole.MANAGE_ALL_APPOINTMENTS
    )

    today: Any = datetime.now(time_zone).date()
    
    appointments: List[Appointment] = (
        session.query(Appointment)
        .join(UserService, Appointment.user_service_id == UserService.id)
        .filter(
            UserService.user_id == user_id,
            func.date(Appointment.start_time) == today).all()
    )

    if not appointments:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointments

def get_search_appointment_id(
        appointment_id: int, 
        session: Session,
        tenant_id: int
) -> Appointment:
    """Busca um agendamento específico.
    
    Args:
        appointment_id: ID do agendamento
        session: Sessão do banco de dados
        current_user: Usuario logado

    Returns:
        Appointment: Agendamento encontrado
        
    """

    appointment = session.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == tenant_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    return appointment

def put_cancel_appointment(
        user_id:int,
        appointment_id: int, 
        session: Session, 
        current_user: User
) -> Appointment:
    """Cancela um agendamento.
    
    Args:
        user_id: ID do usuario
        appointment_id: ID do agendamento
        session: Sessão do banco de dados
        current_user: Usuario logado

    Returns:
        Appointment: Agendamento cancelado

    """
    
    user_id = check_permission_user(
        user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_APPOINTMENTS, 
        PermissionRole.MANAGE_ALL_APPOINTMENTS
    )

    appointment = (
        session.query(Appointment)
        .join(UserService, Appointment.user_service_id == UserService.id)
        .filter(
            Appointment.id == appointment_id,
            Appointment.tenant_id == current_user.tenant_id,
            UserService.user_id == user_id
        )
        .first()
    )
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    
    appointment.status = AppointmentStatus.CANCELLED

    client = session.query(Client).filter(Client.id==appointment.client_id).first()
    tenant = session.query(Tenant).filter(Tenant.id==appointment.tenant_id).first()
    number_client = client.telephone
    message = f"""Olá, {client.name}.
    
Infelizmente, por um imprevisto, precisaremos cancelar seu horário agendado para {appointment.start_time.date()} ás {appointment.start_time.time()}.

Pedimos desculpas pelo transtorno e estamos à disposição para reagendar em um novo horário que seja conveniente para você.

Entre em contato conosco para escolher uma nova data, ou aguarde que retornaremos com opções disponíveis.

Agradecemos pela compreensão e esperamos atendê-lo em breve.

Atenciosamente,

{tenant.name} ✂️
    """

    send_message(number_client, message)

    
    #session.commit()

    return appointment

def find_appointments_in_period(
        user_id:int,
        current_user:User, 
        init_block: datetime, 
        end_block: datetime, 
        session:Session # type: ignore
) -> List[Appointment]:
    """Buscar agendamentos em um periodo
    
    Args:
        user_id: ID do usuario
        current_user: Usuario logado
        init_block: data e horario de inicio da busca
        end_block: data e horario do fim da busca
        session: Sessão do Banco de dados
    
    Return:
        List[Appointment]: Lista de agendamentos encontrados
    """
    
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    list_appointment = get_list_appointment(current_user, session, user_id)

    appointments: list = []
    for appointment in list_appointment:
        if appointment.start_time > init_block and appointment.start_time < end_block:
            print(appointment.client_id)
            appointments.append(appointment)

    return appointments

def reschedule_appointment(        
        id_appointment: int, 
        new_start_time: datetime, 
        session: Session,
        tenant_id: int
) -> Appointment:
    
    appointment = get_search_appointment_id(id_appointment, session, tenant_id) 

    
    duration_service = int((appointment.end_time - appointment.start_time).total_seconds() /60)
    new_end_time = new_start_time + timedelta(minutes=duration_service)
    
    appointment.start_time = new_start_time
    appointment.end_time = new_end_time
    
    appointment_slots = (
        session.query(AppointmentSlot)
            .filter(AppointmentSlot.appointment_id == id_appointment).all()
    )

    if not appointment_slots:
        raise HTTPException(status_code=404, detail="erro")
    
    for a_s in appointment_slots:
        session.delete(a_s)
    
    session.flush()
    post_create_appointment_slot(duration_service, new_start_time, session, appointment)
    
    return appointment


