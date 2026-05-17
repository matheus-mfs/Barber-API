from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import User, Tenant
from schemas import ClientSchema
from services.client_service import (
    create_new_client,
    list_tenant_clients,
    get_client_by_id
)

router = APIRouter(prefix="/clients", tags=["clients"])
@router.post("/")
def create_client(client_schema: ClientSchema, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):

    client = create_new_client(session=session, tenant_id=current_tenant.id, client_schema=client_schema)

    return client

@router.get("/list")
def list_clients(current_tenant: Tenant = Depends(get_tenant), session: Session = Depends(get_session), current_user: User = Depends(check_token)):

    return list_tenant_clients(session=session,tenant_id=current_tenant.id)

@router.get("/search/{id_client}")
def search_clients(id_client: int, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant), current_user: User = Depends(check_token)):

    return get_client_by_id(session=session, client_id=id_client, tenant_id=current_tenant.id)