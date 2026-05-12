from fastapi import APIRouter

router = APIRouter(prefix="/agendamentos", tags=["agendamentos"])

@router.post("")
def criar_agendamento():
    # TODO: criar agendamento
    pass

@router.get("")
def listar_agendamentos():
    # TODO: listar todos os agendamentos
    pass

@router.get("/hoje")
def agendamentos_hoje():
    # TODO: agenda do dia
    pass

@router.get("/cliente/{cliente_id}")
def historico_cliente(cliente_id: int):
    # TODO: histórico do cliente
    pass

@router.get("/{id}")
def buscar_agendamento(id: int):
    # TODO: buscar agendamento por id
    pass

@router.put("/{id}/status")
def atualizar_status_agendamento(id: int):
    # TODO: confirmar, cancelar, concluir
    pass

@router.delete("/{id}")
def cancelar_agendamento(id: int):
    # TODO: cancelar agendamento
    pass
