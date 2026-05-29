from pydantic import BaseModel
from typing import Optional
from datetime import time


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
