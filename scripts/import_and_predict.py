#!/usr/bin/env python3
"""
Script de Importação e Predição - HullZero

Importa dados reais e gera predições de bioincrustação.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db
from src.data.import_real_data import import_all_real_data
from src.data.prediction_pipeline import PredictionPipeline
from src.data.validation_pipeline import ValidationPipeline


def main():
    """
    Executa importação de dados reais e gera predições.
    """
    print("="*80)
    print("🚀 HullZero - Importação e Predição de Dados Reais")
    print("="*80)
    
    # Inicializar banco
    db = SessionLocal()
    try:
        # Inicializar tabelas se necessário
        init_db()
        print("✅ Banco de dados inicializado\n")
        
        # Fase 1: Importar dados reais
        print("="*80)
        print("FASE 1: Importação de Dados Reais")
        print("="*80)
        
        import_results = import_all_real_data(db)
        
        print("\n" + "="*80)
        print("FASE 2: Geração de Predições de Bioincrustação")
        print("="*80)
        
        # Fase 2: Gerar predições
        prediction_stats = PredictionPipeline.generate_predictions_for_all_vessels(
            db, use_advanced=True
        )
        
        print("\n" + "="*80)
        print("FASE 3: Validação de Predições")
        print("="*80)
        
        # Fase 3: Validar predições
        validation_results = ValidationPipeline.validate_all_vessels(db, days=30)
        
        print("\n" + "="*80)
        print("✅ PROCESSO CONCLUÍDO")
        print("="*80)
        print(f"\n📊 Resumo:")
        print(f"  - Dados importados: {sum(import_results.get('ais_data', {}).values()) + import_results.get('consumption_data', 0) + import_results.get('events_data', 0)} registros")
        print(f"  - Predições geradas: {prediction_stats.get('success', 0)}")
        print(f"  - Validações realizadas: {len([r for r in validation_results if r.get('status') == 'validated'])}")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

