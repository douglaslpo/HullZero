"""
Script para adicionar coluna photos_paths na tabela maintenance_events
"""
from sqlalchemy import text
from src.database.database import SessionLocal, init_db

def migrate():
    print("🔄 Adicionando coluna photos_paths...")
    db = SessionLocal()
    try:
        # Verificar se a coluna já existe
        result = db.execute(text("PRAGMA table_info(maintenance_events)"))
        columns = [row[1] for row in result]
        
        if 'photos_paths' not in columns:
            print("  ➕ Criando coluna photos_paths...")
            db.execute(text("ALTER TABLE maintenance_events ADD COLUMN photos_paths JSON"))
            db.commit()
            print("  ✅ Coluna criada com sucesso.")
        else:
            print("  ℹ️ Coluna já existe.")
            
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
