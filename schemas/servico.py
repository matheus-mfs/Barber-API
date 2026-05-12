from pydantic import BaseModel

class ServicoCreate(BaseModel):
    nome: str
    preco: float
    duracao_minutos: int

class ServicoUpdate(BaseModel):
    nome: str | None = None
    preco: float | None = None
    duracao_minutos: int | None = None

class ServicoOut(BaseModel):
    id: int
    nome: str
    preco: float
    duracao_minutos: int
    ativo: bool
    class Config:
        from_attributes = True
