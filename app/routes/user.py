from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant, permission_required
from app.models import Tenant, User
from app.models.permission import PermissionRole
from app.schemas.user_schema import UserEditSchema, UserResponseSchema
from app.services.user_service import (

    status_user_service,
    get_user_by_id,
    list_users_service,
    update_user_service,
)

router: APIRouter = APIRouter(prefix="/users", tags=["users"])

@router.get("/list", response_model=List[UserResponseSchema])
def list_user(
    session: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_tenant)
) -> List[UserResponseSchema]:
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
def search_user(
    id_user: int, 
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant),
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_ALL_USERS))
) -> UserResponseSchema:
    """Busca um usuário específico."""
    return get_user_by_id(session, id_user, current_tenant.id)

@router.put("/edit/{id_user}", response_model=UserResponseSchema)
def edit_user(
    user_edit_schema: UserEditSchema,
    user_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(check_token)
) -> UserResponseSchema:
    """Edita dados de um usuário."""
    return update_user_service(session, user_edit_schema, current_user, user_id)

@router.post("/status/{id_user}")
def status_user(
    id_user: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_ALL_USERS))
) -> Dict[str, str]:
    """Desativa um usuário ou ativa"""
    user: User = status_user_service(session, id_user, current_user)
    return {
            "id": user.id,
            "status": user.status 
        }
