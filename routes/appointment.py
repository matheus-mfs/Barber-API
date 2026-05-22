from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import User, Tenant
from schemas import AppointmentSchemas
from services.appointment_service import (
    post_create_appointment,
    get_list_appointment,
    get_today_appointment,
    get_search_appointment_id,
    put_cancel_appointment
)

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/create", status_code=201)
def create_appointment(appointment_schemas: AppointmentSchemas, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    appointment = post_create_appointment(appointment_schemas, current_tenant.id, session)
    return{
            "id": appointment.id,
            "status": appointment.status
    }
    
@router.get("/list")
def list_appointment(current_user:User = Depends(check_token), session:Session = Depends(get_session)):
    
    return get_list_appointment(current_user.id, session)
    
@router.get("/today")
def today_appointment(current_user:User = Depends(check_token), session:Session = Depends(get_session)):
    
    return get_today_appointment(current_user.id, session)

@router.get("/{id_appointment}")
def search_appointment(id_appointment:int, current_user:User = Depends(check_token), session:Session = Depends(get_session)):
    
    return get_search_appointment_id(id_appointment, current_user.id, session)

@router.put("/cancel/{id_appointment}")
def cancel_appointment(id_appointment:int, current_user:User = Depends(check_token), session:Session = Depends(get_session)):
    
    appointment = put_cancel_appointment(id_appointment, current_user.id, session)
    return{
            "id": appointment.id,
            "status": appointment.status
    }
    