from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_session
from core.auth import check_token
from models import User
from schemas import UserEditSchema, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/list-user", response_model=List[UserResponseSchema])
def list_user(session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Acesso negado")
    
    users = session.query(User).filter(User.tenant_id==current_user.tenant_id).all()
    return users

@router.get("/search-users/{id_user}", response_model=UserResponseSchema)
def search_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    # verificar se o usuario é admin
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Acesso negado")
    # buscar usuarios do mesmo tenant do admin
    user = session.query(User).filter(User.id==id_user, User.tenant_id==current_user.tenant_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario não econtrado")

    return user

@router.put("/edit-user/{id_user}")
def edit_user(id_user : int, user_edit_schema : UserEditSchema, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    # verificar se o usuario é admin ou o proprio usuario editar o proprio cadastro
    if not current_user.admin and current_user.id != id_user:
        raise HTTPException(status_code=400, detail="Acesso negado")
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado") 

    user.name = user_edit_schema.name
    user.email = user_edit_schema.email
    user.role = user_edit_schema.role

    session.commit()
    return{"mensagem":"Dados Atualizados com sucesso"}
    
@router.post("/disable-user/{id_user}")
def disable_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    # verificar se o usuario é admin e verifica se o usuario para alterar existe
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Acesso negado")
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    # mudar status para False
    user.status = False
    session.commit()
    return {
        "mensagem": f"usuario {user.name} desativado "
    }

@router.post("/active-user/{id_user}")
def active_user(id_user : int, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    # verificar se o usuario é admin e verifica se o usuario para alterar existe
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Acesso negado")
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    # mudar status para False
    user.status = True
    session.commit()
    return {
        "mensagem": f"usuario {user.name} ativado "
    }
