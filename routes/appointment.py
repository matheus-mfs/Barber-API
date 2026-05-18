from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import User, Tenant, Client, Service, Slot, Appointment, AppointmentStatus
from schemas import AppointmentSchemas
from services.appointment_service import (post_create_appointment)


router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/create")
def create_appointment(appointment_schemas: AppointmentSchemas, session: Session = Depends(get_session), 
                       current_tenant: Tenant = Depends(get_tenant)):

    post_create_appointment(appointment_schemas, current_tenant.id, session)
    return{
        "mensagem":"Agendamento confirmado"
    }
    
@router.get("/list")
def list_appointment():
    # TODO: listar todos os agendamentos
    pass

@router.get("/today")
def today_appointment():
    # TODO: agenda do dia
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
