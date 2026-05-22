from fastapi import HTTPException
from models import Service

def create_new_service(session, current_user, service_schema):

    service_schema.name = service_schema.name.lower().strip()

    service_search = session.query(Service).filter(Service.name == service_schema.name,
                                                   Service.tenant_id == current_user.tenant_id).first()
    if service_search:
        raise HTTPException(status_code=401, detail="Servico ja cadastrado")

    service = Service(current_user.tenant_id, service_schema.name, service_schema.duration,
                      service_schema.price, service_schema.status)

    session.add(service)
    session.commit()

    return service

def list_tenant_services(session, tenant_id):

    return session.query(Service).filter(Service.tenant_id == tenant_id).all()

def get_service_by_id(session, service_id,tenant_id):

    service = session.query(Service).filter(Service.id == service_id, 
                                            Service.tenant_id == tenant_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Nenhum servico encontrado")

    return service

def update_service(session, service_id, tenant_id, service_schema):

    service = get_service_by_id(session=session, service_id=service_id, tenant_id=tenant_id)

    service.name = service_schema.name.lower().strip()
    service.duration = service_schema.duration
    service.price = service_schema.price

    session.commit()
    return service

def disable_service_by_id(session, service_id, tenant_id):

    service = get_service_by_id(session=session, service_id=service_id, tenant_id=tenant_id)
    service.status = False
    session.commit()

    return service

def activate_service_by_id(session, service_id, tenant_id):

    service = get_service_by_id(session=session, service_id=service_id, tenant_id=tenant_id)
    service.status = True
    session.commit()

    return service