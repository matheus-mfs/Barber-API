from pydantic import BaseModel
from datetime import datetime

class SlotCreate(BaseModel):
    usuario_id: int
    inicio: datetime
    fim: datetime

class SlotGerar(BaseModel):
    usuario_id: int
    data_inicio: datetime
    data_fim: datetime
    duracao_minutos: int = 30

class SlotUpdate(BaseModel):
    disponivel: bool | None = None

class SlotOut(BaseModel):
    id: int
    usuario_id: int
    inicio: datetime
    fim: datetime
    disponivel: bool
    class Config:
        from_attributes = True
