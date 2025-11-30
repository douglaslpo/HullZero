#!/usr/bin/env python3
"""
Script de Importação de Dados Reais - HullZero

Importa dados reais da pasta dados/ para o banco de dados.

Uso:
    python scripts/import_real_data.py
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db
from src.data.import_real_data import import_all_real_data


def main():
    """Função principal"""
    print("="*60)
    print("🚀 IMPORTADOR DE DADOS REAIS - HULLZERO")
    print("="*60)
    
    # Inicializar banco
    print("\n📊 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados inicializado")
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Importar todos os dados
        results = import_all_real_data(db)
        
        print("\n" + "="*60)
        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

