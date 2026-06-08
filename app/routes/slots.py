from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models import User
from app.models.tenant import Tenant
from app.schemas.slot_schema import SlotBlockSchema
from app.services.slot_service import (
    block_slots, 
    generate_user_slots, 
    complete_expired_slots, 
    get_available_start_times
)

router = APIRouter(prefix="/slots", tags=["slots"])

@router.get("/availability/service/{service_id}/user/{user_id}")
def availability_slots(
    service_id:int, 
    user_id:int, 
    session:Session = Depends(get_session),
    current_tenant:Tenant = Depends(get_tenant)
):
    
    availability = get_available_start_times(service_id, user_id, current_tenant.id, session)
    return [
            {
                "Start_time":a
        }for a in availability
    ]

@router.put("/block")
def block_slot(
    slot_block_schema: SlotBlockSchema, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(check_token)
):
    
    time_block = block_slots(session, current_user, slot_block_schema)
    
    return [
            {
                "horario_block":  block.date_time_init
        }for block in time_block
    ]

# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.post("/generate")
def generate_slots(session: Session = Depends(get_session),current_user: User = Depends(check_token)):
    
    generate_user_slots(session, current_user)
    return {
        "message": "Slots gerados com sucesso"
    }

# Converter essa rota para def, e automatizar para ela finalizar slots para todos os Barber/Admin-Barber nao apenas 1
@router.post("/complet")
def finaly_slots(session: Session = Depends(get_session)):

    complete_expired_slots(session)
    return {
        "message": "Slots atualizados"
    }




