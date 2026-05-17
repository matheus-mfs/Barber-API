from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import User, Tenant, Client, Service, Slot, Appointment, AppointmentStatus
from schemas import AppointmentSchemas


router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/create")
def create_appointment(appointment_schemas: AppointmentSchemas, session: Session = Depends(get_session), 
                       current_tenant: Tenant = Depends(get_tenant)):
    appointment = Appointment(current_tenant.id, appointment_schemas.client_id, appointment_schemas.service_id,
                              appointment_schemas.user_id, appointment_schemas.slot_id, appointment_schemas.status)
    return appointment_schemas

@router.get("/list")
def list_appointment():
    # TODO: listar todos os agendamentos
    pass

@router.get("/today")
def today_appointment():
    # TODO: agenda do dia
    pass

@router.get("/client/{cliente_id}")
def history_appointment(cliente_id: int):
    # TODO: histórico do cliente
    pass

@router.get("/{id}")
def search_appointment(id: int):
    # TODO: buscar agendamento por id
    pass

@router.put("/edit/{id}")
def edit_status_appointment(id: int):
    # TODO: confirmar, cancelar, concluir
    pass

@router.put("/cancel/{id}")
def cancel_appointment(id: int):
    # TODO: cancelar agendamento
    pass
