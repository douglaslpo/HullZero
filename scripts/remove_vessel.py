import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import SessionLocal
from src.database.repositories import VesselRepository

def remove_vessel(vessel_name: str):
    print(f"🗑️  Removendo embarcação: {vessel_name}...")
    db = SessionLocal()
    
    try:
        # Buscar navio
        vessel = VesselRepository.get_by_name(db, vessel_name)
        if not vessel:
            print(f"❌ Navio '{vessel_name}' não encontrado.")
            return

        # Remover
        # Nota: O delete do repositório já faz commit
        success = VesselRepository.delete(db, vessel.id)
        
        if success:
            print(f"✅ Navio '{vessel_name}' removido com sucesso!")
        else:
            print(f"❌ Falha ao remover navio '{vessel_name}'.")
            
    except Exception as e:
        print(f"❌ Erro ao remover navio: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "NAVIO TESTE 1"
        
    remove_vessel(name)
