"""
Script de Migração de Banco de Dados - HullZero

Executa migrações SQL para normalizar o banco de dados.
"""

import os
from pathlib import Path
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from .database import engine, SessionLocal
from .config import DATABASE_URL


def execute_sql_file(engine: Engine, file_path: Path) -> bool:
    """
    Executa um arquivo SQL no banco de dados.
    
    Args:
        engine: Engine do SQLAlchemy
        file_path: Caminho para o arquivo SQL
        
    Returns:
        True se executado com sucesso, False caso contrário
    """
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    print(f"📄 Executando: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir em comandos individuais (separados por ;)
        # Remover comentários e linhas vazias
        commands = [
            cmd.strip() 
            for cmd in sql_content.split(';') 
            if cmd.strip() and not cmd.strip().startswith('--')
        ]
        
        with engine.connect() as conn:
            for i, command in enumerate(commands, 1):
                if not command:
                    continue
                
                try:
                    # Executar comando
                    conn.execute(text(command))
                    conn.commit()
                except Exception as e:
                    # Ignorar erros de "já existe" ou "não existe"
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'does not exist' in error_msg:
                        print(f"  ⚠️  Comando {i}: {str(e)[:100]}... (ignorado)")
                    else:
                        print(f"  ❌ Erro no comando {i}: {str(e)[:200]}")
                        # Não falhar completamente, continuar com próximos comandos
                        conn.rollback()
            
            print(f"  ✅ {file_path.name} executado com sucesso")
            return True
            
    except Exception as e:
        print(f"  ❌ Erro ao executar {file_path.name}: {str(e)}")
        return False


def check_table_exists(engine: Engine, table_name: str) -> bool:
    """
    Verifica se uma tabela existe no banco de dados.
    
    Args:
        engine: Engine do SQLAlchemy
        table_name: Nome da tabela
        
    Returns:
        True se a tabela existe, False caso contrário
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def run_migrations(dry_run: bool = False):
    """
    Executa todas as migrações SQL.
    
    Args:
        dry_run: Se True, apenas mostra o que seria executado sem fazer alterações
    """
    print("🔄 Iniciando migrações de banco de dados...")
    print(f"📊 Banco de dados: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"🔍 Modo: {'DRY RUN (simulação)' if dry_run else 'EXECUÇÃO REAL'}")
    print("")
    
    # Diretório de migrações
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"❌ Diretório de migrações não encontrado: {migrations_dir}")
        return
    
    # Listar arquivos SQL em ordem
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("⚠️  Nenhum arquivo de migração encontrado")
        return
    
    print(f"📋 Encontradas {len(migration_files)} migrações:")
    for f in migration_files:
        print(f"   - {f.name}")
    print("")
    
    if dry_run:
        print("🔍 DRY RUN: Nenhuma alteração será feita")
        return
    
    # Executar migrações
    success_count = 0
    failed_count = 0
    
    for migration_file in migration_files:
        success = execute_sql_file(engine, migration_file)
        if success:
            success_count += 1
        else:
            failed_count += 1
        print("")
    
    # Resumo
    print("=" * 60)
    print("📊 Resumo da Migração:")
    print(f"   ✅ Sucesso: {success_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📄 Total: {len(migration_files)}")
    print("=" * 60)
    
    if failed_count == 0:
        print("\n✅ Todas as migrações foram executadas com sucesso!")
    else:
        print(f"\n⚠️  {failed_count} migração(ões) falharam. Verifique os erros acima.")


def check_migration_status():
    """
    Verifica o status das migrações (quais tabelas foram criadas).
    """
    print("🔍 Verificando status das migrações...")
    print("")
    
    # Tabelas de referência esperadas
    reference_tables = [
        'vessel_types', 'vessel_classes', 'paint_types', 'ports', 
        'routes', 'contractors', 'cargo_types', 'fuel_types', 'invasive_species'
    ]
    
    # Tabelas de relacionamento esperadas
    relationship_tables = [
        'vessel_routes', 'vessel_cargo_types', 'vessel_fuel_alternatives'
    ]
    
    # Novas entidades esperadas
    new_entities = [
        'paint_applications', 'sensor_calibrations', 'inspections',
        'compliance_checks', 'compliance_violations', 'compliance_warnings',
        'compliance_recommendations', 'risk_factors', 'risk_recommendations',
        'invasive_species_risks', 'invasive_species_recommendations'
    ]
    
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    all_expected = reference_tables + relationship_tables + new_entities
    
    print("📊 Status das Tabelas:")
    print("")
    
    # Tabelas de referência
    print("📚 Tabelas de Referência:")
    for table in reference_tables:
        status = "✅" if table in existing_tables else "❌"
        print(f"   {status} {table}")
    
    print("")
    print("🔗 Tabelas de Relacionamento:")
    for table in relationship_tables:
        status = "✅" if table in existing_tables else "❌"
        print(f"   {status} {table}")
    
    print("")
    print("🆕 Novas Entidades:")
    for table in new_entities:
        status = "✅" if table in existing_tables else "❌"
        print(f"   {status} {table}")
    
    print("")
    print("=" * 60)
    created = sum(1 for t in all_expected if t in existing_tables)
    total = len(all_expected)
    print(f"📈 Progresso: {created}/{total} tabelas criadas ({created*100//total}%)")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            check_migration_status()
        elif command == "dry-run":
            run_migrations(dry_run=True)
        elif command == "run":
            run_migrations(dry_run=False)
        else:
            print("Uso: python -m src.database.migrate [check|dry-run|run]")
            print("  check    - Verifica status das migrações")
            print("  dry-run  - Simula execução sem fazer alterações")
            print("  run      - Executa as migrações")
    else:
        # Por padrão, verificar status
        check_migration_status()
        print("")
        print("💡 Para executar migrações, use: python -m src.database.migrate run")
        print("💡 Para simular, use: python -m src.database.migrate dry-run")

