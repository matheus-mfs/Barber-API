from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_session
from core.auth import check_token
from core.dependencies import get_tenant
from models import User
from schemas import UserEditSchema, UserResponseSchema
from services.user_service import (
    list_users_service,
    get_user_by_id,
    update_user_service,
    disable_user_service,
    active_user_service
)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/list", response_model=List[UserResponseSchema])
def list_user(session: Session = Depends(get_session), current_tenant: User = Depends(get_tenant)):
    
    return list_users_service(session, current_tenant.id)

@router.get("/search/{id_user}", response_model=UserResponseSchema)
def search_user(id_user: int, session: Session = Depends(get_session), current_tenant: User = Depends(get_tenant)):
    
    return get_user_by_id(session, id_user, current_tenant.id)

@router.put("/edit/{id_user}", response_model=List[UserResponseSchema])
def edit_user(id_user: int, user_edit_schema: UserEditSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    return update_user_service(session, id_user, user_edit_schema, current_user)

@router.post("/disable/{id_user}")
def disable_user(id_user: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    user = disable_user_service(session, id_user, current_user)
    return {
        "mensagem":f"usuario {user.name} desativado"
    }

@router.post("/active/{id_user}")
def active_user(id_user: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    user = active_user_service(session, id_user, current_user)
    return {
        "mensagem":f"usuario {user.name} ativado"
    }