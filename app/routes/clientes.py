from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import check_token
from app.core.database import get_session
from app.core.dependencies import get_tenant
from app.models import User, Tenant
from app.schemas.client_schema import ClientSchema
from app.services.client_service import (
    create_new_client,
    list_tenant_clients,
    get_client_by_id
)

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/")
def create_client(
    client_schema: ClientSchema, 
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant)
) -> Dict[str, Any]:
    """Cadastrar cliente"""

    client = create_new_client(session, current_tenant.id, client_schema)
    return {
            "id": client.id, 
            "name": client.name, 
            "telephone": client.telephone, 
            "tenant_id": client.tenant_id
        }

@router.get("/list")
def list_clients(
    current_tenant: Tenant = Depends(get_tenant), 
    session: Session = Depends(get_session), 
    current_user: User = Depends(check_token)
) -> List[Dict[str, Any]]:
    """Listar clientes de um tenant"""

    clients = list_tenant_clients(session, current_tenant.id)
    return [
            {
                "id": c.id, 
                "name": c.name, 
                "telephone": c.telephone, 
                "tenant_id": c.tenant_id
            } for c in clients
        ]

@router.get("/search/{id_client}")
def search_clients(
    id_client: int, 
    session: Session = Depends(get_session), 
    current_tenant: Tenant = Depends(get_tenant), 
    current_user: User = Depends(check_token)
)-> Dict[str, Any]:
    """Pesquisar clientes no tenant"""
    
    client = get_client_by_id(session, id_client, current_tenant.id)
    return {
            "id": client.id, 
            "name": client.name, 
            "telephone": client.telephone, 
            "tenant_id": client.tenant_id
        }