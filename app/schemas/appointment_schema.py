from pydantic import BaseModel
from datetime import datetime
from app.models import AppointmentStatus
from typing import Optional


class AppointmentSchemas(BaseModel):
    client_id: int
    user_service_id: int
    start_time: datetime
    status: Optional[AppointmentStatus] = AppointmentStatus.PENDING

    class config:
        from_attibutes = True 