from fastapi import APIRouter

router = APIRouter(prefix="/slots", tags=["slots"])

@router.post("")
def criar_slot():
    # TODO: criar slot manualmente
    pass

@router.post("/gerar")
def gerar_slots():
    # TODO: gerar slots automáticos do dia/semana
    pass

@router.get("")
def listar_slots():
    # TODO: listar todos os slots
    pass

@router.get("/disponiveis")
def listar_slots_disponiveis():
    # TODO: listar só os slots disponíveis
    pass

@router.get("/barbeiro/{usuario_id}")
def agenda_barbeiro(usuario_id: int):
    # TODO: agenda de um barbeiro específico
    pass

@router.put("/{id}")
def atualizar_slot(id: int):
    # TODO: atualizar status do slot (bloquear, liberar)
    pass

@router.delete("/{id}")
def remover_slot(id: int):
    # TODO: remover slot
    pass
