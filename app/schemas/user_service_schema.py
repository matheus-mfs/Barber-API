from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class UserServiceSchema(BaseModel):
    user_id: Optional[int]
    service_id: int
    custom_duration: Optional[int] = None
    custom_price: Optional[Decimal] = None

    class config:
        from_attibutes = True  


class UserServiceEditSchema(BaseModel):
    user_id: Optional[int]
    service_id: int
    custom_duration: Optional[int] = None
    custom_price: Optional[Decimal] = None

    class config:
        from_attibutes = True  
