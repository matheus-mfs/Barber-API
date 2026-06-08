from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.services.permission_service import assign_barber_permissions, assign_owner_permissions
from .config import settings
from .database import get_session

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def check_token(
    token: str = Depends(oauth2_schema),
    session: Session = Depends(get_session),
) -> User:
    """Valida o token JWT e retorna o usuário autenticado.
    
    Args:
        token: Token JWT do header Authorization
        session: Sessão do banco de dados
        
    Returns:
        User: Usuário autenticado
        

    """
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Acesso Negado, verifique a validade do token",
        )
    
    user: Optional[User] = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Acesso Negado")
    
    return user

def create_token(
    user_id: int,
    duration_token: timedelta = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ),
) -> str:
    """Cria um token JWT para o usuário.
    
    Args:
        user_id: ID do usuário
        duration_token: Duração do token
        
    Returns:
        str: Token JWT codificado
    """
    expiration_date: datetime = datetime.now(timezone.utc) + duration_token
    payload: Dict[str, Any] = {"sub": str(user_id), "exp": expiration_date}
    encoded_token: str = jwt.encode(
        payload, settings.SECRET_KEY, settings.ALGORITHM
    )
    return encoded_token

def authenticate_user(
    email: str, password: str, tenant_id: int, session: Session
) -> Optional[User]:
    """Autentica um usuário verificando email e senha.
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        tenant_id: ID do tenant
        session: Sessão do banco de dados
        
    Returns:
        Optional[User]: Usuário autenticado ou None
    """
    user: Optional[User] = session.query(User).filter(
        User.email == email, User.tenant_id == tenant_id
    ).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password):
        return None
    return user

def create_account_service(
    session: Session, user_schema: Any, current_tenant: Any
) -> User:
    """Cria uma nova conta de usuário com permissões padrão.
    
    Ao criar um novo usuário, suas permissões são atribuídas automaticamente
    baseado no seu role (BARBER ou OWNER).
    
    Args:
        session: Sessão do banco de dados
        user_schema: Schema com dados do usuário
        current_tenant: Tenant atual
        
    Returns:
        User: Usuário criado com permissões atribuídas
        
    Raises:
        HTTPException: Se email já existe ou se houver erro ao atribuir permissões
    """
    existing_user: Optional[User] = session.query(User).filter(
        User.email == user_schema.email,
        User.tenant_id == current_tenant.id,
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400, detail="E-mail do usuario ja cadastrado"
        )

    hashed_password: str = bcrypt_context.hash(user_schema.password)
    new_user: User = User(
        current_tenant.id,
        user_schema.name,
        user_schema.email,
        hashed_password,
        user_schema.role,
        user_schema.status,
    )

    session.add(new_user)
    session.commit()
    
    # Atribui permissões padrão baseado no role
    if new_user.role == UserRole.BARBER:
        assign_barber_permissions(new_user, session)
    elif new_user.role == UserRole.OWNER:
        assign_owner_permissions(new_user, session)

    return new_user

def login_service(
    email: str, password: str, tenant_id: int, session: Session
) -> Dict[str, str]:
    """Realiza o login do usuário retornando tokens.
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        tenant_id: ID do tenant
        session: Sessão do banco de dados
        
    Returns:
        Dict[str, str]: Dicionário com access_token, refresh_token e token_type
    """
    user: Optional[User] = authenticate_user(email, password, tenant_id, session)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Usuario nao encontrado ou credenciais invalidas",
        )

    access_token: str = create_token(user.id)
    refresh_token: str = create_token(
        user.id, duration_token=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }

def refresh_token_service(user: User) -> Dict[str, str]:
    """Renova o token de acesso do usuário.
    
    Args:
        user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Novo access_token e token_type
    """
    access_token: str = create_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

def put_reset_password(new_password: str, current_user: User, session: Session):
    """Renova o token de acesso do usuário.
    
    Args:
        new_password: Nova senha do usuario
        user: Usuário autenticado
        session: Sessão do banco de dados
    """

    hashed_password: str = bcrypt_context.hash(new_password)
    current_user.password = hashed_password
    session.commit()
    
