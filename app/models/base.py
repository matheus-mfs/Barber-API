"""Base model para SQLAlchemy."""
from app.core.database import Base

__all__ = ["Base"]


# criar a migração: alembic revision --autogenerate -m "menssagem"
#executar a migração: alembic upgrade head