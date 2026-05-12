from fastapi import APIRouter

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("")
def criar_cliente():
    # TODO: cadastrar cliente
    pass

@router.get("")
def listar_clientes():
    # TODO: listar clientes
    pass

@router.get("/{id}")
def buscar_cliente(id: int):
    # TODO: buscar cliente por id
    pass

@router.put("/{id}")
def atualizar_cliente(id: int):
    # TODO: atualizar dados do cliente
    pass

@router.delete("/{id}")
def remover_cliente(id: int):
    # TODO: remover cliente
    pass
