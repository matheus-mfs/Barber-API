from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from schemas import ServiceSchema, ServiceEditSchema
from models import User, Service

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(check_token)])

@router.post("/create-service")
def create_service(service_schema: ServiceSchema, session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    service = session.query(Service).filter(Service.name == service_schema.name).first()
    if not service:
        raise HTTPException(status_code=401, detail="Serviço ja cadastrado")
    service = Service(current_user.tenant_id ,service_schema.name, service_schema.duration, service_schema.price, service_schema.status)
    session.add(service)
    session.commit()
    return{"mesagem":f"Serviço {service.name} criado com sucesso",
           "Service": service
           }

@router.get("/list-services")
def list_service(session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    services = session.query(Service).filter(Service.tenant_id==current_user.tenant_id).all()
    return{"services":services}

@router.get("/search-service/{id_service}")
def search_service(id_service: int, session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    service_search = session.query(Service).filter(Service.id==id_service, Service.tenant_id==current_user.tenant_id).first()
    if not service_search:
        raise HTTPException(status_code=404, detail="Nenhum serviço encontrado")
    return {"Service":service_search}

@router.put("/edit-service/{id_service}")
def edit_service(id_service: int, service_schema: ServiceEditSchema, session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    service_search = session.query(Service).filter(Service.id==id_service, Service.tenant_id==current_user.tenant_id).first()
    if not service_search:
        raise HTTPException(status_code=404, detail="Nenhum serviço encontrado para esse id")
    service_search.name = service_schema.name
    service_search.duration = service_schema.duration
    service_search.price = service_schema.price
    session.commit()
    return {"mensagem":"Dados Atualizados"}
    

@router.put("/disable-service/{id_service}")
def disable_service(id_service: int, session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    service_search = session.query(Service).filter(Service.id==id_service, Service.tenant_id==current_user.tenant_id).first()
    if not service_search:
        raise HTTPException(status_code=404, detail="Nenhum serviço encontrado para esse id")
    service_search.status=False
    session.commit()
    return{"mensagem":"Serviço desativado"}
    
@router.put("/active-service/{id_service}")
def active_service(id_service: int, session: Session = (Depends(get_session)), current_user : User = Depends(check_token)):
    service_search = session.query(Service).filter(Service.id==id_service, Service.tenant_id==current_user.tenant_id).first()
    if not service_search:
        raise HTTPException(status_code=404, detail="Nenhum serviço encontrado para esse id")
    service_search.status=True
    session.commit()
    return{"mensagem":"Serviço ativado"}
    