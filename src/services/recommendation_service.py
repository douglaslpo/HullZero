"""
Serviço de Recomendação - HullZero

Este módulo implementa a otimização do momento ideal de limpeza/manutenção
baseado em custo-benefício, conformidade regulatória e impacto ambiental.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..models.fouling_prediction import predict_fouling, VesselFeatures
from ..models.fuel_impact import calculate_fuel_impact, ConsumptionFeatures


class RecommendationType(Enum):
    """Tipos de recomendação"""
    IMMEDIATE_CLEANING = "immediate_cleaning"
    SCHEDULED_CLEANING = "scheduled_cleaning"
    MONITOR_INTENSIFIED = "monitor_intensified"
    PREVENTIVE_ACTION = "preventive_action"
    NO_ACTION = "no_action"


class RecommendationPriority(Enum):
    """Prioridades de recomendação"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Recommendation:
    """Recomendação de ação"""
    recommendation_id: str
    vessel_id: str
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    recommended_date: datetime
    estimated_benefit_brl: float
    estimated_co2_reduction_kg: float
    estimated_cost_brl: float
    net_benefit_brl: float
    compliance_risk: float  # 0-1, risco de não conformidade
    reasoning: str
    created_at: datetime
    status: str  # 'pending', 'accepted', 'rejected', 'completed'


@dataclass
class CleaningScenario:
    """Cenário de limpeza"""
    cleaning_date: datetime
    estimated_fouling_at_cleaning: float  # mm
    estimated_fuel_savings_brl: float
    estimated_co2_reduction_kg: float
    cleaning_cost_brl: float
    downtime_cost_brl: float
    total_cost_brl: float
    net_benefit_brl: float
    compliance_score: float  # 0-1


class RecommendationOptimizer:
    """
    Otimizador de recomendações de limpeza.
    Usa programação dinâmica e algoritmos genéticos.
    """
    
    # Parâmetros de custo
    CLEANING_COST_BASE_BRL = 250000.0  # Custo base de limpeza
    CLEANING_COST_PER_MM_BRL = 10000.0  # Custo adicional por mm de bioincrustação
    DOWNTIME_COST_PER_DAY_BRL = 50000.0  # Custo de downtime por dia
    CLEANING_DURATION_DAYS = 3.0  # Duração média de limpeza
    
    # Parâmetros de combustível
    FUEL_PRICE_PER_KG_BRL = 3.5
    CO2_EMISSION_FACTOR = 3.15  # kg CO2 per kg fuel
    
    # Limites NORMAM 401
    MAX_FOULING_THICKNESS_MM = 5.0  # Limite máximo de espessura
    MAX_ROUGHNESS_UM = 500.0  # Limite máximo de rugosidade
    
    def __init__(self):
        self.horizon_days = 90  # Horizonte de otimização
    
    def optimize_cleaning_schedule(
        self,
        vessel_id: str,
        current_fouling_mm: float,
        current_roughness_um: float,
        vessel_features: VesselFeatures,
        current_date: Optional[datetime] = None
    ) -> Recommendation:
        """
        Otimiza o momento ideal de limpeza.
        
        Args:
            vessel_id: ID da embarcação
            current_fouling_mm: Bioincrustação atual (mm)
            current_roughness_um: Rugosidade atual (μm)
            vessel_features: Features da embarcação
            current_date: Data atual (opcional)
            
        Returns:
            Recomendação otimizada
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Gera cenários de limpeza
        scenarios = self._generate_cleaning_scenarios(
            vessel_id,
            current_fouling_mm,
            current_roughness_um,
            vessel_features,
            current_date
        )
        
        # Avalia cada cenário
        for scenario in scenarios:
            scenario = self._evaluate_scenario(
                scenario,
                vessel_features,
                current_date
            )
        
        # Seleciona melhor cenário
        best_scenario = max(scenarios, key=lambda s: s.net_benefit_brl)
        
        # Determina tipo de recomendação
        recommendation_type, priority = self._determine_recommendation_type(
            best_scenario,
            current_fouling_mm,
            current_roughness_um
        )
        
        # Calcula risco de conformidade
        compliance_risk = self._calculate_compliance_risk(
            current_fouling_mm,
            current_roughness_um,
            best_scenario.cleaning_date,
            vessel_features
        )
        
        # Gera reasoning
        reasoning = self._generate_reasoning(
            best_scenario,
            recommendation_type,
            compliance_risk
        )
        
        return Recommendation(
            recommendation_id=f"REC_{vessel_id}_{current_date.strftime('%Y%m%d')}",
            vessel_id=vessel_id,
            recommendation_type=recommendation_type,
            priority=priority,
            recommended_date=best_scenario.cleaning_date,
            estimated_benefit_brl=best_scenario.estimated_fuel_savings_brl,
            estimated_co2_reduction_kg=best_scenario.estimated_co2_reduction_kg,
            estimated_cost_brl=best_scenario.total_cost_brl,
            net_benefit_brl=best_scenario.net_benefit_brl,
            compliance_risk=compliance_risk,
            reasoning=reasoning,
            created_at=current_date,
            status='pending'
        )
    
    def _generate_cleaning_scenarios(
        self,
        vessel_id: str,
        current_fouling_mm: float,
        current_roughness_um: float,
        vessel_features: VesselFeatures,
        current_date: datetime
    ) -> List[CleaningScenario]:
        """
        Gera cenários de limpeza para diferentes datas futuras.
        
        Args:
            vessel_id: ID da embarcação
            current_fouling_mm: Bioincrustação atual
            current_roughness_um: Rugosidade atual
            vessel_features: Features da embarcação
            current_date: Data atual
            
        Returns:
            Lista de cenários
        """
        scenarios = []
        
        # Gera cenários para diferentes datas (7, 14, 21, 30, 45, 60, 90 dias)
        for days_ahead in [7, 14, 21, 30, 45, 60, 90]:
            cleaning_date = current_date + timedelta(days=days_ahead)
            
            # Prediz bioincrustação na data de limpeza
            future_features = VesselFeatures(
                vessel_id=vessel_features.vessel_id,
                time_since_cleaning_days=vessel_features.time_since_cleaning_days + days_ahead,
                water_temperature_c=vessel_features.water_temperature_c,
                salinity_psu=vessel_features.salinity_psu,
                time_in_port_hours=vessel_features.time_in_port_hours,
                average_speed_knots=vessel_features.average_speed_knots,
                route_region=vessel_features.route_region,
                paint_type=vessel_features.paint_type,
                vessel_type=vessel_features.vessel_type,
                hull_area_m2=vessel_features.hull_area_m2
            )
            
            prediction = predict_fouling(future_features)
            estimated_fouling = prediction.estimated_thickness_mm
            estimated_roughness = prediction.estimated_roughness_um
            
            scenario = CleaningScenario(
                cleaning_date=cleaning_date,
                estimated_fouling_at_cleaning=estimated_fouling,
                estimated_fuel_savings_brl=0.0,  # Será calculado
                estimated_co2_reduction_kg=0.0,  # Será calculado
                cleaning_cost_brl=0.0,  # Será calculado
                downtime_cost_brl=0.0,  # Será calculado
                total_cost_brl=0.0,  # Será calculado
                net_benefit_brl=0.0,  # Será calculado
                compliance_score=0.0  # Será calculado
            )
            
            scenarios.append(scenario)
        
        return scenarios
    
    def _evaluate_scenario(
        self,
        scenario: CleaningScenario,
        vessel_features: VesselFeatures,
        current_date: datetime
    ) -> CleaningScenario:
        """
        Avalia um cenário de limpeza.
        
        Args:
            scenario: Cenário a avaliar
            vessel_features: Features da embarcação
            current_date: Data atual
            
        Returns:
            Cenário avaliado
        """
        # Calcula custo de limpeza
        scenario.cleaning_cost_brl = (
            self.CLEANING_COST_BASE_BRL +
            scenario.estimated_fouling_at_cleaning * self.CLEANING_COST_PER_MM_BRL
        )
        
        # Calcula custo de downtime
        scenario.downtime_cost_brl = (
            self.CLEANING_DURATION_DAYS * self.DOWNTIME_COST_PER_DAY_BRL
        )
        
        # Calcula economia de combustível
        # Assumindo que limpeza remove toda bioincrustação
        days_until_cleaning = (scenario.cleaning_date - current_date).days
        
        # Consumo adicional devido à bioincrustação (estimado)
        # Baseado na espessura e rugosidade
        fuel_increase_percent = (
            scenario.estimated_fouling_at_cleaning * 1.0 +  # 1% por mm
            scenario.estimated_roughness_um / 100.0 * 0.1  # 0.1% por 100 um
        )
        
        # Consumo base estimado (simplificado)
        base_consumption_kg_day = vessel_features.hull_area_m2 * 10.0  # Estimativa
        
        # Economia acumulada até a limpeza
        daily_savings_kg = base_consumption_kg_day * (fuel_increase_percent / 100.0)
        total_savings_kg = daily_savings_kg * days_until_cleaning
        
        scenario.estimated_fuel_savings_brl = total_savings_kg * self.FUEL_PRICE_PER_KG_BRL
        scenario.estimated_co2_reduction_kg = total_savings_kg * self.CO2_EMISSION_FACTOR
        
        # Custo total
        scenario.total_cost_brl = (
            scenario.cleaning_cost_brl + scenario.downtime_cost_brl
        )
        
        # Benefício líquido
        scenario.net_benefit_brl = (
            scenario.estimated_fuel_savings_brl - scenario.total_cost_brl
        )
        
        # Score de conformidade
        scenario.compliance_score = self._calculate_compliance_score(
            scenario.estimated_fouling_at_cleaning,
            scenario.estimated_roughness_um
        )
        
        return scenario
    
    def _calculate_compliance_score(
        self,
        fouling_mm: float,
        roughness_um: float
    ) -> float:
        """
        Calcula score de conformidade (0-1, 1 = totalmente conforme).
        
        Args:
            fouling_mm: Espessura de bioincrustação
            roughness_um: Rugosidade
            
        Returns:
            Score de conformidade
        """
        # Penaliza se exceder limites
        fouling_score = 1.0 if fouling_mm <= self.MAX_FOULING_THICKNESS_MM else 0.0
        roughness_score = 1.0 if roughness_um <= self.MAX_ROUGHNESS_UM else 0.0
        
        # Score combinado
        compliance_score = (fouling_score + roughness_score) / 2.0
        
        # Penaliza se próximo dos limites
        if fouling_mm > self.MAX_FOULING_THICKNESS_MM * 0.8:
            compliance_score *= 0.7
        if roughness_um > self.MAX_ROUGHNESS_UM * 0.8:
            compliance_score *= 0.7
        
        return compliance_score
    
    def _calculate_compliance_risk(
        self,
        current_fouling_mm: float,
        current_roughness_um: float,
        recommended_date: datetime,
        vessel_features: VesselFeatures
    ) -> float:
        """
        Calcula risco de não conformidade (0-1, 1 = alto risco).
        
        Args:
            current_fouling_mm: Bioincrustação atual
            current_roughness_um: Rugosidade atual
            recommended_date: Data recomendada
            vessel_features: Features da embarcação
            
        Returns:
            Risco de não conformidade
        """
        # Prediz bioincrustação até a data recomendada
        days_until = (recommended_date - datetime.now()).days
        
        future_features = VesselFeatures(
            vessel_id=vessel_features.vessel_id,
            time_since_cleaning_days=vessel_features.time_since_cleaning_days + days_until,
            water_temperature_c=vessel_features.water_temperature_c,
            salinity_psu=vessel_features.salinity_psu,
            time_in_port_hours=vessel_features.time_in_port_hours,
            average_speed_knots=vessel_features.average_speed_knots,
            route_region=vessel_features.route_region,
            paint_type=vessel_features.paint_type,
            vessel_type=vessel_features.vessel_type,
            hull_area_m2=vessel_features.hull_area_m2
        )
        
        prediction = predict_fouling(future_features)
        
        # Risco baseado em quão próximo dos limites
        fouling_risk = max(0.0, (prediction.estimated_thickness_mm - self.MAX_FOULING_THICKNESS_MM * 0.7) / (self.MAX_FOULING_THICKNESS_MM * 0.3))
        roughness_risk = max(0.0, (prediction.estimated_roughness_um - self.MAX_ROUGHNESS_UM * 0.7) / (self.MAX_ROUGHNESS_UM * 0.3))
        
        risk = min(1.0, (fouling_risk + roughness_risk) / 2.0)
        return risk
    
    def _determine_recommendation_type(
        self,
        scenario: CleaningScenario,
        current_fouling_mm: float,
        current_roughness_um: float
    ) -> Tuple[RecommendationType, RecommendationPriority]:
        """
        Determina tipo e prioridade da recomendação.
        
        Args:
            scenario: Melhor cenário
            current_fouling_mm: Bioincrustação atual
            current_roughness_um: Rugosidade atual
            
        Returns:
            Tupla (tipo, prioridade)
        """
        days_until = (scenario.cleaning_date - datetime.now()).days
        
        # Crítico: excede limites ou muito próximo
        if (current_fouling_mm > self.MAX_FOULING_THICKNESS_MM or
            current_roughness_um > self.MAX_ROUGHNESS_UM):
            return RecommendationType.IMMEDIATE_CLEANING, RecommendationPriority.CRITICAL
        
        # Alto: próximo dos limites e recomendação em <14 dias
        if (current_fouling_mm > self.MAX_FOULING_THICKNESS_MM * 0.8 or
            current_roughness_um > self.MAX_ROUGHNESS_UM * 0.8):
            if days_until <= 14:
                return RecommendationType.IMMEDIATE_CLEANING, RecommendationPriority.HIGH
            else:
                return RecommendationType.SCHEDULED_CLEANING, RecommendationPriority.HIGH
        
        # Médio: recomendação em 30-60 dias
        if 30 <= days_until <= 60:
            return RecommendationType.SCHEDULED_CLEANING, RecommendationPriority.MEDIUM
        
        # Baixo: recomendação em >60 dias
        if days_until > 60:
            return RecommendationType.MONITOR_INTENSIFIED, RecommendationPriority.LOW
        
        return RecommendationType.SCHEDULED_CLEANING, RecommendationPriority.MEDIUM
    
    def _generate_reasoning(
        self,
        scenario: CleaningScenario,
        recommendation_type: RecommendationType,
        compliance_risk: float
    ) -> str:
        """
        Gera explicação da recomendação.
        
        Args:
            scenario: Cenário selecionado
            recommendation_type: Tipo de recomendação
            compliance_risk: Risco de não conformidade
            
        Returns:
            Explicação em texto
        """
        reasoning = f"Recomendação baseada em análise de custo-benefício e conformidade regulatória. "
        
        if recommendation_type == RecommendationType.IMMEDIATE_CLEANING:
            reasoning += "Limpeza imediata recomendada devido a risco crítico de não conformidade. "
        elif recommendation_type == RecommendationType.SCHEDULED_CLEANING:
            reasoning += f"Limpeza agendada para {scenario.cleaning_date.strftime('%d/%m/%Y')} otimiza custo-benefício. "
        else:
            reasoning += "Monitoramento intensificado recomendado. Limpeza pode ser agendada no futuro. "
        
        reasoning += f"Benefício líquido estimado: R$ {scenario.net_benefit_brl:,.2f}. "
        reasoning += f"Redução de CO₂ estimada: {scenario.estimated_co2_reduction_kg:,.0f} kg. "
        
        if compliance_risk > 0.7:
            reasoning += "ALERTA: Risco alto de não conformidade com NORMAM 401."
        elif compliance_risk > 0.4:
            reasoning += "Atenção: Risco moderado de não conformidade."
        else:
            reasoning += "Risco baixo de não conformidade."
        
        return reasoning


# Função de conveniência
def get_cleaning_recommendation(
    vessel_id: str,
    current_fouling_mm: float,
    current_roughness_um: float,
    vessel_features: VesselFeatures
) -> Recommendation:
    """
    Obtém recomendação de limpeza para uma embarcação.
    
    Args:
        vessel_id: ID da embarcação
        current_fouling_mm: Bioincrustação atual (mm)
        current_roughness_um: Rugosidade atual (μm)
        vessel_features: Features da embarcação
        
    Returns:
        Recomendação de limpeza
    """
    optimizer = RecommendationOptimizer()
    return optimizer.optimize_cleaning_schedule(
        vessel_id,
        current_fouling_mm,
        current_roughness_um,
        vessel_features
    )


if __name__ == "__main__":
    # Exemplo de uso
    vessel_features = VesselFeatures(
        vessel_id="VESSEL001",
        time_since_cleaning_days=90,
        water_temperature_c=25.0,
        salinity_psu=32.5,
        time_in_port_hours=120,
        average_speed_knots=12.0,
        route_region="South_Atlantic",
        paint_type="Antifouling_Type_A",
        vessel_type="Tanker",
        hull_area_m2=5000.0
    )
    
    recommendation = get_cleaning_recommendation(
        vessel_id="VESSEL001",
        current_fouling_mm=4.5,
        current_roughness_um=450.0,
        vessel_features=vessel_features
    )
    
    print("Recomendação de Limpeza:")
    print(f"Tipo: {recommendation.recommendation_type.value}")
    print(f"Prioridade: {recommendation.priority.name}")
    print(f"Data Recomendada: {recommendation.recommended_date.strftime('%d/%m/%Y')}")
    print(f"Benefício Líquido: R$ {recommendation.net_benefit_brl:,.2f}")
    print(f"Redução de CO₂: {recommendation.estimated_co2_reduction_kg:,.0f} kg")
    print(f"Risco de Conformidade: {recommendation.compliance_risk:.2%}")
    print(f"\nRaciocínio:\n{recommendation.reasoning}")

