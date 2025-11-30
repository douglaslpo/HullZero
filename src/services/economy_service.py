"""
Serviço de Cálculo de Economia - HullZero

Este módulo calcula economia acumulada baseada na redução de consumo
de combustível atribuível à gestão de bioincrustação.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.models.fuel_impact import calculate_fuel_impact, ConsumptionFeatures, FuelImpactResult


@dataclass
class EconomyPeriod:
    """Período de economia"""
    start_date: datetime
    end_date: datetime
    total_fuel_saved_kg: float
    total_economy_brl: float
    average_daily_economy_brl: float
    number_of_days: int


@dataclass
class VesselEconomy:
    """Economia por embarcação"""
    vessel_id: str
    period: EconomyPeriod
    fuel_impact_records: List[FuelImpactResult]


@dataclass
class FleetEconomy:
    """Economia da frota"""
    total_vessels: int
    period: EconomyPeriod
    vessel_economies: List[VesselEconomy]
    total_fuel_saved_kg: float
    total_economy_brl: float


class EconomyService:
    """
    Serviço para cálculo de economia acumulada.
    
    A economia é calculada como a diferença entre o consumo real
    e o consumo que teria ocorrido sem gestão de bioincrustação.
    """
    
    # Preço do combustível (R$/kg) - pode ser configurável
    DEFAULT_FUEL_PRICE_BRL_PER_KG = 3.5  # R$ 3,50/kg (aproximadamente R$ 3.500/tonelada)
    
    # Fator de emissão CO₂ (kg CO₂ por kg de combustível)
    CO2_EMISSION_FACTOR = 3.15
    
    def __init__(self, fuel_price_brl_per_kg: Optional[float] = None):
        self.fuel_price = fuel_price_brl_per_kg or self.DEFAULT_FUEL_PRICE_BRL_PER_KG
    
    def calculate_accumulated_economy(
        self,
        vessel_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        fuel_consumption_data: List[Dict],
        fouling_predictions: List[Dict]
    ) -> FleetEconomy:
        """
        Calcula economia acumulada para um período.
        
        Args:
            vessel_ids: Lista de IDs de embarcações
            start_date: Data de início
            end_date: Data de fim
            fuel_consumption_data: Dados de consumo de combustível
                [{"vessel_id": str, "timestamp": datetime, "consumption_kg_h": float, ...}, ...]
            fouling_predictions: Predições de bioincrustação
                [{"vessel_id": str, "timestamp": datetime, "fouling_mm": float, ...}, ...]
                
        Returns:
            Economia da frota
        """
        vessel_economies = []
        total_fuel_saved = 0.0
        total_economy = 0.0
        
        for vessel_id in vessel_ids:
            vessel_economy = self._calculate_vessel_economy(
                vessel_id,
                start_date,
                end_date,
                fuel_consumption_data,
                fouling_predictions
            )
            vessel_economies.append(vessel_economy)
            total_fuel_saved += vessel_economy.period.total_fuel_saved_kg
            total_economy += vessel_economy.period.total_economy_brl
        
        period = EconomyPeriod(
            start_date=start_date,
            end_date=end_date,
            total_fuel_saved_kg=total_fuel_saved,
            total_economy_brl=total_economy,
            average_daily_economy_brl=total_economy / max(1, (end_date - start_date).days),
            number_of_days=(end_date - start_date).days
        )
        
        return FleetEconomy(
            total_vessels=len(vessel_ids),
            period=period,
            vessel_economies=vessel_economies,
            total_fuel_saved_kg=total_fuel_saved,
            total_economy_brl=total_economy
        )
    
    def _calculate_vessel_economy(
        self,
        vessel_id: str,
        start_date: datetime,
        end_date: datetime,
        fuel_consumption_data: List[Dict],
        fouling_predictions: List[Dict]
    ) -> VesselEconomy:
        """
        Calcula economia para uma embarcação.
        """
        # Filtrar dados da embarcação
        vessel_fuel_data = [
            d for d in fuel_consumption_data
            if d.get("vessel_id") == vessel_id
            and start_date <= d.get("timestamp") <= end_date
        ]
        
        vessel_fouling_data = {
            pred["timestamp"]: pred
            for pred in fouling_predictions
            if pred.get("vessel_id") == vessel_id
            and start_date <= pred.get("timestamp") <= end_date
        }
        
        fuel_impact_records = []
        total_fuel_saved_kg = 0.0
        
        for fuel_record in vessel_fuel_data:
            timestamp = fuel_record.get("timestamp")
            
            # Obter predição de bioincrustação mais próxima
            fouling_pred = self._get_closest_fouling_prediction(timestamp, vessel_fouling_data)
            
            if fouling_pred:
                # Calcular impacto no combustível
                consumption_features = ConsumptionFeatures(
                    vessel_id=vessel_id,
                    speed_knots=fuel_record.get("speed_knots", 12.0),
                    engine_power_kw=fuel_record.get("engine_power_kw", 5000.0),
                    rpm=fuel_record.get("rpm", 120),
                    water_temperature_c=fuel_record.get("water_temperature_c", 25.0),
                    wind_speed_knots=fuel_record.get("wind_speed_knots", 15.0),
                    wave_height_m=fuel_record.get("wave_height_m", 2.0),
                    current_speed_knots=fuel_record.get("current_speed_knots", 1.0),
                    vessel_load_percent=fuel_record.get("vessel_load_percent", 80.0),
                    fouling_thickness_mm=fouling_pred.get("fouling_mm", 0.0),
                    fouling_roughness_um=fouling_pred.get("roughness_um", 0.0),
                    hull_area_m2=fuel_record.get("hull_area_m2", 5000.0),
                    vessel_type=fuel_record.get("vessel_type", "Tanker")
                )
                
                fuel_impact = calculate_fuel_impact(consumption_features)
                fuel_impact_records.append(fuel_impact)
                
                # Economia = impacto evitado (se tivéssemos limpeza preventiva)
                # Assumindo que a gestão de bioincrustação reduziu o impacto
                fuel_saved = fuel_impact.delta_fuel_kg_per_hour * fuel_record.get("hours_operating", 1.0)
                total_fuel_saved_kg += max(0, fuel_saved)
        
        total_economy_brl = total_fuel_saved_kg * self.fuel_price
        
        period = EconomyPeriod(
            start_date=start_date,
            end_date=end_date,
            total_fuel_saved_kg=total_fuel_saved_kg,
            total_economy_brl=total_economy_brl,
            average_daily_economy_brl=total_economy_brl / max(1, (end_date - start_date).days),
            number_of_days=(end_date - start_date).days
        )
        
        return VesselEconomy(
            vessel_id=vessel_id,
            period=period,
            fuel_impact_records=fuel_impact_records
        )
    
    def _get_closest_fouling_prediction(
        self,
        timestamp: datetime,
        fouling_data: Dict[datetime, Dict]
    ) -> Optional[Dict]:
        """
        Obtém predição de bioincrustação mais próxima do timestamp.
        """
        if not fouling_data:
            return None
        
        closest_timestamp = min(
            fouling_data.keys(),
            key=lambda t: abs((t - timestamp).total_seconds())
        )
        
        # Se muito distante (>7 dias), retornar None
        if abs((closest_timestamp - timestamp).days) > 7:
            return None
        
        return fouling_data[closest_timestamp]
    
    def calculate_monthly_economy(
        self,
        vessel_ids: List[str],
        year: int,
        month: int,
        fuel_consumption_data: List[Dict],
        fouling_predictions: List[Dict]
    ) -> EconomyPeriod:
        """
        Calcula economia mensal.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        fleet_economy = self.calculate_accumulated_economy(
            vessel_ids,
            start_date,
            end_date,
            fuel_consumption_data,
            fouling_predictions
        )
        
        return fleet_economy.period
    
    def calculate_trends(
        self,
        vessel_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        fuel_consumption_data: List[Dict],
        fouling_predictions: List[Dict],
        interval_days: int = 30
    ) -> List[EconomyPeriod]:
        """
        Calcula tendências de economia ao longo do tempo.
        """
        trends = []
        current_date = start_date
        
        while current_date < end_date:
            period_end = min(current_date + timedelta(days=interval_days), end_date)
            
            fleet_economy = self.calculate_accumulated_economy(
                vessel_ids,
                current_date,
                period_end,
                fuel_consumption_data,
                fouling_predictions
            )
            
            trends.append(fleet_economy.period)
            current_date = period_end
        
        return trends


# Função de conveniência
def calculate_accumulated_economy(
    vessel_ids: List[str],
    start_date: datetime,
    end_date: datetime,
    fuel_consumption_data: List[Dict],
    fouling_predictions: List[Dict],
    fuel_price_brl_per_kg: Optional[float] = None
) -> FleetEconomy:
    """
    Calcula economia acumulada.
    """
    service = EconomyService(fuel_price_brl_per_kg)
    return service.calculate_accumulated_economy(
        vessel_ids,
        start_date,
        end_date,
        fuel_consumption_data,
        fouling_predictions
    )


if __name__ == "__main__":
    # Exemplo de uso
    from datetime import datetime, timedelta
    
    vessel_ids = ["VESSEL001", "VESSEL002", "VESSEL003"]
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()
    
    # Dados mock (em produção, viriam de banco de dados)
    fuel_data = [
        {
            "vessel_id": "VESSEL001",
            "timestamp": datetime.now() - timedelta(days=30),
            "consumption_kg_h": 500.0,
            "speed_knots": 12.0,
            "engine_power_kw": 5000.0,
            "hours_operating": 24.0
        }
    ]
    
    fouling_data = [
        {
            "vessel_id": "VESSEL001",
            "timestamp": datetime.now() - timedelta(days=30),
            "fouling_mm": 4.5,
            "roughness_um": 450.0
        }
    ]
    
    economy = calculate_accumulated_economy(
        vessel_ids,
        start_date,
        end_date,
        fuel_data,
        fouling_data
    )
    
    print("Economia Acumulada:")
    print(f"Período: {economy.period.start_date.date()} a {economy.period.end_date.date()}")
    print(f"Total de Embarcações: {economy.total_vessels}")
    print(f"Combustível Economizado: {economy.total_fuel_saved_kg:,.2f} kg")
    print(f"Economia Total: R$ {economy.total_economy_brl:,.2f}")
    print(f"Economia Média Diária: R$ {economy.period.average_daily_economy_brl:,.2f}")

