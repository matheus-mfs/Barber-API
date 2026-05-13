from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    tenant_id: int
    name: str
    email: str
    password: str
    role: str
    status: Optional[bool]
    admin: Optional[bool] = False

    class config:
        from_attributes = True

class UserEditSchema(BaseModel):
    name: str
    email: str
    role: str

    class config:
        from_attributes = True

class UserResponseSchema(BaseModel):
    id: int
    status: bool
    created_at: datetime
    tenant_id: int
    email: str
    name: str
    role: str
    admin: bool

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class config:
        from_attibutes = True   