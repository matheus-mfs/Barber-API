from pydantic import BaseModel
from datetime import datetime

class AgendamentoCreate(BaseModel):
    cliente_id: int
    usuario_id: int
    slot_id: int
    servico_id: int

class AgendamentoStatusUpdate(BaseModel):
    status: str  # pendente | confirmado | cancelado | concluido

class AgendamentoOut(BaseModel):
    id: int
    cliente_id: int
    usuario_id: int
    slot_id: int
    servico_id: int
    status: str
    criado_em: datetime | None
    class Config:
        from_attributes = True
