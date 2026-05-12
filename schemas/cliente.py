from pydantic import BaseModel

class ClienteCreate(BaseModel):
    nome: str
    telefone: str | None = None

class ClienteUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None

class ClienteOut(BaseModel):
    id: int
    nome: str
    telefone: str | None
    class Config:
        from_attributes = True
