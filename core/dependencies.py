from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models import Tenant, User
from .database import get_session


def get_tenant(request: Request, session: Session = Depends(get_session)) -> Tenant:
    """Extrai o tenant do subdomínio do host.
    
    Args:
        request: Request do FastAPI
        session: Sessão do banco de dados
        
    Returns:
        Tenant: Tenant encontrado
        
    Raises:
        HTTPException: Se o host não for encontrado ou tenant inválido
    """
    # Pega host completo
    host: Optional[str] = request.headers.get("host")
    if not host:
        raise HTTPException(status_code=400, detail="Host não encontrado")
    
    # Remove porta
    host_without_port: str = host.split(":")[0]
    parts: list[str] = host_without_port.split(".")

    # Valida se existe subdomínio
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Tenant inválido")
    
    subdomain: str = parts[0]

    # Busca tenant no banco
    tenant: Optional[Tenant] = session.query(Tenant).filter(
        Tenant.slug == subdomain
    ).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    return tenant
