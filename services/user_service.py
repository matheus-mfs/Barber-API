from fastapi import HTTPException
from models import User, UserRole

def validate_admin(user_role):
    if user_role == UserRole.BARBER:
        raise HTTPException(status_code=400, detail="Acesso negado")
    
def validate_user_exists(user):
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    
def get_user_by_id(session, id_user, current_user):

    validate_admin(current_user.role)
    user = session.query(User).filter(User.id == id_user,User.tenant_id == current_user.tenant_id).first()
    validate_user_exists(user)

    return user

def list_users_service(session, current_user):

    validate_admin(current_user.role)
    users = session.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    validate_user_exists(users)

    return users

def update_user_service(session, id_user, user_edit_schema, current_user):

    if current_user.role == UserRole.BARBER and current_user.id != id_user:
        raise HTTPException(status_code=400, detail="Acesso negado")

    user = session.query(User).filter(User.id == id_user).first()

    validate_user_exists(user)

    user.name = user_edit_schema.name
    user.email = user_edit_schema.email

    session.commit()

    return user

def disable_user_service(session, id_user, current_user):

    validate_admin(current_user.role)
    user = session.query(User).filter(User.id == id_user).first()
    validate_user_exists(user)

    user.status = False
    session.commit()

    return user

def active_user_service(session, id_user, current_user):

    validate_admin(current_user.role)
    user = session.query(User).filter(User.id == id_user).first()
    validate_user_exists(user)

    user.status = True
    session.commit()

    return user