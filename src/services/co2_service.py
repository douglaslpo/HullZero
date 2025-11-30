"""
Serviço de Cálculo de Redução de CO₂ - HullZero

Este módulo calcula redução de emissões de CO₂ baseada na economia
de combustível atribuível à gestão de bioincrustação.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .economy_service import EconomyService, FleetEconomy, EconomyPeriod


@dataclass
class CO2Reduction:
    """Redução de CO₂"""
    co2_reduced_kg: float
    co2_reduced_tonnes: float
    fuel_saved_kg: float
    equivalent_cars: float  # Carros equivalentes
    equivalent_trees: float  # Árvores equivalentes
    equivalent_homes: float  # Casas equivalentes (energia anual)


@dataclass
class CO2ReductionPeriod:
    """Redução de CO₂ em um período"""
    start_date: datetime
    end_date: datetime
    co2_reduction: CO2Reduction
    daily_average_co2_tonnes: float
    number_of_days: int


class CO2Service:
    """
    Serviço para cálculo de redução de CO₂.
    
    A redução de CO₂ é calculada a partir da economia de combustível,
    usando fatores de emissão padrão.
    """
    
    # Fator de emissão CO₂ (kg CO₂ por kg de combustível marítimo)
    CO2_EMISSION_FACTOR = 3.15  # kg CO₂ / kg combustível
    
    # Equivalências para comparação
    CO2_PER_CAR_PER_YEAR_KG = 4600.0  # 1 carro médio = 4.6 tCO₂/ano
    CO2_PER_TREE_PER_YEAR_KG = 0.05  # 1 árvore = 0.05 tCO₂/ano (20 kg CO₂/ano)
    CO2_PER_HOME_PER_YEAR_KG = 12000.0  # 1 casa = 12 tCO₂/ano
    
    def __init__(self):
        pass
    
    def calculate_co2_reduction(
        self,
        fuel_saved_kg: float
    ) -> CO2Reduction:
        """
        Calcula redução de CO₂ a partir da economia de combustível.
        
        Args:
            fuel_saved_kg: Combustível economizado (kg)
            
        Returns:
            Redução de CO₂
        """
        # CO₂ reduzido
        co2_reduced_kg = fuel_saved_kg * self.CO2_EMISSION_FACTOR
        co2_reduced_tonnes = co2_reduced_kg / 1000.0
        
        # Comparações
        equivalent_cars = co2_reduced_tonnes / (self.CO2_PER_CAR_PER_YEAR_KG / 1000.0)
        equivalent_trees = co2_reduced_tonnes / (self.CO2_PER_TREE_PER_YEAR_KG / 1000.0)
        equivalent_homes = co2_reduced_tonnes / (self.CO2_PER_HOME_PER_YEAR_KG / 1000.0)
        
        return CO2Reduction(
            co2_reduced_kg=co2_reduced_kg,
            co2_reduced_tonnes=co2_reduced_tonnes,
            fuel_saved_kg=fuel_saved_kg,
            equivalent_cars=equivalent_cars,
            equivalent_trees=equivalent_trees,
            equivalent_homes=equivalent_homes
        )
    
    def calculate_co2_reduction_from_economy(
        self,
        fleet_economy: FleetEconomy
    ) -> CO2ReductionPeriod:
        """
        Calcula redução de CO₂ a partir da economia da frota.
        
        Args:
            fleet_economy: Economia da frota
            
        Returns:
            Redução de CO₂ no período
        """
        co2_reduction = self.calculate_co2_reduction(
            fleet_economy.total_fuel_saved_kg
        )
        
        period = fleet_economy.period
        daily_average = co2_reduction.co2_reduced_tonnes / max(1, period.number_of_days)
        
        return CO2ReductionPeriod(
            start_date=period.start_date,
            end_date=period.end_date,
            co2_reduction=co2_reduction,
            daily_average_co2_tonnes=daily_average,
            number_of_days=period.number_of_days
        )
    
    def calculate_monthly_co2_reduction(
        self,
        vessel_ids: List[str],
        year: int,
        month: int,
        fuel_consumption_data: List[Dict],
        fouling_predictions: List[Dict],
        fuel_price_brl_per_kg: Optional[float] = None
    ) -> CO2ReductionPeriod:
        """
        Calcula redução de CO₂ mensal.
        
        Args:
            vessel_ids: Lista de IDs de embarcações
            year: Ano
            month: Mês (1-12)
            fuel_consumption_data: Dados de consumo
            fouling_predictions: Predições de bioincrustação
            fuel_price_brl_per_kg: Preço do combustível (opcional)
            
        Returns:
            Redução de CO₂ no mês
        """
        from .economy_service import EconomyService
        
        economy_service = EconomyService(fuel_price_brl_per_kg)
        fleet_economy = economy_service.calculate_monthly_economy(
            vessel_ids,
            year,
            month,
            fuel_consumption_data,
            fouling_predictions
        )
        
        # Criar FleetEconomy temporário para usar calculate_co2_reduction_from_economy
        temp_fleet_economy = FleetEconomy(
            total_vessels=len(vessel_ids),
            period=fleet_economy,
            vessel_economies=[],
            total_fuel_saved_kg=fleet_economy.total_fuel_saved_kg,
            total_economy_brl=fleet_economy.total_economy_brl
        )
        
        return self.calculate_co2_reduction_from_economy(temp_fleet_economy)
    
    def calculate_trends(
        self,
        economy_trends: List[EconomyPeriod]
    ) -> List[CO2ReductionPeriod]:
        """
        Calcula tendências de redução de CO₂.
        
        Args:
            economy_trends: Tendências de economia
            
        Returns:
            Tendências de redução de CO₂
        """
        co2_trends = []
        
        for economy_period in economy_trends:
            co2_reduction = self.calculate_co2_reduction(
                economy_period.total_fuel_saved_kg
            )
            
            daily_average = co2_reduction.co2_reduced_tonnes / max(1, economy_period.number_of_days)
            
            co2_trends.append(CO2ReductionPeriod(
                start_date=economy_period.start_date,
                end_date=economy_period.end_date,
                co2_reduction=co2_reduction,
                daily_average_co2_tonnes=daily_average,
                number_of_days=economy_period.number_of_days
            ))
        
        return co2_trends
    
    def get_comparison_text(
        self,
        co2_reduction: CO2Reduction
    ) -> str:
        """
        Gera texto de comparação para exibição.
        
        Args:
            co2_reduction: Redução de CO₂
            
        Returns:
            Texto formatado
        """
        text = f"Redução de {co2_reduction.co2_reduced_tonnes:,.1f} toneladas de CO₂"
        
        if co2_reduction.equivalent_cars >= 1:
            text += f", equivalente a {co2_reduction.equivalent_cars:.0f} carros"
        
        if co2_reduction.equivalent_trees >= 1:
            text += f" ou {co2_reduction.equivalent_trees:,.0f} árvores"
        
        return text


# Função de conveniência
def calculate_co2_reduction(
    fuel_saved_kg: float
) -> CO2Reduction:
    """
    Calcula redução de CO₂.
    """
    service = CO2Service()
    return service.calculate_co2_reduction(fuel_saved_kg)


if __name__ == "__main__":
    # Exemplo de uso
    fuel_saved = 100000.0  # 100 toneladas de combustível economizado
    
    co2_reduction = calculate_co2_reduction(fuel_saved)
    
    print("Redução de CO₂:")
    print(f"CO₂ Reduzido: {co2_reduction.co2_reduced_tonnes:,.2f} toneladas")
    print(f"Combustível Economizado: {co2_reduction.fuel_saved_kg:,.2f} kg")
    print(f"\nEquivalências:")
    print(f"  Carros: {co2_reduction.equivalent_cars:.0f} carros/ano")
    print(f"  Árvores: {co2_reduction.equivalent_trees:,.0f} árvores")
    print(f"  Casas: {co2_reduction.equivalent_homes:.1f} casas/ano")
    
    service = CO2Service()
    comparison_text = service.get_comparison_text(co2_reduction)
    print(f"\n{comparison_text}")

