from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Client
from app.models.appointment import Appointment
from app.schemas.client_schema import ClientEditSchema


def create_new_client(
        session: Session, 
        tenant_id: int, 
        client_schema: any
) -> Client:
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


def list_tenant_clients(
        session: Session, 
        tenant_id: int
) -> List[Client]:
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


def get_client_by_id(
        session: Session, 
        client_id: int, 
        tenant_id: int
) -> Client:
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

def edit_client_by_id(
    id_client:int,
    tenant_id:int,
    client_edit_schema: ClientEditSchema,
    session: Session
) -> Client:
    """Editar informações de um cliente

    Args:
        id_client: ID do client
        tenant_id: ID do tenant
        client_edit_schema: Schema com dados do cliente
        session: Sessão do banco de dados

    Return:
        Client: Cliente editado
    """


    client = get_client_by_id(session, id_client, tenant_id)

    client.name = client_edit_schema.name
    client.telephone = client_edit_schema.telephone

    session.commit()

def list_appointment_client(
    id_client:int,
    tenant_id:int,
    session: Session,
) -> List[Appointment]:
    """Buscar agendamentos feito por um client
    
    Args:
        id_client: ID do client
        tenant_id: ID do tenant
        session: Sessão do banco de dados

    Return:
        List[Appointment] = Lista de agendamentos de um cliente
    
    """
    
    appointments = session.query(Appointment).filter(Appointment.client_id==id_client, Appointment.tenant_id==tenant_id).all()

    if not appointments:
        raise

    return appointments

def delete_client_by_id(
        id_client:int,
        tenant_id:int,
        session:Session
) -> None:
    """Deletar um Cliente

    Args:
        id_client: ID do cliente
        tenant_id: ID do Tenant do cliente
        session: Sessao do banco de dados
    
    """
    
    client = get_client_by_id(session, id_client, tenant_id)
    
    session.delete(client)
    session.commit()