from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.schemas.user_service_schema import UserServiceSchema, UserServiceEditSchema
from app.models import User
from app.services.user_service_service import(
    post_create_barber_service,
    get_list_barber_service,
    get_id_user_service,
    put_edit_user_service,
    put_disable_user_service,
    put_active_user_service
)

router = APIRouter(prefix="/user-services", tags=["user-services"])

@router.get("/list/{user_id}")
def list_user_service(user_id:int, session: Session = Depends(get_session)):
    
    user_services = get_list_barber_service(user_id, session)
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

@router.get("/search/{id_service}")
def search_user_service(id_service:int, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    us = get_id_user_service(id_service, current_user.id, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

@router.post("/create")
def create_user_service(user_service_schema:UserServiceSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    us = post_create_barber_service(user_service_schema, current_user, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

@router.put("/edit/{id_service}")
def edit_user_service(id_service:int, user_service_edit_schema: UserServiceEditSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    us = put_edit_user_service(id_service, user_service_edit_schema, current_user, session)
    return {
            "id": us.id, 
            "tenant_id": us.tenant_id, 
            "service_id": us.service_id, 
            "user_id": us.user_id, 
            "custom_duration": us.custom_duration, 
            "custom_price": str(us.custom_price) if us.custom_price else None, 
            "status": us.status
        }

@router.put("/disable/{id_service}")
def disable_user_service(id_service:int, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    user_service = put_disable_user_service(id_service, current_user, session)
    return{
        "status": user_service.status
    }

@router.put("/active/{id_service}")
def active_user_service(id_service:int, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    user_service = put_active_user_service(id_service, current_user, session)
    return{
        "status": user_service.status
    }