from fastapi import HTTPException
from models import Client

def create_new_client(session, tenant_id, client_schema):

    client_schema.name = (client_schema.name.lower().strip())
    client_schema.telephone = ''.join(number for number in client_schema.telephone if number.isdigit())

    client_search = session.query(Client).filter(Client.name == client_schema.name, Client.telephone == client_schema.telephone, Client.tenant_id == tenant_id).first()

    if client_search:
        return client_search

    client = Client(tenant_id, client_schema.name, client_schema.telephone)

    session.add(client)
    session.commit()

    return client

def list_tenant_clients(session, tenant_id):

    clients = session.query(Client).filter(Client.tenant_id == tenant_id).all()

    if not clients:
        raise HTTPException(status_code=404,detail="Sem clientes cadastrados")

    return clients

def get_client_by_id(session, client_id, tenant_id):

    client = session.query(Client).filter(Client.id == client_id, Client.tenant_id == tenant_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    return client