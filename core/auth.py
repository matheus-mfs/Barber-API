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