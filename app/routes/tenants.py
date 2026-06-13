from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import permission_required
from app.models.permission import PermissionRole
from app.schemas.tenant_schema import TenantSchema
from app.models import User, Tenant
from app.services.tenant_service import (
    create_tenant_service,
    get_tenant_by_id,
    update_tenant_service
)

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("/")
def create_tenant(
    tenant_schema: TenantSchema, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(check_token)
)-> Dict[str,Any]:
    """Criar tenant"""
    
    tenant = create_tenant_service(session, tenant_schema, current_user)
    return {
            "id": tenant.id, 
            "name": tenant.name, 
            "slug": tenant.slug, 
            "status": tenant.status
        }

@router.get("/{id_tenant}")
def search_tenant(
    id_tenant: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(check_token)
)-> Dict[str,Any]:
    """Buscar Tenant"""
    
    tenant = get_tenant_by_id(session, id_tenant, current_user)
    return {
            "id": tenant.id, 
            "name": tenant.name, 
            "slug": tenant.slug, 
            "status": tenant.status
        }

@router.put("/{id_tenant}")
def edit_tenant(
    id_tenant: int, 
    tenant_schema: TenantSchema, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(permission_required(PermissionRole.MANAGE_TENANT))
)-> Dict[str,Any]:
    """Editar Tenant"""
    
    tenant = update_tenant_service(session, id_tenant, tenant_schema, current_user)
    return {
            "id": tenant.id, 
            "name": tenant.name, 
            "slug": tenant.slug, 
            "status": tenant.status
        }
