from pydantic import BaseModel
from typing import Optional

class TenantSchema(BaseModel):
    name: str
    status: Optional[bool]

    class config:
        from_attibutes = True  
