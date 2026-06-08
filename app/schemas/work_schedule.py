from pydantic import BaseModel
from typing import Optional
from datetime import time

from app.models.schedule import Weekdays


class WorkScheduleSchema(BaseModel):
    user_id:Optional[int]
    weekday:Weekdays
    work_start: Optional[time]
    work_end: Optional[time]
    lunch_start: Optional[time]
    lunch_end: Optional[time]
    is_working: bool

    class config:
        from_attibutes = True  
    
class WorkScheduleEditSchema(BaseModel):
    user_id:Optional[int]
    weekday:Weekdays
    work_start: Optional[time]
    work_end: Optional[time]
    lunch_start: Optional[time]
    lunch_end: Optional[time]

    class config:
        from_attibutes = True  
        
class WorkScheduleStatusSchema(BaseModel):
    user_id:Optional[int]
    weekday:Weekdays

    class config:
        from_attibutes = True  