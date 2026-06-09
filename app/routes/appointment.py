from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models import User, Tenant, PermissionRole
from app.schemas.appointment_schema import AppointmentSchemas
from app.services.appointment_service import (
    find_appointments_in_period,
    post_create_appointment,
    get_list_appointment,
    get_today_appointment,
    get_search_appointment_id,
    put_cancel_appointment
)

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/create")
def create_appointment(
    appointment_schemas: AppointmentSchemas, 
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant)
)  -> dict[str, Any]:
    """Criar agendamento"""
    appointment = post_create_appointment(appointment_schemas, current_tenant.id, session)
    return{
            "id": appointment.id,
            "status": appointment.status,
            "client": appointment.client_id,
            "tenant": appointment.tenant_id,
            "service": appointment.user_service_id,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time
    }
    
@router.get("/list")
def list_appointment(
    user_id: Optional[int] = None,
    current_user:User = Depends(check_token), 
    session:Session = Depends(get_session)
) -> List[dict[str, Any]]:
    """Listar Agendamentos"""

    appointments = get_list_appointment(current_user, session, user_id)
    return[
            {
            "id": appointment.id,
            "status": appointment.status,
            "client": appointment.client_id,
            "tenant": appointment.tenant_id,
            "service": appointment.user_service_id,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time
            }for appointment in appointments   
    ]

@router.get("/today")
def today_appointment(
    user_id: Optional[int] = None,
    current_user:User = Depends(check_token), 
    session:Session = Depends(get_session)
) -> List[dict[str, Any]]:
    """Listar agendamento do dia"""
    appointments = get_today_appointment(current_user, session, user_id)
    return[
            {
            "id": appointment.id,
            "status": appointment.status,
            "client": appointment.client_id,
            "tenant": appointment.tenant_id,
            "service": appointment.user_service_id,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time
            }for appointment in appointments   
    ]

@router.get("/{id_appointment}")
def search_appointment(
    id_appointment:int,
    current_user:User = Depends(check_token),
    session:Session = Depends(get_session)
) -> dict[str, Any]:
    """Buscar Agendamentos"""
    appointment = get_search_appointment_id(id_appointment, session, current_user)
    return{
            "id": appointment.id,
            "status": appointment.status,
            "client": appointment.client_id,
            "tenant": appointment.tenant_id,
            "service": appointment.user_service_id,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time
    }

@router.get("/user/{user_id}/init_block/{init_block}/end_block{end_block}")
def get_appointments_in_period(
    user_id:int,
    init_block: datetime,
    end_block: datetime, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(check_token)
):
    """Buscar agendamentos em um periodo"""

    return find_appointments_in_period(user_id, current_user, init_block, end_block, session)

@router.put("/cancel/{id_appointment}")
def cancel_appointment(
    user_id:int,
    id_appointment:int, 
    current_user:User = Depends(check_token),
    session:Session = Depends(get_session)
) -> dict[str, Any]:
    """Cancelar agendamento"""
    appointment = put_cancel_appointment(user_id, id_appointment, session, current_user)
    return{
            "id": appointment.id,
            "status": appointment.status,
            "client": appointment.client_id,
            "tenant": appointment.tenant_id,
            "service": appointment.user_service_id,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time
    }