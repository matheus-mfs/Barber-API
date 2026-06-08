from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Service, User, UserService
from app.models.permission import PermissionRole
from app.models.tenant import Tenant
from app.schemas.user_service_schema import UserServiceEditSchema, UserServiceSchema
from app.services.permission_service import check_permission_user

def post_add_barber_service(
        user_service_schema:UserServiceSchema, 
        current_user: User, 
        session:Session,
) -> UserService:
    """Adicionar um novo serviço de barbearia para um usuário.

    Args:
        user_service_schema (UserServiceSchema): O schema para criar user service.
        current_user (User): Usuário autenticado.
        session (Session): Sessão do banco de dados.

    Returns:
        UserService: O user service criado
    """
    
    user_id = check_permission_user(
        user_service_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_USER_SERVICES, 
        PermissionRole.MANAGE_ALL_USER_SERVICES
    )

    if (session.query(UserService).filter(UserService.service_id == user_service_schema.service_id, UserService.user_id==user_id).first()):
        raise HTTPException(status_code=403, detail="Serviço ja cadastrado para o usuario")

    service = (session.query(Service)
               .filter(Service.id==user_service_schema.service_id, 
                       Service.tenant_id==current_user.tenant_id).first()
    )
    
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    if user_service_schema.custom_price is None:
        user_service_schema.custom_price = service.price
    if user_service_schema.custom_duration is None:
        user_service_schema.custom_duration = service.duration

    user_service = UserService(
        current_user.tenant_id, 
        service.id, 
        user_id, 
        user_service_schema.custom_duration, 
        user_service_schema.custom_price
    )

    session.add(user_service)
    session.commit()
    return user_service

def get_list_barber_service(user_id: int, session:Session, current_tenant: Tenant) -> List[UserService]:
    """Retorna uma lista de todos os serviços de barbearia disponíveis para um usuário.

    Args:
        user_id (int): O id do usuario.
        session (Session): Sessão do banco de dados.

    Returns:
        List[UserService]: Uma lista de User service.

    """

    user_service = (
        session.query(UserService)
        .filter(UserService.user_id == user_id, 
                UserService.tenant_id==current_tenant.id).all()
    )

    if not user_service:
        raise HTTPException(status_code=404, detail="Sem serviços no catalogo")
    return user_service

def get_id_user_service(id_service: int, user_id: int, tenant_id: int, session: Session) -> UserService:
    """Retorna um serviço de barbearia específico para um usuário.

    Args:
        id_service (int): O id do servico.
        user_id (int): O id do usuario.
        session (Session): Sessão do banco de dados

    Returns:
        UserService: User service encontrado

    """

    user_service = (
        session.query(UserService)
        .filter(UserService.service_id==id_service, 
                UserService.user_id==user_id, 
                UserService.tenant_id==tenant_id).first()
    )

    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado no catalogo")
    return user_service

def put_edit_user_service(
        user_service_edit_schema: UserServiceEditSchema, 
        current_user:User,
        session: Session,
) -> UserService:
    """Editar um serviço de barbearia existente para um usuário.

    Args:
        id_service (int): O id do servico.
        user_service_edit_schema (UserServiceEditSchema): O schema para editar user service.
        current_user (User): Usuário autenticado
        session (Session): Sessão do banco de dados

    Returns:
        UserService: User service atualizado.
    """

    user_id = check_permission_user(
        user_service_edit_schema.user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_USER_SERVICES, 
        PermissionRole.MANAGE_ALL_USER_SERVICES
    )

    user_service = get_id_user_service(user_service_edit_schema.service_id, user_id, current_user.tenant_id, session)
    if not user_service_edit_schema.custom_price is None:
        user_service.custom_price = user_service_edit_schema.custom_price
    if not user_service_edit_schema.custom_duration is None:
        user_service.custom_duration =  user_service_edit_schema.custom_duration

    session.commit()
    return user_service

def put_status_user_service(
        id_service: int, 
        current_user: User, 
        session: Session,
        user_id: Optional[int] = None,
) -> UserService:
    """Ativar/Desativar um user service para um usuario.

    Args:
        id_service (int): O id do servico.
        current_user (User): Usuário autenticado
        session (Session): Sessão do banco de dados

    Returns:
        UserService: User service ativado ou desativado.
    """

    user_id = check_permission_user(
        user_id, 
        current_user, 
        session, 
        PermissionRole.MANAGE_OWN_USER_SERVICES, 
        PermissionRole.MANAGE_ALL_USER_SERVICES
    )

    user_service = get_id_user_service(id_service, user_id, current_user.tenant_id, session)
    
    if user_service.status:
        user_service.status = False
    else:
        user_service.status = True

    session.commit()
    return user_service
