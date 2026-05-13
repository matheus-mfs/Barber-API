from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
from decimal import Decimal

class UserSchema(BaseModel):
    tenant_id: int
    name: str
    email: str
    password: str
    work_start_time: time
    work_end_time: time
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

class TenantSchema(BaseModel):
    name: str
    service_duration: int = 30
    status: Optional[bool]

    class config:
        from_attibutes = True  

class ServiceSchema(BaseModel):
    name: str
    duration: int
    price: Decimal
    status: Optional[bool]

    class config:
        from_attibutes = True  

class ServiceEditSchema(BaseModel):
    name: str
    duration: int
    price: Decimal

    class config:
        from_attibutes = True  

class ClientSchema(BaseModel):
    name: str
    telephone: str

    class config:
        from_attibutes = True  
