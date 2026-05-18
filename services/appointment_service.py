from schemas import AppointmentSchemas
from models import Appointment, Slot, UserService, SlotStatus, AppointmentSlot
from math import ceil
from datetime import timedelta

def post_create_appointment(appointment_schemas:AppointmentSchemas, tenant_id, session):
    
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
    
