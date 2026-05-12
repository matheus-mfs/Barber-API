from fastapi import APIRouter

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("")
def criar_tenant():
    # TODO: criar barbearia
    pass

@router.get("/{id}")
def buscar_tenant(id: int):
    # TODO: buscar barbearia por id
    pass

@router.put("/{id}")
def atualizar_tenant(id: int):
    # TODO: atualizar dados da barbearia
    pass
