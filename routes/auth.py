from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login():
    # TODO: autenticar usuário e retornar token
    pass

@router.post("/logout")
def logout():
    # TODO: invalidar token / sessão
    pass
