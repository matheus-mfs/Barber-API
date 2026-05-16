from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.config import settings
from models import User, Slot, WorkSchedule, SlotStatus, UserRole
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from schemas import SlotBlockSchema
import requests

time_zone = ZoneInfo(settings.TIME_ZONE)

router = APIRouter(prefix="/slots", tags=["slots"])

def get_weekday(today:date): 

    today = str(today)
    year, month, day = today.split("-")
    today = date(int(year), int(month), int(day)).weekday()
    return today # retorna o dia da semana conforme a data

def is_holiday():
    url = ""
    request = requests.get(url)
    data = request.json()
    print(data)

# Dicionario de dias da semana 
weekdays = {0:"monday",
            1:"tuesday",
            2:"wednesday",
            3:"thursday",
            4:"friday",
            5:"saturday",
            6:"sunday"}

@router.post("/gerar")
def gerar_slots(session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    work_schedule = session.query(WorkSchedule).filter(WorkSchedule.user_id==current_user.id).all()
    if not work_schedule:
        raise HTTPException(status_code=404, detail="Nao encontrado")
    
    for cont in range(0,30):
        data = date.today()+timedelta(days=cont)    
        day = get_weekday(data)                        

        for weekday in work_schedule:
            
            if not weekday.weekday.value == weekdays.get(day):
                # Procurando o horario de trabalho do dia para montar slots
                continue

            if not weekday.is_working:
                # Domingo nao gera slot
                continue
            # Convertendo Time para DateTime para poder fazer operações
            work_start = datetime.combine(data, weekday.work_start)
            work_end = datetime.combine(data, weekday.work_end)
            print(type(work_start))

            query = session.query(Slot).filter(Slot.date_time_init==work_start, Slot.user_id==current_user.id)

            if query:
                # Slots para esse dia ja gerados
                continue

            # Caso nao tenha o horario de almoço no dia 
            if weekday.lunch_start == None:  
                while work_start < work_end:
                    init = work_start
                    work_start += timedelta(minutes=15)
                    slot = Slot(current_user.tenant_id, current_user.id, init, work_start, "FREE")
                    session.add(slot)
                    session.commit()
            # Caso tenha o horario de almoço no dia
            else:
                lunch_start = datetime.combine(data, weekday.lunch_start)
                lunch_end = datetime.combine(data, weekday.lunch_end)
                
                while work_start < work_end:
                    if work_start >= lunch_start and work_start < lunch_end:
                        work_start += timedelta(minutes=15)
                        continue
                    init = work_start
                    work_start += timedelta(minutes=15)
                    slot = Slot(current_user.tenant_id, current_user.id, init, work_start, "FREE")
                    session.add(slot)
                    session.commit()

    return {"Mensagem":"Slots gerados com sucesso"}

@router.post("/complet")
def finaly_slots(session: Session = Depends(get_session)):
    # TODO: bloquear horarios que ja passaram conforme horario atual
    slots = session.query(Slot).filter(Slot.date_time_init<datetime.now(time_zone)).all()
    if not slots:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")
    for slot in slots:
        slot.status = SlotStatus.BLOCKED
    session.commit()
    return slots
    
@router.get("/list")
def list_slots(session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    slots = session.query(Slot).filter(Slot.user_id==current_user.id).all()
    if not slots:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")
    return slots

@router.get("/free-slots")
def free_slots(session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    slots = session.query(Slot).filter(Slot.user_id==current_user.id, Slot.status==SlotStatus.FREE).all()
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")
    return slots

@router.get("/{usuario_id}")
def slots_barber(usuario_id: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    if current_user.role == UserRole.BARBER:
        raise HTTPException(status_code=401, detail="Acesso Negado")
    slots = session.query(Slot).filter(Slot.user_id==usuario_id, Slot.status==SlotStatus.FREE).all()
    if not slots:
        raise HTTPException(status_code=404, detail="Sem horarios livres")
    return slots

@router.put("/block")
def edit_slot(slot_block_schema:SlotBlockSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    while slot_block_schema.init_block < slot_block_schema.end_block:
        slot = session.query(Slot).filter(Slot.date_time_init==slot_block_schema.init_block, Slot.user_id==current_user.id).first()
        slot.status = SlotStatus.BLOCKED
        slot_block_schema.init_block += timedelta(minutes=15)
    session.commit()
    return {"Mensagem":"Horario bloqueado"} 


    
    

