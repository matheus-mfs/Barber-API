"""
Script para seed de permissões no banco de dados.

Execução:
    python -m app.scripts.seed_permissions
"""
from app.models import Permission, PermissionRole
from app.core.database import Session


def seed_permissions():
    """Cria todas as permissões no banco de dados."""
    session = Session()
    
    print("🌱 Iniciando seed de permissões...")
    
    created_count = 0
    already_exists_count = 0
    
    for permission_role in PermissionRole:
        # Verifica se já existe
        existing = session.query(Permission).filter(
            Permission.name == permission_role
        ).first()
        
        if existing:
            already_exists_count += 1
            print(f"  ✓ {permission_role.value} (já existe)")
        else:
            # Cria a permissão
            permission = Permission(name=permission_role)
            session.add(permission)
            created_count += 1
            print(f"  ✅ {permission_role.value} (criada)")
    
    # Commit de todas as permissões
    session.commit()
    session.close()
    
    print(f"\n✨ Seed concluída!")
    print(f"  - Permissões criadas: {created_count}")
    print(f"  - Permissões já existentes: {already_exists_count}")
    print(f"  - Total: {len(PermissionRole)}")


if __name__ == "__main__":
    seed_permissions()
