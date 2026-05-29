from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models import UserRole


class UserSchema(BaseModel):
    """Schema para criação de novo usuário."""

    name: str
    email: str
    password: str
    role: UserRole
    status: Optional[bool] = True

    class Config:
        from_attributes = True


class UserEditSchema(BaseModel):
    """Schema para edição de usuário."""

    name: str
    email: str

    class Config:
        from_attributes = True


class UserResponseSchema(BaseModel):
    """Schema para resposta de usuário."""

    id: int
    status: bool
    created_at: datetime
    tenant_id: int
    email: str
    name: str
    role: UserRole

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    """Schema para login."""

    email: str
    password: str

    class Config:
        from_attributes = True