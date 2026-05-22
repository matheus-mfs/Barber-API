from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas import AppointmentSchemas
from models import Appointment, Slot, UserService, SlotStatus, AppointmentSlot, User, AppointmentStatus
from math import ceil
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
from core.config import settings
time_zone = ZoneInfo(settings.TIME_ZONE)

def post_create_appointment(appointment_schemas:AppointmentSchemas, tenant_id:int, session:Session):
    
    user_service = session.query(UserService).filter(UserService.id==appointment_schemas.user_service_id).first()
    end_time = (appointment_schemas.start_time + timedelta(minutes=user_service.custom_duration))
    
    appointment = Appointment(tenant_id, appointment_schemas.client_id, appointment_schemas.user_service_id, 
                              appointment_schemas.start_time, end_time, appointment_schemas.status)
    
    session.add(appointment)
    session.flush()

    required_slots = ceil(user_service.custom_duration / 15)
    slots = []
    for step in range(required_slots):
        start_time = appointment_schemas.start_time + timedelta(minutes=15 * step)
        slot = session.query(Slot).filter(Slot.user_id==user_service.user_id, Slot.date_time_init==start_time).first()
        slot.status = SlotStatus.BOOKED
        appointment_slot = AppointmentSlot(appointment.id, slot.id)
        slots.append(appointment_slot)

    session.add_all(slots)
    session.commit()
    return appointment
    
def get_list_appointment(user_id:int, session:Session ):
    appointment = session.query(Appointment).filter(Appointment.user_service_id.user_id == user_id).all()
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    return appointment

def get_today_appointment(user_id:int, session:Session ):
    today = datetime.now(time_zone).date
    appointment = session.query(Appointment).filter(Appointment.user_service_id.user_id == user_id, 
                                                    Appointment.start_time.date == today).all()
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    return appointment

def get_search_appointment_id(appointment_id:int, current_user:User , session:Session):
    appointment = session.query(Appointment).filter(Appointment.id==appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    return appointment

def put_cancel_appointment(appointment_id:int, current_user:User , session:Session):
    appointment = session.query(Appointment).filter(Appointment.id==appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Nada encontrado")
    appointment.status == AppointmentStatus.CANCELLED
    return appointment
