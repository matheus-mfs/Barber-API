from fastapi import APIRouter

router = APIRouter(prefix="/servicos", tags=["servicos"])

@router.post("")
def criar_servico():
    # TODO: cadastrar serviço
    pass

@router.get("")
def listar_servicos():
    # TODO: listar serviços ativos
    pass

@router.get("/{id}")
def buscar_servico(id: int):
    # TODO: buscar serviço por id
    pass

@router.put("/{id}")
def atualizar_servico(id: int):
    # TODO: atualizar preço/duração
    pass

@router.delete("/{id}")
def desativar_servico(id: int):
    # TODO: desativar serviço
    pass
