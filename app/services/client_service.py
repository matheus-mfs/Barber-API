from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Client


def create_new_client(session: Session, tenant_id: int, client_schema: any) -> Client:
    """Cria um novo cliente.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: ID do tenant
        client_schema: Schema com dados do cliente
        
    Returns:
        Client: Cliente criado ou existente
    """
    
    client_schema.name = client_schema.name.lower().strip()
    client_schema.telephone = "".join(
        number for number in client_schema.telephone if number.isdigit()
    )

    existing_client: Optional[Client] = session.query(Client).filter(
        Client.name == client_schema.name,
        Client.telephone == client_schema.telephone,
        Client.tenant_id == tenant_id,
    ).first()

    if existing_client:
        return existing_client

    new_client: Client = Client(
        tenant_id, client_schema.name, client_schema.telephone
    )
    session.add(new_client)
    session.commit()

    return new_client


def list_tenant_clients(session: Session, tenant_id: int) -> List[Client]:
    """Lista todos os clientes de um tenant.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: ID do tenant
        
    Returns:
        List[Client]: Lista de clientes
        
    """
    
    clients: List[Client] = session.query(Client).filter(
        Client.tenant_id == tenant_id
    ).all()

    if not clients:
        raise HTTPException(status_code=404, detail="Sem clientes cadastrados")

    return clients


def get_client_by_id(session: Session, client_id: int, tenant_id: int) -> Client:
    """Busca um cliente por ID.
    
    Args:
        session: Sessão do banco de dados
        client_id: ID do cliente
        tenant_id: ID do tenant
        
    Returns:
        Client: Cliente encontrado
   
    """
    
    client: Optional[Client] = session.query(Client).filter(
        Client.id == client_id, Client.tenant_id == tenant_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    return client