from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models.tenant import Tenant
from app.schemas.user_service_schema import UserServiceSchema, UserServiceEditSchema
from app.models import User
from app.services.user_service_service import(
    post_add_barber_service,
    get_list_barber_service,
    get_id_user_service,
    put_edit_user_service,
    put_status_user_service
)

router = APIRouter(prefix="/user-services", tags=["user-services"])

@router.get("/list/{user_id}")
def list_user_service(
    user_id:int, 
    session: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_tenant)
)-> List[Dict[str,Any]]:
    """Listar serviços de um usuario"""

    user_services = get_list_barber_service(user_id, session, current_tenant)
    return [
            {
                "id": us.id, 
                "tenant_id": us.tenant_id, 
                "service_id": us.service_id, 
                "user_id": us.user_id, 
                "custom_duration": us.custom_duration, 
                "custom_price": str(us.custom_price) if us.custom_price else None, 
                "status": us.status
            } for us in user_services
    ]

@router.get("/search/{id_service}/{id_user}")
def search_user_service(
    id_service:int, 
    id_user:int, 
    session: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_tenant)
)-> Dict[str,Any]:
    """Buscar serviço de um usuario"""
    
    us = get_id_user_service(id_service, id_user, current_tenant.id, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

@router.post("/add")
def add_user_service(
    user_service_schema:UserServiceSchema, 
    current_user: User = Depends(check_token), 
    session: Session = Depends(get_session)
)-> Dict[str,Any]:
    """Adicionar serviço ao catalogo de um usuario"""

    us = post_add_barber_service(user_service_schema, current_user, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

@router.put("/edit/")
def edit_user_service(
    user_service_edit_schema: UserServiceEditSchema, 
    current_user: User = Depends(check_token), 
    session: Session = Depends(get_session)
)-> Dict[str,Any]:
    """Editar um serviço de um usuario"""
    
    us = put_edit_user_service(user_service_edit_schema, current_user, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

router.put("/status/{id_service}")
def status_user_service(
        id_service:int, 
        user_id: Optional[int] = None,
        current_user: User = Depends(check_token), 
        session: Session = Depends(get_session)
)-> Dict[str,Any]:
    """Ativar/desativar serviço de um usuario"""
    
    user_service = put_status_user_service(id_service, current_user, session, user_id)
    return{
        "status": user_service.status
    }

