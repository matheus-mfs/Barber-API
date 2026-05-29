from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Service, User


def create_new_service(session: Session, current_user: User, service_schema: any) -> Service:
    """Cria um novo serviço.
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        service_schema: Schema com dados do serviço
        
    Returns:
        Service: Serviço criado
        
    Raises:
        HTTPException: Se o serviço já está cadastrado
    """

    service_schema.name = service_schema.name.lower().strip()

    service_search: Optional[Service] = session.query(Service).filter(
        Service.name == service_schema.name,
        Service.tenant_id == current_user.tenant_id,
    ).first()
    if service_search:
        raise HTTPException(status_code=401, detail="Servico ja cadastrado")

    service: Service = Service(
        current_user.tenant_id,
        service_schema.name,
        service_schema.duration,
        service_schema.price,
        service_schema.status,
    )

    session.add(service)
    session.commit()

    return service

def list_tenant_services(session: Session, tenant_id: int) -> List[Service]:
    """Lista todos os serviços ativos de um tenant.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: ID do tenant
        
    Returns:
        List[Service]: Lista de serviços
    """
    
    service = session.query(Service).filter(
        Service.tenant_id == tenant_id, Service.status == True
    ).all()

    return service

def get_service_by_id(session: Session, service_id: int, tenant_id: int) -> Service:
    """Busca um serviço por ID.
    
    Args:
        session: Sessão do banco de dados
        service_id: ID do serviço
        tenant_id: ID do tenant
        
    Returns:
        Service: Serviço encontrado
        
    Raises:
        HTTPException: Se o serviço não for encontrado
    """
    
    service: Optional[Service] = session.query(Service).filter(
        Service.id == service_id, Service.tenant_id == tenant_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Nenhum servico encontrado")

    return service

def update_service(session: Session, service_id: int, tenant_id: int, service_schema: any) -> Service:
    """Atualiza dados de um serviço.
    
    Args:
        session: Sessão do banco de dados
        service_id: ID do serviço
        tenant_id: ID do tenant
        service_schema: Schema com dados para atualização
        
    Returns:
        Service: Serviço atualizado
    """
    
    service: Service = get_service_by_id(
        session=session, service_id=service_id, tenant_id=tenant_id
    )
    if not service:
        raise HTTPException(status_code=404, detail="Nenhum servico encontrado")

    service.name = service_schema.name.lower().strip()
    service.duration = service_schema.duration
    service.price = service_schema.price

    session.commit()
    return service


def status_service_by_id(session: Session, service_id: int, tenant_id: int) -> Service:
    """Alterna o status de um serviço.
    
    Args:
        session: Sessão do banco de dados
        service_id: ID do serviço
        tenant_id: ID do tenant
        
    Returns:
        Service: Serviço com status atualizado
    """
    
    service: Service = get_service_by_id(
        session=session, service_id=service_id, tenant_id=tenant_id
    )

    if not service:
        raise HTTPException(status_code=404, detail="Nenhum servico encontrado")

    if service.status:
        service.status = False
    else:
        service.status = True
    
    session.commit()
    return service