from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.auth import check_token
from core.database import get_session
from core.dependencies import get_tenant
from models import User, Client, Tenant
from schemas import ClientSchema

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/")
def create_client(client_schema: ClientSchema ,session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant)):
    client_schema.name = client_schema.name.lower().strip()
    client_schema.telephone = ''.join(number for number in client_schema.telephone if number.isdigit())
    
    while True:
        client_search = session.query(Client).filter(Client.name==client_schema.name, Client.telephone==client_schema.telephone, Client.tenant_id==current_tenant.id).first()
        if not client_search:
            client = Client(current_tenant.id, client_schema.name, client_schema.telephone)
            session.add(client)
            session.commit()
        if client_search:
            return client_search  


@router.get("/list")
def list_clients(current_tenant: Tenant = Depends(get_tenant), session: Session = Depends(get_session), current_user: User = Depends(check_token)):
    clients = session.query(Client).filter(Client.id==current_tenant.id).all()
    if not clients:
        raise HTTPException(status_code=404, detail="sem clientes cadastrados")
    return clients
    

@router.get("/search/{id_client}")
def search_clients(id_client: int, session: Session = Depends(get_session), current_tenant: Tenant = Depends(get_tenant), current_user: User = Depends(check_token)):
    client_search = session.query(Client).filter(Client.id==id_client, Client.tenant_id==current_tenant.id).first()
    if not client_search:
        raise HTTPException(status_code=401, detail="Cliente nao encontrado")
    return client_search
