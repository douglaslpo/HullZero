"""
Pipeline de Validação - HullZero

Valida predições de bioincrustação comparando com dados reais de consumo.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..database.models import Vessel, OperationalData, FoulingData
from ..database.repositories import (
    VesselRepository,
    OperationalDataRepository,
    FoulingDataRepository
)


class ValidationPipeline:
    """
    Pipeline para validar predições comparando com dados reais.
    """
    
    @staticmethod
    def get_real_consumption_stats(
        db: Session,
        vessel_id: str,
        days: int = 30
    ) -> Dict:
        """
        Obtém estatísticas de consumo real de uma embarcação.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Buscar dados operacionais com consumo
        operational_data = db.query(OperationalData).filter(
            and_(
                OperationalData.vessel_id == vessel_id,
                OperationalData.timestamp >= cutoff_date,
                OperationalData.fuel_consumption_kg_h.isnot(None)
            )
        ).all()
        
        if not operational_data:
            return {
                "avg_consumption_kg_h": None,
                "min_consumption_kg_h": None,
                "max_consumption_kg_h": None,
                "total_records": 0,
                "days_covered": days,
            }
        
        consumptions = [d.fuel_consumption_kg_h for d in operational_data if d.fuel_consumption_kg_h]
        
        return {
            "avg_consumption_kg_h": sum(consumptions) / len(consumptions) if consumptions else None,
            "min_consumption_kg_h": min(consumptions) if consumptions else None,
            "max_consumption_kg_h": max(consumptions) if consumptions else None,
            "total_records": len(operational_data),
            "days_covered": days,
        }
    
    @staticmethod
    def get_predicted_impact(
        db: Session,
        vessel_id: str,
        days: int = 30
    ) -> Optional[Dict]:
        """
        Obtém impacto predito de bioincrustação no consumo.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Buscar predição mais recente
        fouling = db.query(FoulingData).filter(
            and_(
                FoulingData.vessel_id == vessel_id,
                FoulingData.timestamp >= cutoff_date
            )
        ).order_by(FoulingData.timestamp.desc()).first()
        
        if not fouling:
            return None
        
        return {
            "predicted_fuel_impact_percent": fouling.predicted_fuel_impact_percent,
            "predicted_co2_impact_kg": fouling.predicted_co2_impact_kg,
            "fouling_thickness_mm": fouling.estimated_thickness_mm,
            "fouling_severity": fouling.fouling_severity,
            "confidence_score": fouling.confidence_score,
            "timestamp": fouling.timestamp,
        }
    
    @staticmethod
    def validate_prediction_vs_reality(
        db: Session,
        vessel_id: str,
        days: int = 30
    ) -> Dict:
        """
        Valida predição comparando com dados reais de consumo.
        
        Returns:
            Dict com métricas de validação
        """
        vessel = VesselRepository.get_by_id(db, vessel_id)
        if not vessel:
            return {"error": "Vessel not found"}
        
        # Obter consumo real
        real_stats = ValidationPipeline.get_real_consumption_stats(db, vessel_id, days)
        
        # Obter predição
        predicted = ValidationPipeline.get_predicted_impact(db, vessel_id, days)
        
        if not real_stats.get("avg_consumption_kg_h"):
            return {
                "vessel_id": vessel_id,
                "vessel_name": vessel.name,
                "status": "no_real_data",
                "message": "Sem dados reais de consumo para validação",
            }
        
        if not predicted:
            return {
                "vessel_id": vessel_id,
                "vessel_name": vessel.name,
                "status": "no_prediction",
                "message": "Sem predição de bioincrustação",
            }
        
        # Calcular consumo esperado (base) e consumo com impacto
        base_consumption = real_stats["avg_consumption_kg_h"]
        impact_percent = predicted["predicted_fuel_impact_percent"] or 0
        expected_consumption_with_fouling = base_consumption * (1 + impact_percent / 100)
        
        # Calcular diferença
        actual_consumption = real_stats["avg_consumption_kg_h"]
        difference = actual_consumption - base_consumption
        difference_percent = (difference / base_consumption * 100) if base_consumption else 0
        
        # Avaliar se a predição faz sentido
        prediction_error = abs(difference_percent - impact_percent)
        
        validation_result = {
            "vessel_id": vessel_id,
            "vessel_name": vessel.name,
            "status": "validated",
            "period_days": days,
            
            # Dados reais
            "real_avg_consumption_kg_h": base_consumption,
            "real_min_consumption_kg_h": real_stats.get("min_consumption_kg_h"),
            "real_max_consumption_kg_h": real_stats.get("max_consumption_kg_h"),
            "real_total_records": real_stats.get("total_records"),
            
            # Predição
            "predicted_fuel_impact_percent": impact_percent,
            "predicted_co2_impact_kg": predicted.get("predicted_co2_impact_kg"),
            "predicted_fouling_thickness_mm": predicted.get("fouling_thickness_mm"),
            "predicted_fouling_severity": predicted.get("fouling_severity"),
            "prediction_confidence": predicted.get("confidence_score"),
            
            # Validação
            "expected_consumption_with_fouling_kg_h": expected_consumption_with_fouling,
            "actual_consumption_kg_h": actual_consumption,
            "consumption_difference_kg_h": difference,
            "consumption_difference_percent": difference_percent,
            "prediction_error_percent": prediction_error,
            
            # Avaliação
            "validation_score": max(0, 100 - prediction_error),  # Score de 0-100
            "is_valid": prediction_error < 20,  # Considera válido se erro < 20%
        }
        
        return validation_result
    
    @staticmethod
    def validate_all_vessels(
        db: Session,
        days: int = 30,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Valida predições para todas as embarcações.
        
        Returns:
            Lista de resultados de validação
        """
        vessels = VesselRepository.get_all(db)
        if limit:
            vessels = vessels[:limit]
        
        results = []
        
        print(f"\n🔍 Validando predições para {len(vessels)} embarcações...")
        
        for vessel in vessels:
            result = ValidationPipeline.validate_prediction_vs_reality(
                db, vessel.id, days
            )
            results.append(result)
            
            if result.get("status") == "validated":
                score = result.get("validation_score", 0)
                is_valid = result.get("is_valid", False)
                status_icon = "✅" if is_valid else "⚠️"
                print(f"{status_icon} {vessel.name}: Score {score:.1f}% (Erro: {result.get('prediction_error_percent', 0):.1f}%)")
            elif result.get("status") == "no_real_data":
                print(f"⏭️  {vessel.name}: Sem dados reais")
            elif result.get("status") == "no_prediction":
                print(f"⏭️  {vessel.name}: Sem predição")
        
        # Estatísticas gerais
        validated = [r for r in results if r.get("status") == "validated"]
        if validated:
            avg_score = sum(r.get("validation_score", 0) for r in validated) / len(validated)
            valid_count = sum(1 for r in validated if r.get("is_valid", False))
            
            print(f"\n📊 Estatísticas de Validação:")
            print(f"  ✅ Validações realizadas: {len(validated)}")
            print(f"  ✅ Predições válidas (erro < 20%): {valid_count}/{len(validated)}")
            print(f"  📈 Score médio: {avg_score:.1f}%")
        
        return results

