from fastapi import APIRouter

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("")
def criar_usuario():
    # TODO: cadastrar barbeiro/admin
    pass

@router.get("")
def listar_usuarios():
    # TODO: listar todos da barbearia
    pass

@router.get("/{id}")
def buscar_usuario(id: int):
    # TODO: buscar usuário por id
    pass

@router.put("/{id}")
def atualizar_usuario(id: int):
    # TODO: atualizar dados do usuário
    pass

@router.delete("/{id}")
def desativar_usuario(id: int):
    # TODO: desativar usuário
    pass
