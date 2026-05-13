from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from models import User, Slot

router = APIRouter(prefix="/slots", tags=["slots"])

@router.post("/gerar")
def gerar_slots():
    pass

@router.get("/list-slots")
def list_slots():
    # TODO: listar todos os slots
    pass

@router.get("/free-slots")
def free_slots():
    # TODO: listar só os slots disponíveis
    pass

@router.get("/{usuario_id}")
def slots_barber(usuario_id: int):
    # TODO: agenda de um barbeiro específico
    pass

@router.put("/edit-slot/{id}")
def edit_slot(id: int):
    # TODO: atualizar status do slot (bloquear, liberar)
    pass

@router.put("/disable-slot/{id}")
def disable_slot(id: int):
    # TODO: remover slot
    pass

@router.put("/active-slot/{id}")
def active_slot(id: int):
    # TODO: remover slot
    pass

