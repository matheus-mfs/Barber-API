from fastapi import HTTPException
from slugify import slugify
from models import Tenant, UserRole

def validate_dev_permission(current_user):

    if current_user.role != UserRole.DEV:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
def get_tenant_by_id(session, tenant_id, current_user):

    validate_dev_permission(current_user)

    tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant nao encontrado")

    return tenant

def create_tenant_service(session, tenant_schema, current_user):

    validate_dev_permission(current_user)

    slug = slugify(tenant_schema.name)

    tenant = Tenant(tenant_schema.name, slug, tenant_schema.status)

    session.add(tenant)

    session.commit()

    return tenant

def update_tenant_service(session, tenant_id, tenant_schema, current_user):

    tenant = get_tenant_by_id(session=session, tenant_id=tenant_id, current_user=current_user )

    tenant.name = tenant_schema.name
    tenant.status = tenant_schema.status

    session.commit()

    return tenant