"""
Criar Tabelas Normalizadas usando SQLAlchemy - HullZero

Cria todas as tabelas normalizadas usando os modelos SQLAlchemy.
Mais confiável que executar SQL diretamente, especialmente para SQLite.
"""

from sqlalchemy import inspect
from .database import engine, init_db
from .models_normalized import Base as NormalizedBase

# Importar modelos de autenticação
try:
    from ..auth.models import Base as AuthBase
    AUTH_MODELS_AVAILABLE = True
except ImportError:
    AUTH_MODELS_AVAILABLE = False
    AuthBase = None


def create_normalized_tables():
    """
    Cria todas as tabelas normalizadas usando SQLAlchemy.
    """
    print("🔄 Criando tabelas normalizadas...")
    print(f"📊 Engine: {engine.url}")
    print("")
    
    # Verificar tabelas existentes
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    # Criar todas as tabelas normalizadas
    try:
        NormalizedBase.metadata.create_all(bind=engine)
        print("✅ Tabelas normalizadas criadas com sucesso!")
        
        # Criar tabelas de autenticação se disponíveis
        if AUTH_MODELS_AVAILABLE and AuthBase:
            AuthBase.metadata.create_all(bind=engine)
            print("✅ Tabelas de autenticação criadas com sucesso!")
        
        print("")
        
        # Verificar tabelas criadas
        inspector = inspect(engine)
        new_tables = set(inspector.get_table_names())
        created_tables = new_tables - existing_tables
        
        if created_tables:
            print(f"📋 Tabelas criadas ({len(created_tables)}):")
            for table in sorted(created_tables):
                print(f"   ✅ {table}")
        else:
            print("ℹ️  Todas as tabelas já existiam")
        
        print("")
        print(f"📊 Total de tabelas no banco: {len(new_tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Garantir que o banco base está inicializado
    init_db()
    
    # Criar tabelas normalizadas
    success = create_normalized_tables()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou. Verifique os erros acima.")

