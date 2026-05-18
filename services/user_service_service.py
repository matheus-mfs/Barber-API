from fastapi import HTTPException
from models import Service, UserService

def post_create_barber_service(user_service_schema, current_user, session):
    
    if (session.query(UserService).filter(UserService.service_id == user_service_schema.service_id).first()):
        raise HTTPException(status_code=403, detail="Serviço ja cadastrado para o usuario")

    service = session.query(Service).filter(Service.id==user_service_schema.service_id, Service.tenant_id==current_user.tenant_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    if user_service_schema.custom_price is None:
        user_service_schema.custom_price = service.price
    if user_service_schema.custom_duration is None:
        user_service_schema.custom_duration = service.duration

    user_service = UserService(current_user.tenant_id, service.id, current_user.id, user_service_schema.custom_duration, user_service_schema.custom_price)
    session.add(user_service)
    session.commit()

def get_list_barber_service(current_user, session):
    user_service = session.query(UserService).filter(UserService.user_id == current_user.id).all()
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return user_service

def get_id_user_service(id_service, user_id, session):
    user_service = session.query(UserService).filter(UserService.service_id==id_service, UserService.user_id==user_id).first()
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return user_service

def put_edit_user_service(id_service, user_service_edit_schema, current_user, session):
    user_service = get_id_user_service(id_service, current_user.id, session)

    user_service.custom_price = user_service_edit_schema.custom_price
    user_service.custom_duration =  user_service_edit_schema.custom_duration

    session.commit()

def put_disable_user_service(id_service, current_user, session):
    user_service = get_id_user_service(id_service, current_user.id, session)
    user_service.status = False

    session.commit()

def put_active_user_service(id_service, current_user, session):
    user_service = get_id_user_service(id_service, current_user.id, session)
    user_service.status = True

    session.commit()