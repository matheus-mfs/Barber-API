from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from models import Tenant, User
from schemas import SlotBlockSchema
from services.slot_service import (
    block_slots, 
    generate_user_slots, 
    complete_expired_slots, 
    get_available_start_times
)

router = APIRouter(prefix="/slots", tags=["slots"])

@router.get("/availability")
def availability_slots(service_id:int, user_id:int, session:Session = Depends(get_session)):
    
    return get_available_start_times(service_id, user_id, session)

@router.put("/block")
def block_slot(slot_block_schema: SlotBlockSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    return block_slots(session, current_user.id, slot_block_schema.init_block, end_block=slot_block_schema.end_block)

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




