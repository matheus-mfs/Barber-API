from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.models.permission import PermissionRole
from app.services.permission_service import check_permission_user


def validate_admin(user_role: UserRole) -> None:
    """Valida se o usuário é administrador.
    
    Args:
        user_role: Cargo do usuário
        
    """
    
    if user_role == UserRole.BARBER:
        raise HTTPException(status_code=400, detail="Acesso negado")


def validate_user_exists(user: Optional[User]) -> None:
    """Valida se um usuário existe.
    
    Args:
        user: Usuário para validar
        
    """
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")


def get_user_by_id(session: Session, user_id: int, tenant_id: int) -> User:
    """Busca um usuário por ID.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do usuário
        tenant_id: ID do tenant
        
    Returns:
        User: Usuário encontrado
        
    """
    
    user: Optional[User] = session.query(User).filter(
        User.id == user_id, User.tenant_id == tenant_id
    ).first()
    validate_user_exists(user)
    return user


def list_users_service(session: Session, tenant_id: int) -> List[User]:
    """Lista todos os usuários de um tenant.
    
    Args:
        session: Sessão do banco de dados
        tenant_id: ID do tenant
        
    Returns:
        List[User]: Lista de usuários
 
    """
    
    users: List[User] = session.query(User).filter(
        User.tenant_id == tenant_id
    ).all()
    validate_user_exists(users if users else None)
    return users


def update_user_service(
        session: Session, 
        user_edit_schema: any, 
        current_user: User,
        user_id: Optional[int] = None,
) -> User:
    """Atualiza dados de um usuário.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do usuário a atualizar
        user_edit_schema: Schema com dados para atualização
        current_user: Usuário autenticado fazendo a requisição
        
    Returns:
        User: Usuário atualizado
        
    """
    
    user_id = check_permission_user(
        user_id,
        current_user,
        session,
        PermissionRole.MANAGE_OWN_USER,
        PermissionRole.MANAGE_ALL_USERS
    )
    
    user: Optional[User] = session.query(User).filter(User.id == user_id).first()
    validate_user_exists(user)

    if current_user.role == UserRole.BARBER and current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Acesso negado")

    user.name = user_edit_schema.name
    user.email = user_edit_schema.email
    session.commit()

    return user


def status_user_service(session: Session, user_id: int, current_user: User) -> User:
    """Ativa um usuário.
    
    Args:
        session: Sessão do banco de dados
        user_id: ID do usuário a ativar
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        User: Usuário ativado
        

    """

    validate_admin(current_user.role)
    user: Optional[User] = session.query(User).filter(User.id == user_id).first()
    validate_user_exists(user)
    if user.status:
        user.status = False
    else:
        user.status = True

    session.commit()

    return user