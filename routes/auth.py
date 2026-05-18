from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import UserSchema, LoginSchema
from models import User, Tenant
from core.database import get_session
from core.dependencies import get_tenant
from core.auth import check_token
from core.auth import (
    create_account_service,
    login_service,
    refresh_token_service
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/create_account")
def create_account(user_schema: UserSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    create_account_service(session, user_schema, current_tenant)

    return {"message":"User cadastrado"}

@router.post("/login")
def login(login_schema: LoginSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    return login_service(login_schema.email, login_schema.password, current_tenant.id, session)

@router.post("/login-form")
def login_form(data_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    return login_service(data_form.username, data_form.password, current_tenant.id, session)

@router.get("/refresh")
def user_refresh_token(user: User = Depends(check_token)):

    return refresh_token_service(user)

