from typing import Optional

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy.orm import Session

from app.models import Tenant, User, UserRole
from app.schemas.tenant_schema import TenantSchema


def validate_dev_permission(current_user: User) -> None:
    """Valida se o usuário tem permissão de desenvolvedor.
    
    Args:
        current_user: Usuário autenticado
        
    Raises:
        HTTPException: Se o usuário não for desenvolvedor
    """
    
    if current_user.role != UserRole.DEV:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
def get_tenant_by_id(session: Session, tenant_id: int, current_user: User) -> Tenant:
    """Busca um tenant por ID.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: ID do tenant
        current_user: Usuário autenticado (deve ser dev)
        
    Returns:
        Tenant: Tenant encontrado
        
    Raises:
        HTTPException: Se sem permissão ou tenant não encontrado
    """
    
    validate_dev_permission(current_user)
    tenant: Optional[Tenant] = session.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant nao encontrado")

    return tenant

def create_tenant_service(session: Session, tenant_schema: TenantSchema, current_user: User) -> Tenant:
    """Cria um novo tenant.
    
    Args:
        session: Sessão do banco de dados
        tenant_schema: Schema com dados do tenant
        current_user: Usuário autenticado (deve ser dev)
        
    Returns:
        Tenant: Tenant criado
        
    Raises:
        HTTPException: Se sem permissão
    """
    
    validate_dev_permission(current_user)
    slug: str = slugify(tenant_schema.name)
    tenant: Tenant = Tenant(tenant_schema.name, slug, tenant_schema.status)

    session.add(tenant)
    session.commit()
    return tenant

def update_tenant_service(session:Session, tenant_id:int, tenant_schema:TenantSchema, current_user:User) -> Tenant:
    """Atualizar dados de um tenant.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: Id do Tenant
        tenant_schema: Schema com dados do tenant
        current_user: Usuário autenticado (deve ser dev)
        
    Returns:
        Tenant: Tenant atualizado
        
    Raises:
        HTTPException: Se sem permissão
    """

    tenant = get_tenant_by_id(session=session, tenant_id=tenant_id, current_user=current_user )
    tenant.name = tenant_schema.name
    tenant.status = tenant_schema.status

    session.commit()
    return tenant