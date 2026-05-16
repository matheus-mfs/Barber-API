from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
from decimal import Decimal
from models import UserRole


#-------------------------------------------------
#               Tenant Schemas
#-------------------------------------------------

class TenantSchema(BaseModel):
    name: str
    status: Optional[bool]

    class config:
        from_attibutes = True  

#-------------------------------------------------
#               User Schemas
#-------------------------------------------------

class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole
    status: Optional[bool]

    class config:
        from_attributes = True

class UserEditSchema(BaseModel):
    name: str
    email: str

    class config:
        from_attributes = True

class UserResponseSchema(BaseModel):
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
    email: str
    password: str

    class config:
        from_attibutes = True   


#-------------------------------------------------
#               Client Schemas
#-------------------------------------------------


class ClientSchema(BaseModel):
    name: str
    telephone: str

    class config:
        from_attibutes = True  


#-------------------------------------------------
#               Service Schemas
#-------------------------------------------------

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

#-------------------------------------------------
#               Slot Schemas
#-------------------------------------------------

class SlotBlockSchema(BaseModel):
    init_block: datetime
    end_block: datetime

    class config:
        from_attibutes = True  


#-------------------------------------------------
#               Appointment Schemas
#-------------------------------------------------

#-------------------------------------------------
#               WorkSchedule Schemas
#-------------------------------------------------
class WorkScheduleSchema(BaseModel):
    work_start: Optional[time]
    work_end: Optional[time]
    lunch_start: Optional[time]
    lunch_end: Optional[time]
    is_working: bool

    class config:
        from_attibutes = True  
    
class WorkScheduleEditSchema(BaseModel):
    work_start: Optional[time]
    work_end: Optional[time]
    lunch_start: Optional[time]
    lunch_end: Optional[time]

    class config:
        from_attibutes = True  



