from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from models import User, Tenant
from core.auth import bcrypt_context, authenticate_user, create_token, check_token
from core.database import get_session
from core.dependencies import get_tenant
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/create_account")
def create_account(user_schema: UserSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    user = session.query(User).filter(User.email==user_schema.email, User.tenant_id==current_tenant.id).first()
    if user:
        raise HTTPException(status_code=400, detail="E-mail do usuario ja cadastrado")
    else:
        password_encrypted = bcrypt_context.hash(user_schema.password)
        new_user = User(current_tenant.id, user_schema.name, user_schema.email, password_encrypted, user_schema.role, user_schema.status)
        session.add(new_user)
        session.commit()
        return{"message":"User cadastrado "}
    
@router.post("/login")
def login(login_schema: LoginSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):
    user = authenticate_user(login_schema.email, login_schema.password, current_tenant.id, session)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario não encontrado, ou credenciais invalidas")
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, duration_token=timedelta(days=7))
        return{"access_token": access_token,
               "refresh_token": refresh_token,
               "token_type":"Bearer"}

    
@router.post("/login-form")
def login_form(date_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):
    user = authenticate_user(date_form.username, date_form.password, current_tenant.id, session)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario não encontrado, ou credenciais invalidas")
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, duration_token=timedelta(days=7))
        return{"access_token": access_token,
               "refresh_token": refresh_token,
               "token_type":"Bearer"}

    
@router.get("/refresh")
def user_refresh_token(user: User = Depends(check_token)):
    access_token = create_token(user.id)

    return{
        "access_token": access_token,
        "token_type":"Bearer"
        }