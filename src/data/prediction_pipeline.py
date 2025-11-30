"""
Pipeline de Predição de Bioincrustação - HullZero

Gera predições de bioincrustação baseadas em dados operacionais reais.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database.models import Vessel, OperationalData, FoulingData
from ..database.repositories import (
    VesselRepository,
    OperationalDataRepository,
    FoulingDataRepository
)
from ..models.fouling_prediction import predict_fouling, VesselFeatures
from ..models.advanced_fouling_prediction import (
    predict_advanced_fouling,
    AdvancedVesselFeatures
)


class PredictionPipeline:
    """
    Pipeline para gerar predições de bioincrustação baseadas em dados operacionais reais.
    """
    
    @staticmethod
    def get_latest_operational_data(
        db: Session,
        vessel_id: str,
        days: int = 30
    ) -> Optional[OperationalData]:
        """
        Obtém os dados operacionais mais recentes de uma embarcação.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        operational = db.query(OperationalData).filter(
            and_(
                OperationalData.vessel_id == vessel_id,
                OperationalData.timestamp >= cutoff_date
            )
        ).order_by(OperationalData.timestamp.desc()).first()
        
        return operational
    
    @staticmethod
    def get_operational_stats(
        db: Session,
        vessel_id: str,
        days: int = 30
    ) -> Dict:
        """
        Calcula estatísticas operacionais de uma embarcação.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        operational_data = db.query(OperationalData).filter(
            and_(
                OperationalData.vessel_id == vessel_id,
                OperationalData.timestamp >= cutoff_date
            )
        ).all()
        
        if not operational_data:
            return {}
        
        # Calcular médias
        speeds = [d.speed_knots for d in operational_data if d.speed_knots]
        consumptions = [d.fuel_consumption_kg_h for d in operational_data if d.fuel_consumption_kg_h]
        temps = [d.water_temperature_c for d in operational_data if d.water_temperature_c]
        salinities = [d.salinity_psu for d in operational_data if d.salinity_psu]
        
        stats = {
            "avg_speed_knots": sum(speeds) / len(speeds) if speeds else None,
            "avg_fuel_consumption_kg_h": sum(consumptions) / len(consumptions) if consumptions else None,
            "avg_water_temperature_c": sum(temps) / len(temps) if temps else None,
            "avg_salinity_psu": sum(salinities) / len(salinities) if salinities else None,
            "total_records": len(operational_data),
            "days_covered": days,
        }
        
        return stats
    
    @staticmethod
    def get_last_cleaning_date(
        db: Session,
        vessel_id: str
    ) -> Optional[datetime]:
        """
        Obtém data da última limpeza (manutenção do tipo cleaning).
        """
        from ..database.models import MaintenanceEvent
        
        last_cleaning = db.query(MaintenanceEvent).filter(
            and_(
                MaintenanceEvent.vessel_id == vessel_id,
                MaintenanceEvent.event_type == "cleaning",
                MaintenanceEvent.status == "completed"
            )
        ).order_by(MaintenanceEvent.end_date.desc()).first()
        
        return last_cleaning.end_date if last_cleaning and last_cleaning.end_date else None
    
    @staticmethod
    def predict_fouling_from_real_data(
        db: Session,
        vessel_id: str,
        use_advanced: bool = True
    ) -> Optional[FoulingData]:
        """
        Gera predição de bioincrustação baseada em dados operacionais reais.
        
        Args:
            db: Sessão do banco de dados
            vessel_id: ID da embarcação
            use_advanced: Se True, usa modelo avançado
            
        Returns:
            FoulingData criado ou None se não houver dados suficientes
        """
        # Obter embarcação
        vessel = VesselRepository.get_by_id(db, vessel_id)
        if not vessel:
            print(f"⚠️  Embarcação {vessel_id} não encontrada")
            return None
        
        # Obter dados operacionais recentes
        operational = PredictionPipeline.get_latest_operational_data(db, vessel_id)
        if not operational:
            print(f"⚠️  Sem dados operacionais para {vessel.name}")
            return None
        
        # Obter estatísticas
        stats = PredictionPipeline.get_operational_stats(db, vessel_id)
        
        # Obter última limpeza
        last_cleaning = PredictionPipeline.get_last_cleaning_date(db, vessel_id)
        time_since_cleaning_days = (
            (datetime.utcnow() - last_cleaning).days
            if last_cleaning
            else 180  # Default: 6 meses
        )
        
        try:
            if use_advanced:
                # Usar modelo avançado
                try:
                    features = AdvancedVesselFeatures(
                        vessel_id=vessel_id,
                        time_since_cleaning_days=time_since_cleaning_days,
                        water_temperature_c=operational.water_temperature_c or stats.get("avg_water_temperature_c", 25.0),
                        salinity_psu=operational.salinity_psu or stats.get("avg_salinity_psu", 35.0),
                        time_in_port_hours=0,  # Calcular baseado em dados operacionais
                        average_speed_knots=operational.speed_knots or stats.get("avg_speed_knots", 12.0),
                        route_region="Brazil_Coast",  # Default
                        paint_type=vessel.paint_type or "AFS",
                        vessel_type=vessel.vessel_type or "tanker",
                        hull_area_m2=vessel.hull_area_m2 or 10000.0,
                        # Campos adicionais (se disponíveis no modelo)
                        latitude=operational.latitude,
                        longitude=operational.longitude,
                        fuel_consumption_kg_h=operational.fuel_consumption_kg_h or stats.get("avg_fuel_consumption_kg_h"),
                        engine_power_kw=operational.engine_power_kw or vessel.engine_power_kw,
                    )
                    
                    prediction = predict_advanced_fouling(features)
                except Exception as e:
                    # Fallback para modelo básico se avançado falhar
                    print(f"⚠️  Modelo avançado falhou, usando modelo básico: {e}")
                    use_advanced = False
            else:
                # Usar modelo básico
                features = VesselFeatures(
                    vessel_id=vessel_id,
                    time_since_cleaning_days=time_since_cleaning_days,
                    water_temperature_c=operational.water_temperature_c or 25.0,
                    salinity_psu=operational.salinity_psu or 35.0,
                    time_in_port_hours=0,
                    average_speed_knots=operational.speed_knots or 12.0,
                    route_region="Brazil_Coast",
                    paint_type=vessel.paint_type or "AFS",
                    vessel_type=vessel.vessel_type or "tanker",
                    hull_area_m2=vessel.hull_area_m2 or 10000.0,
                )
                
                prediction = predict_fouling(features)
            
            # Criar registro de fouling_data
            fouling_data = {
                "vessel_id": vessel_id,
                "timestamp": datetime.utcnow(),
                "estimated_thickness_mm": prediction.estimated_thickness_mm,
                "estimated_roughness_um": prediction.estimated_roughness_um,
                "fouling_severity": prediction.fouling_severity,
                "confidence_score": prediction.confidence_score,
                "predicted_fuel_impact_percent": prediction.predicted_fuel_impact_percent,
                "predicted_co2_impact_kg": prediction.predicted_co2_impact_kg,
                "model_type": "advanced" if use_advanced else "hybrid",
                "model_version": "1.0",
                "features": {
                    "time_since_cleaning_days": time_since_cleaning_days,
                    "water_temperature_c": features.water_temperature_c,
                    "salinity_psu": features.salinity_psu,
                    "average_speed_knots": features.average_speed_knots,
                    "operational_data_used": True,
                }
            }
            
            fouling_record = FoulingDataRepository.create(db, fouling_data)
            print(f"✅ Predição gerada para {vessel.name}: {prediction.fouling_severity} ({prediction.estimated_thickness_mm:.2f}mm)")
            
            return fouling_record
            
        except Exception as e:
            print(f"❌ Erro ao gerar predição para {vessel.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def generate_predictions_for_all_vessels(
        db: Session,
        use_advanced: bool = True,
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Gera predições para todas as embarcações com dados operacionais.
        
        Returns:
            Dict com estatísticas: {"success": X, "failed": Y, "skipped": Z}
        """
        vessels = VesselRepository.get_all(db)
        if limit:
            vessels = vessels[:limit]
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        print(f"\n🚀 Gerando predições para {len(vessels)} embarcações...")
        
        for vessel in vessels:
            # Verificar se tem dados operacionais
            operational = PredictionPipeline.get_latest_operational_data(db, vessel.id, days=90)
            
            if not operational:
                print(f"⏭️  Pulando {vessel.name} - sem dados operacionais")
                stats["skipped"] += 1
                continue
            
            result = PredictionPipeline.predict_fouling_from_real_data(
                db, vessel.id, use_advanced=use_advanced
            )
            
            if result:
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        print(f"\n📊 Estatísticas:")
        print(f"  ✅ Sucesso: {stats['success']}")
        print(f"  ❌ Falhas: {stats['failed']}")
        print(f"  ⏭️  Pulados: {stats['skipped']}")
        
        return stats

