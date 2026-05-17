from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from schemas import ServiceSchema, ServiceEditSchema
from models import User, Tenant
from services.service_service import (
    create_new_service,
    list_tenant_services,
    get_service_by_id,
    update_service,
    disable_service_by_id,
    activate_service_by_id
)

router = APIRouter(prefix="/services", tags=["services"])

@router.post("/create")
def create_service(service_schema: ServiceSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    service = create_new_service(session=session,current_user=current_user,service_schema=service_schema)

    return {
            "message": f"Servico {service.name} criado com sucesso",
            "service": service
    }

@router.get("/list")
def list_service(session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    services = list_tenant_services(session=session, tenant_id=current_tenant.id)

    return {
            "services": services
    }

@router.get("/search/{id_service}")
def search_service(id_service: int, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    return get_service_by_id(session=session, service_id=id_service, tenant_id=current_tenant.id)

@router.put("/edit/{id_service}")
def edit_service(id_service: int, service_schema: ServiceEditSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    update_service(session=session, service_id=id_service, tenant_id=current_user.tenant_id, service_schema=service_schema)

    return {
            "message": "Dados atualizados"
    }

@router.put("/disable/{id_service}")
def disable_service(id_service: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    disable_service_by_id(session=session, service_id=id_service, tenant_id=current_user.tenant_id)

    return {
            "message": "Servico desativado"
    }

@router.put("/active/{id_service}")
def active_service(id_service: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    activate_service_by_id(session=session, service_id=id_service, tenant_id=current_user.tenant_id)

    return {
        "message": "Servico ativado"
    }