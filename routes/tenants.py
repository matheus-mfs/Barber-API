from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from schemas import TenantSchema
from models import User
from services.tenant_service import (
    create_tenant_service,
    get_tenant_by_id,
    update_tenant_service
)

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("/create")
def create_tenant(tenant_schema: TenantSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    create_tenant_service(session=session, tenant_schema=tenant_schema, current_user=current_user)

    return {"message":"Tenant criado com sucesso"}

@router.get("/search/{id_tenant}")
def search_tenant(id_tenant: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    return get_tenant_by_id(session=session, tenant_id=id_tenant, current_user=current_user)

@router.put("/edit/{id_tenant}")
def edit_tenant(id_tenant: int, tenant_schema: TenantSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    update_tenant_service(session=session, tenant_id=id_tenant, tenant_schema=tenant_schema, current_user=current_user)

    return {"mensagem":"Informacoes atualizadas"}