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
    
    service = create_new_service(session, current_user, service_schema)
    return {
            "mensagem": f"Servico criado com sucesso",
            "service": service.name,
            "id_service":service.id
    }

@router.get("/list")
def list_service(session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):
    
    return list_tenant_services(session, current_tenant.id)

@router.get("/search/{id_service}")
def search_service(id_service: int, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):
    
    return get_service_by_id(session, id_service, current_tenant.id)

@router.put("/edit/{id_service}")
def edit_service(id_service: int, service_schema: ServiceEditSchema, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    return update_service(session, id_service, current_user.tenant_id,  service_schema)
     
@router.put("/disable/{id_service}")
def disable_service(id_service: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    service = disable_service_by_id(session, id_service, current_user.tenant_id)
    return {
            "status": service.status
    }

@router.put("/active/{id_service}")
def active_service(id_service: int, session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    
    service = activate_service_by_id(session, id_service, current_user.tenant_id)
    return {
        "status": service.status
    }