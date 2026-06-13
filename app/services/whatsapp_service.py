from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.core.database import Session
from app.models.appointment import Appointment, AppointmentStatus

time_zone: ZoneInfo = ZoneInfo(settings.TIME_ZONE)

load_dotenv()

def send_message(number:str, message:str):
    """Enviar menssagem no whatsapp
    Args:
        number: numero de telefone 
        message: menssagem para enviar
    
    """
    url = "http://127.0.0.1:8080/message/sendText/Madu"

    payload = {
        "number": number,
        "textMessage": { "text": message },

    }
    headers = {
        "apikey": os.getenv("AUTHENTICATION_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


def send_reminders():
    session = Session()

    try:
        now = datetime.now(time_zone)
        
        pendentes = session.query(Appointment).filter(
            Appointment.notify_at <= now,
            Appointment.notified == False,
            Appointment.status == AppointmentStatus.PENDING  # não cancelados/passados
        ).all()

        for appointment in pendentes:
            msg = (
                f"Olá {appointment.client.name}! Lembrete: você tem um agendamento "
                f"em 1 hora "
                f"com {appointment.user_service.user.name}. Até logo!"
            )
            send_message(appointment.client.telephone, msg)
            appointment.notified = True

        session.commit()
    finally:
        session.close()