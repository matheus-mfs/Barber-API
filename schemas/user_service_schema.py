from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class UserServiceSchema(BaseModel):
    service_id: int
    custom_duration: Optional[int] = None
    custom_price: Optional[Decimal] = None

    class config:
        from_attibutes = True  


class UserServiceEditSchema(BaseModel):
    custom_duration: Optional[int] = None
    custom_price: Optional[Decimal] = None

    class config:
        from_attibutes = True  
