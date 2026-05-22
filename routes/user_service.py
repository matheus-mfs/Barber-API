from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from schemas import UserServiceSchema, UserServiceEditSchema
from models import User, Tenant
from services.user_service_service import(
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
    
    return get_list_barber_service(user_id, session)

@router.get("/search/{id_service}")
def search_user_service(id_service:int, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    return get_id_user_service(id_service, current_user, session)

@router.post("/create")
def create_user_service(user_service_schema:UserServiceSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    return post_create_barber_service(user_service_schema, current_user, session)

@router.put("/edit/{id_service}")
def edit_user_service(id_service:int, user_service_edit_schema: UserServiceEditSchema, current_user: User = Depends(check_token), session: Session = Depends(get_session)):
    
    return put_edit_user_service(id_service, user_service_edit_schema, current_user, session)

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