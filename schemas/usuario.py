from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str = "barbeiro"

class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    ativo: bool
    class Config:
        from_attributes = True
