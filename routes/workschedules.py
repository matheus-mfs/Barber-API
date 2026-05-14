from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from models import User
from schemas import WorkScheduleSchema

router = APIRouter(prefix="/workschedules", tags=["workschedules"])

@router.post("/")
def create_workschedules(work_schedule_schema: WorkScheduleSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    pass

