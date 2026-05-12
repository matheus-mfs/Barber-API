from pydantic import BaseModel

class TenantCreate(BaseModel):
    nome: str

class TenantUpdate(BaseModel):
    nome: str | None = None

class TenantOut(BaseModel):
    id: int
    nome: str
    ativo: bool
    class Config:
        from_attributes = True
