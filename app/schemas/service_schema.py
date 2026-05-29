from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ServiceSchema(BaseModel):
    """Schema para criação de serviço."""

    name: str
    duration: int
    price: Decimal
    status: Optional[bool] = True

    class Config:
        from_attributes = True


class ServiceEditSchema(BaseModel):
    """Schema para edição de serviço."""

    name: str
    duration: int
    price: Decimal

    class Config:
        from_attributes = True