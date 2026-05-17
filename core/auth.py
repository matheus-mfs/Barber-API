from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings
from .database import get_session
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from models import User

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def check_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        dic_info = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id_user = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
        raise HTTPException(status_code=401, detail="Acesso Negado")
        
    return user

def create_token(id_user, duration_token=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + duration_token
    dic_info = {"sub": str(id_user), "exp": expiration_date}
    encode_token = jwt.encode(dic_info, settings.SECRET_KEY, settings.ALGORITHM)
    return encode_token

def authenticate_user(email, password, tenant, session):
    user = session.query(User).filter(User.email==email, User.tenant_id==tenant).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_account_service(session, user_schema, current_tenant):

    user = session.query(User).filter(User.email == user_schema.email, User.tenant_id == current_tenant.id).first()

    if user:
        raise HTTPException(status_code=400, detail="E-mail do usuario ja cadastrado")

    password_encrypted = bcrypt_context.hash(user_schema.password)

    new_user = User(current_tenant.id, user_schema.name, user_schema.email,
                    password_encrypted, user_schema.role, user_schema.status)

    session.add(new_user)
    session.commit()

    return new_user

def login_service(email, password, tenant_id, session):

    user = authenticate_user(email, password, tenant_id, session)

    if not user:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado ou credenciais invalidas")

    access_token = create_token(user.id)
    refresh_token = create_token(user.id, duration_token=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

def refresh_token_service(user):

    access_token = create_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }