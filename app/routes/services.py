from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import permission_required
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.schemas.service_schema import ServiceSchema, ServiceEditSchema
from app.models.user import User
from app.models.permission import PermissionRole
from app.models.tenant import Tenant
from app.services.service_service import (
    create_new_service,
    list_tenant_services,
    get_service_by_id,
    status_service_by_id,
    update_service
)

router = APIRouter(prefix="/services", tags=["services"])

@router.post("/create")
def create_service(
    service_schema: ServiceSchema, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_SERVICES))
)-> Dict[str, Any]:
    
    service = create_new_service(session, current_user, service_schema)
    return {
            "mensagem": f"Servico criado com sucesso",
            "service": service.name,
            "id_service":service.id
    }

@router.get("/list")
def list_service(
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant)
)-> list[Dict[str, Any]]:
    
    services = list_tenant_services(session, current_tenant)
    return [
            {"id": s.id, 
             "name": s.name, 
             "duration": s.duration, 
             "price": str(s.price) if s.price else None, 
             "status": s.status, 
             "tenant_id": s.tenant_id
             } for s in services
        ]

@router.get("/search/{id_service}")
def search_service(
    id_service: int, 
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant)
)-> Dict[str, Any]:
    
    s = get_service_by_id(session, id_service, current_tenant.id)
    return {
            "id": s.id, 
            "name": s.name, 
            "duration": s.duration, 
            "price": str(s.price) if s.price else None, 
            "status": s.status, 
            "tenant_id": s.tenant_id
        }

@router.put("/edit/{id_service}")
def edit_service(
    id_service: int, 
    service_schema: ServiceEditSchema, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_SERVICES))
)-> Dict[str, Any]:
    
    s = update_service(session, id_service, current_user.tenant_id,  service_schema)
    return {
            "id": s.id, 
            "name": s.name, 
            "duration": s.duration, 
            "price": str(s.price) if s.price else None, 
            "status": s.status, 
            "tenant_id": s.tenant_id
        }
     

@router.put("/status/{id_service}")
def status_service(
    id_service: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_SERVICES))
)-> Dict[str, Any]:
    
    service = status_service_by_id(session, id_service, current_user.tenant_id)
    return {
        "status": service.status
    }