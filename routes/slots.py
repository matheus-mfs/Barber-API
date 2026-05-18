from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import Tenant, User
from schemas import SlotBlockSchema
from services.slot_service import (
    block_slots, 
    generate_user_slots, 
    complete_expired_slots, 
    get_barber_free_slots, 
    get_user_free_slots, 
    get_user_slots,
    get_available_start_times
)

router = APIRouter(prefix="/slots", tags=["slots"])

@router.get("/availability")
def availability_slots(service_id:int, user_id:int, session:Session = Depends(get_session)):

    return get_available_start_times(service_id, user_id, session)

@router.put("/block")
def block_slot(slot_block_schema: SlotBlockSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    block_slots(session=session, user_id=current_user.id, init_block=slot_block_schema.init_block, end_block=slot_block_schema.end_block)

    return {
        "message": "Horario bloqueado"
    }

# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.post("/generate")
def generate_slots(session: Session = Depends(get_session),current_user: User = Depends(check_token)):
    generate_user_slots(session=session, user=current_user)

    return {
        "message": "Slots gerados com sucesso"
    }

# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.post("/complet")
def finaly_slots(session: Session = Depends(get_session)):

    complete_expired_slots(session)

    return {
        "message": "Slots atualizados"
    }
# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.get("/list")
def list_slots(session: Session = Depends(get_session),current_user: User = Depends(check_token)):

    return get_user_slots(session=session, user_id=current_user.id)

# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.get("/free-slots")
def free_slots(session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    return get_user_free_slots(session=session,user_id=current_user.id)

# Converter essa rota para def, e automatizar para ela gerar slots para todos os Barber/Admin-Barber nao apenas 1
@router.get("/{usuario_id}")
def slots_barber(usuario_id: int,session: Session = Depends(get_session),current_user: User = Depends(check_token)):

    return get_barber_free_slots(session=session, current_user=current_user, user_id=usuario_id)



