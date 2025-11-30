"""
Script para inicializar dados de autenticação - HullZero

Cria papéis, permissões e usuário administrador inicial.
"""

import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from src.database import SessionLocal, init_db
from src.auth.init_roles import init_permissions, init_roles
from src.auth.models import User, Role
from src.auth.auth_service import AuthService
from src.auth.models import UserRoleEnum


def create_admin_user(db: Session, username: str = "admin", password: str = "admin123"):
    """Cria usuário administrador inicial"""
    # Verificar se já existe
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Usuário '{username}' já existe. Pulando criação.")
        return existing
    
    # Criar usuário
    hashed_password = AuthService.get_password_hash(password)
    admin_user = User(
        username=username,
        email=f"{username}@hullzero.com",
        full_name="Administrador do Sistema",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        employee_id="ADMIN001",
        department="TI",
        position="Administrador de Sistema"
    )
    
    db.add(admin_user)
    db.flush()
    
    # Atribuir papel de administrador
    admin_role = db.query(Role).filter(Role.id == UserRoleEnum.ADMINISTRADOR_SISTEMA.value).first()
    if admin_role:
        admin_user.roles.append(admin_role)
    
    db.commit()
    print(f"✓ Usuário administrador criado: {username}")
    print(f"  Senha padrão: {password}")
    print(f"  ⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")
    return admin_user


def main():
    """Função principal"""
    print("=" * 60)
    print("Inicialização de Autenticação e Autorização")
    print("=" * 60)
    print()
    
    # Inicializar banco de dados
    print("Inicializando banco de dados...")
    init_db()
    print("✓ Banco de dados inicializado")
    print()
    
    # Criar sessão
    db = SessionLocal()
    try:
        # Inicializar permissões e papéis
        print("Criando permissões...")
        init_permissions(db)
        print()
        
        print("Criando papéis e atribuindo permissões...")
        init_roles(db)
        print()
        
        # Criar usuário administrador
        print("Criando usuário administrador...")
        create_admin_user(db)
        print()
        
        print("=" * 60)
        print("✓ Inicialização concluída com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Erro durante inicialização: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

