from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_session
from core.auth import check_token
from models import User, UserRole
from schemas import UserEditSchema, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])

def is_admin(user_role):
    if user_role == UserRole.BARBER:
        raise HTTPException(status_code=400, detail="Acesso negado")

def user_exists(user:User):
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

@router.get("/list", response_model=List[UserResponseSchema])
def list_user(session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    is_admin(current_user.role)
    users = session.query(User).filter(User.tenant_id==current_user.tenant_id).all()
    user_exists(users)
    return users

@router.get("/search/{id_user}", response_model=UserResponseSchema)
def search_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    is_admin(current_user.role)
    user = session.query(User).filter(User.id==id_user, User.tenant_id==current_user.tenant_id).first()
    user_exists(user)

    return user

@router.put("/edit/{id_user}")
def edit_user(id_user : int, user_edit_schema : UserEditSchema, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    # verificar se o usuario é admin ou o proprio usuario editar o proprio cadastro
    if current_user.role == UserRole.BARBER and current_user.id != id_user:
        raise HTTPException(status_code=400, detail="Acesso negado")
    user = session.query(User).filter(User.id==id_user).first()
    user_exists(user)

    user.name = user_edit_schema.name
    user.email = user_edit_schema.email

    session.commit()
    return{"mensagem":"Dados Atualizados com sucesso"}
    
@router.post("/disable/{id_user}")
def disable_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    is_admin(current_user.role)
    user = session.query(User).filter(User.id==id_user).first()
    user_exists(user)

    user.status = False
    session.commit()
    return {
        "mensagem": f"usuario {user.name} desativado "
    }

@router.post("/active/{id_user}")
def active_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    is_admin(current_user.role)
    user = session.query(User).filter(User.id==id_user).first()
    user_exists(user)

    user.status = True
    session.commit()
    return {
        "mensagem": f"usuario {user.name} ativado "
    }
