from fastapi import APIRouter, Depends, HTTPException
from core.auth import check_token
from core.database import get_session
from sqlalchemy.orm import Session
from schemas import TenantSchema
from models import User, Tenant
from slugify import slugify


router = APIRouter(prefix="/tenants", tags=["tenants"], dependencies=[Depends(check_token)])

'''
    Criar autentificação para que apenas devs possam alterar, ou criar um super admin 

'''

@router.post("/create-tenant")
def create_tenant(tenant_schema: TenantSchema, session: Session = Depends(get_session), current_user : User = Depends(check_token)):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    slug = slugify(tenant_schema.name)
    tenant = Tenant(tenant_schema.name, slug, tenant_schema.service_duration, tenant_schema.status)
    session.add(tenant)
    session.commit()
    
    return{"message":"Tenant criado com sucesso"}

@router.get("/search-tenant/{id_tenant}")
def search_tenant(id_tenant: int , session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    tenant = session.query(Tenant).filter(Tenant.id==id_tenant).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    return tenant

@router.put("/edit-tenant/{id_tenant}")
def atualizar_tenant(id_tenant: int, tenant_schema: TenantSchema, session : Session = Depends(get_session), current_user : User = Depends(check_token)):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    tenant = session.query(Tenant).filter(Tenant.id==id_tenant).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    tenant.name = tenant_schema.name
    tenant.status = tenant_schema.status

    session.commit()

    return{"mensagem":"Informações atualizadas"}

