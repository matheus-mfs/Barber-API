from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_session
from models import Tenant,User

def get_tenant(request: Request, session: Session = Depends(get_session)):
    
    # pega host completo
    host = request.headers.get("host")
    if not host:
        raise HTTPException(status_code=400, detail="Host não encontrado")
    
    # remove porta
    host_without_port = host.split(":")[0]
    parts = host_without_port.split(".")

    # valida se existe subdominio
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Tenant inválido")
    subdomain = parts[0]

    # busca tenant no banco
    tenant = session.query(Tenant).filter(Tenant.slug == subdomain).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    return tenant

