from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Service, User, UserService
from app.schemas.user_service_schema import UserServiceEditSchema, UserServiceSchema

def post_create_barber_service(user_service_schema:UserServiceSchema, current_user: User, session:Session) -> UserService:
    """Create a new barber service for a user.

    Args:
        user_service_schema (UserServiceSchema): The schema of the user service to create.
        current_user (User): The current authenticated user.
        session (Session): The database session.

    Returns:
        UserService: The created user service instance.

    Raises:
        HTTPException: If the service is already registered for the user or if the service is not found.
    """
    
    if (session.query(UserService).filter(UserService.service_id == user_service_schema.service_id).first()):
        raise HTTPException(status_code=403, detail="Serviço ja cadastrado para o usuario")

    service = session.query(Service).filter(Service.id==user_service_schema.service_id, Service.tenant_id==current_user.tenant_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    if user_service_schema.custom_price is None:
        user_service_schema.custom_price = service.price
    if user_service_schema.custom_duration is None:
        user_service_schema.custom_duration = service.duration

    user_service = UserService(current_user.tenant_id, service.id, current_user.id, user_service_schema.custom_duration, user_service_schema.custom_price)
    session.add(user_service)
    session.commit()
    return user_service

def get_list_barber_service(user_id: int, session:Session) -> List[UserService]:
    """Retrieve a list of all barber services for a user.

    Args:
        user_id (int): The ID of the user.
        session (Session): The database session.

    Returns:
        List[UserService]: A list of user service instances.

    Raises:
        HTTPException: If no services are found for the user.
    """

    user_service = session.query(UserService).filter(UserService.user_id == user_id).all()
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return user_service

def get_id_user_service(id_service: int, user_id: int, session: Session) -> UserService:
    """Retrieve a specific barber service for a user.

    Args:
        id_service (int): The ID of the service.
        user_id (int): The ID of the user.
        session (Session): The database session.

    Returns:
        UserService: A user service instance.

    Raises:
        HTTPException: If the service is not found.
    """

    user_service = session.query(UserService).filter(UserService.service_id==id_service, UserService.user_id==user_id).first()
    if not user_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return user_service

def put_edit_user_service(id_service: int, user_service_edit_schema: UserServiceEditSchema, current_user: User, session: Session) -> UserService:
    """Edit an existing barber service for a user.

    Args:
        id_service (int): The ID of the service.
        user_service_edit_schema (UserServiceEditSchema): The schema of the edited user service.
        current_user (User): The current authenticated user.
        session (Session): The database session.

    Returns:
        UserService: The updated user service instance.
    """

    user_service = get_id_user_service(id_service, current_user.id, session)

    user_service.custom_price = user_service_edit_schema.custom_price
    user_service.custom_duration =  user_service_edit_schema.custom_duration

    session.commit()
    return user_service

def put_disable_user_service(id_service: int, current_user: User, session: Session) -> UserService:
    """Disable an existing barber service for a user.

    Args:
        id_service (int): The ID of the service.
        current_user (User): The current authenticated user.
        session (Session): The database session.

    Returns:
        UserService: The updated user service instance.
    """

    user_service = get_id_user_service(id_service, current_user.id, session)
    user_service.status = False

    session.commit()
    return user_service

def put_active_user_service(id_service: int, current_user: User, session: Session) -> UserService:
    """Enable an existing barber service for a user.

    Args:
        id_service (int): The ID of the service.
        current_user (User): The current authenticated user.
        session (Session): The database session.

    Returns:
        UserService: The updated user service instance.
    """

    user_service = get_id_user_service(id_service, current_user.id, session)
    user_service.status = True

    session.commit()
    return user_service