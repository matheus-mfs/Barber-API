from typing import Optional, List, Callable

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Tenant, User, PermissionRole
from .database import get_session
from .auth import check_token


def get_tenant(request: Request, session: Session = Depends(get_session)) -> Tenant:
    """Extrai o tenant do subdomínio do host.
    
    Args:
        request: Request do FastAPI
        session: Sessão do banco de dados
        
    Returns:
        Tenant: Tenant encontrado

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


# ============================================================================
# FACTORIES DE PERMISSÃO - Dependências de autorização
# ============================================================================

def permission_required(permission: PermissionRole) -> Callable:
    """Factory que cria uma dependência para validar uma permissão específica.
    
    Args:
        permission: Permissão requerida (PermissionRole enum)
        
    Returns:
        Callable: Função de dependência pronta para usar com FastAPI
        
    Exemplo:
        @router.post("/servicos")
        def criar_servico(
            current_user: User = Depends(permission_required(PermissionRole.CREATE_SERVICE))
        ):
            return {"message": "Serviço criado"}
    """

    async def verify(
        user: User = Depends(check_token),
        session: Session = Depends(get_session)
    ) -> User:
        # Carrega as permissões do usuário
        user_with_permissions = session.query(User).options(
            selectinload(User.permissions)
        ).filter(User.id == user.id).first()
        
        if not user_with_permissions:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        # Verifica se possui a permissão
        has_permission = any(
            perm.name == permission 
            for perm in user_with_permissions.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"Permissão negada. Requerido: {permission.value}"
            )
        
        return user_with_permissions
    return verify


def any_permission_required(permissions: List[PermissionRole]) -> Callable:
    """Factory para validar se o usuário possui QUALQUER uma das permissões.
    
    Args:
        permissions: Lista de permissões (usuário precisa ter apenas uma)
        
    Returns:
        Callable: Função de dependência pronta para usar com FastAPI
        
    Exemplo:
        @router.put("/servicos/{id}")
        def editar_servico(
            id: int,
            current_user: User = Depends(any_permission_required([
                PermissionRole.EDIT_SERVICE,
                PermissionRole.CREATE_SERVICE
            ]))
        ):
            return {"message": "Serviço editado"}
    """

    async def verify(
        user: User = Depends(check_token),
        session: Session = Depends(get_session)
    ) -> User:
        user_with_permissions = session.query(User).options(
            selectinload(User.permissions)
        ).filter(User.id == user.id).first()
        
        if not user_with_permissions:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        has_permission = any(
            perm.name in permissions 
            for perm in user_with_permissions.permissions
        )
        
        if not has_permission:
            permissions_str = ", ".join([p.value for p in permissions])
            raise HTTPException(
                status_code=403,
                detail=f"Permissão negada. Uma destas é requerida: {permissions_str}"
            )
        
        return user_with_permissions
    return verify


def all_permissions_required(permissions: List[PermissionRole]) -> Callable:
    """Factory para validar se o usuário possui TODAS as permissões.
    
    Args:
        permissions: Lista de permissões (usuário precisa ter todas)
        
    Returns:
        Callable: Função de dependência pronta para usar com FastAPI
        
    Exemplo:
        @router.delete("/servicos/{id}")
        def deletar_servico(
            id: int,
            current_user: User = Depends(all_permissions_required([
                PermissionRole.DELETE_SERVICE,
                PermissionRole.MANAGE_SCHEDULE
            ]))
        ):
            return {"message": "Serviço deletado"}
    """
    async def verify(
        user: User = Depends(check_token),
        session: Session = Depends(get_session)
    ) -> User:
        user_with_permissions = session.query(User).options(
            selectinload(User.permissions)
        ).filter(User.id == user.id).first()
        
        if not user_with_permissions:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        user_permissions = {perm.name for perm in user_with_permissions.permissions}
        required_set = set(permissions)
        
        if not required_set.issubset(user_permissions):
            missing_permissions = required_set - user_permissions
            permissions_str = ", ".join([p.value for p in missing_permissions])
            raise HTTPException(
                status_code=403,
                detail=f"Permissão negada. Faltam: {permissions_str}"
            )
        
        return user_with_permissions
    return verify
