from typing import Any, Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import (
    check_token,
    create_account_service,
    login_service,
    refresh_token_service,
)
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models import Tenant, User
from app.schemas.user_schema import LoginSchema, UserResponseSchema, UserSchema

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/create_account", response_model=UserResponseSchema)
def create_account(user_schema: UserSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant),) -> UserResponseSchema:
    """Cria uma nova conta de usuário."""
    user: User = create_account_service(session, user_schema, current_tenant)
    return user


@router.post("/login")
def login(login_schema: LoginSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant),) -> Dict[str, Any]:
    """Realiza o login do usuário."""
    return login_service(
        login_schema.email, login_schema.password, current_tenant.id, session
    )


@router.post("/login-form")
def login_form(data_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant),) -> Dict[str, Any]:
    """Realiza o login usando OAuth2 form."""
    return login_service(
        data_form.username, data_form.password, current_tenant.id, session
    )


@router.get("/refresh")
def user_refresh_token(user: User = Depends(check_token)) -> Dict[str, Any]:
    """Renova o token de acesso."""
    return refresh_token_service(user)
