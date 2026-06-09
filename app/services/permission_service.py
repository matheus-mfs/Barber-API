"""
Serviço para gerenciar permissões de usuários baseado em seu role.
"""
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models import User, Permission, UserPermission, PermissionRole, UserRole
from fastapi import Depends, HTTPException


BARBER_PERMISSIONS = [
    PermissionRole.MANAGE_OWN_USER_SERVICES,
    PermissionRole.MANAGE_OWN_APPOINTMENTS,
    PermissionRole.VIEW_CLIENTS,
    PermissionRole.MANAGE_OWN_SLOTS,
    PermissionRole.MANAGE_OWN_USER,
    PermissionRole.MANAGE_OWN_WORKSCHEDULE,
    PermissionRole.VIEW_OWN_REPORTS,
]

OWNER_PERMISSIONS = [
    PermissionRole.MANAGE_ALL_USER_SERVICES,
    PermissionRole.MANAGE_ALL_APPOINTMENTS,
    PermissionRole.MANAGE_ALL_CLIENTS,
    PermissionRole.MANAGE_SERVICES,
    PermissionRole.MANAGE_ALL_SLOTS,
    PermissionRole.MANAGE_ALL_USERS,
    PermissionRole.MANAGE_ALL_WORKSCHEDULES,
    PermissionRole.VIEW_ALL_REPORTS,
    PermissionRole.MANAGE_TENANT,
]


def assign_barber_permissions(user: User, session: Session) -> None:
    """Atribui permissões padrão de barbeiro a um novo usuário.
    
    Args:
        user: Usuário recém criado com role BARBER
        session: Sessão do banco de dados
        
    Raises:
        HTTPException: Se não conseguir atribuir as permissões
    """
    _assign_permissions(user, BARBER_PERMISSIONS, session)

def assign_owner_permissions(user: User, session: Session) -> None:
    """Atribui permissões padrão de proprietário a um novo usuário.
    
    Args:
        user: Usuário recém criado com role OWNER
        session: Sessão do banco de dados
        
    Raises:
        HTTPException: Se não conseguir atribuir as permissões
    """
    _assign_permissions(user, OWNER_PERMISSIONS, session)

def _assign_permissions(
    user: User, 
    permission_roles: list[PermissionRole], 
    session: Session
) -> None:
    """Função interna para atribuir uma lista de permissões a um usuário.
    
    Args:
        user: Usuário para receber as permissões
        permission_roles: Lista de PermissionRole enums
        session: Sessão do banco de dados
        
    Raises:
        HTTPException: Se alguma permissão não existir no banco
    """
    for permission_role in permission_roles:
        # Busca a permissão no banco
        permission = session.query(Permission).filter(
            Permission.name == permission_role
        ).first()
        
        if not permission:
            raise HTTPException(
                status_code=500,
                detail=f"Permissão '{permission_role.value}' não existe no banco de dados. Execute a seed de permissões."
            )
        
        # Verifica se já não está atribuída
        existing = session.query(UserPermission).filter(
            UserPermission.user_id == user.id,
            UserPermission.permission_id == permission.id
        ).first()
        
        if not existing:
            # Cria novo registro de permissão
            user_permission = UserPermission(
                user_id=user.id,
                permission_id=permission.id
            )
            session.add(user_permission)
    
    # Commit de todas as permissões de uma vez
    session.commit()

def get_default_permissions_for_role(role: UserRole) -> list[PermissionRole]:
    """Retorna a lista de permissões padrão para um role.
    
    Args:
        role: UserRole enum (BARBER, OWNER, etc)
        
    Returns:
        Lista de PermissionRole que o usuário deve ter
    """
    if role == UserRole.BARBER:
        return BARBER_PERMISSIONS
    elif role == UserRole.OWNER:
        return OWNER_PERMISSIONS
    else:
        return []

def get_list_permissions_user(
        user_id: int, 
        session: Session = Depends(get_session)
) -> list[PermissionRole]:
    """Listar permissões do usuario
    Args:
        user_id: ID do usuario
        session: Sessao do banco de dados
    
    Return:
        List[PermissionRole]: Lista de permissões
    """
    permissions = session.query(UserPermission).filter(UserPermission.user_id==user_id).all()
    if not permissions:
        raise HTTPException(status_code=404, detail="nenhum permissão atribuiada a usuario")
    list_permission: list = []
    for p in permissions:
        permission_name = session.query(Permission).filter(Permission.id==p.permission_id).first()
        list_permission.append(permission_name.name.value)
    
    return list_permission

def check_permission_user(
          user_id:int,
          current_user:User, 
          session:Session, 
          permission_barber:PermissionRole, 
          permission_owner:PermissionRole
) -> int:
    """Verificar se tem permissao permissão 
    Args:
        user_id: ID do usuario
        current_user: Usuario logado
        session: sessao do banco de dados
        permission_barber: Permissao necessaria user
        permission_ower: Permissao necessaria owner
    Return:
        user_id: ID do usuario
    """


    from app.services.user_service import get_user_by_id
    
    list_permissions_user = get_list_permissions_user(current_user.id, session)

    if permission_owner.value in list_permissions_user:
        
        # Proprietário
        if user_id is None:
            raise HTTPException(status_code=400, detail="user_id é obrigatório")
        get_user_by_id(session, user_id, current_user.tenant_id)
        return user_id
    if permission_barber.value in list_permissions_user:
        # Barbeiro
        return current_user.id
    
    raise HTTPException(status_code=403, detail="Usuário não tem permissão para realizar esta ação")
