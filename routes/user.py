from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models import Tenant, User
from app.schemas.user_schema import UserEditSchema, UserResponseSchema
from app.services.user_service import (
    active_user_service,
    disable_user_service,
    get_user_by_id,
    list_users_service,
    update_user_service,
)

router: APIRouter = APIRouter(prefix="/users", tags=["users"])

@router.get("/list", response_model=List[UserResponseSchema])
def list_user(session: Session = Depends(get_session),current_tenant: Tenant = Depends(get_tenant)) -> List[UserResponseSchema]:
    """Lista todos os usuários do tenant."""
    users = list_users_service(session, current_tenant.id)
    return [
            {
                "tenant_id":user.tenant_id,
                "id":user.id,
                "name":user.name,
                "email":user.email,
                "role":user.role,
                "status":user.status,
                "created_at":user.created_at
            }for user in users
    ]

@router.get("/search/{id_user}", response_model=UserResponseSchema)
def search_user(id_user: int, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)) -> UserResponseSchema:
    """Busca um usuário específico."""
    return get_user_by_id(session, id_user, current_tenant.id)

@router.put("/edit/{id_user}", response_model=UserResponseSchema)
def edit_user(id_user: int,user_edit_schema: UserEditSchema,session: Session = Depends(get_session),current_user: User = Depends(check_token)) -> UserResponseSchema:
    """Edita dados de um usuário."""
    return update_user_service(session, id_user, user_edit_schema, current_user)

@router.post("/disable/{id_user}")
def disable_user(id_user: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)) -> Dict[str, str]:
    """Desativa um usuário."""
    user: User = disable_user_service(session, id_user, current_user)
    return {
            "mensagem": f"usuario {user.name} desativado"
        }

@router.post("/active/{id_user}")
def active_user(id_user: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)) -> Dict[str, str]:
    """Ativa um usuário."""
    user: User = active_user_service(session, id_user, current_user)
    return {
            "mensagem": f"usuario {user.name} ativado"
        }