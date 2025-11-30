"""
Modelo de Predição de Risco NORMAM 401 - HullZero

Este módulo implementa modelos de IA para predizer risco de não conformidade
com a NORMAM 401 e identificar fatores de risco.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .fouling_prediction import predict_fouling, VesselFeatures
from .fuel_impact import ConsumptionFeatures


class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskFactor:
    """Fator de risco identificado"""
    factor_name: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    contribution: float  # 0-1, contribuição para o risco
    recommendation: str


@dataclass
class NORMAM401RiskPrediction:
    """Predição de risco NORMAM 401"""
    vessel_id: str
    prediction_date: datetime
    days_ahead: int
    risk_score: float  # 0-1
    risk_level: RiskLevel
    predicted_fouling_mm: float
    predicted_roughness_um: float
    predicted_compliance_status: str
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    confidence: float


class NORMAM401RiskPredictor:
    """
    Modelo que prediz risco de não conformidade com NORMAM 401.
    """
    
    # Limites NORMAM 401
    MAX_FOULING_THICKNESS_MM = 5.0
    MAX_ROUGHNESS_UM = 500.0
    
    # Thresholds de risco
    RISK_THRESHOLDS = {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8
    }
    
    def __init__(self):
        pass
    
    def predict_risk(
        self,
        vessel_id: str,
        vessel_features: VesselFeatures,
        days_ahead: int = 30,
        current_fouling_mm: Optional[float] = None,
        current_roughness_um: Optional[float] = None
    ) -> NORMAM401RiskPrediction:
        """
        Prediz risco de não conformidade em X dias.
        
        Args:
            vessel_id: ID da embarcação
            vessel_features: Features da embarcação
            days_ahead: Quantos dias à frente predizer (30, 60, 90)
            current_fouling_mm: Bioincrustação atual (opcional)
            current_roughness_um: Rugosidade atual (opcional)
            
        Returns:
            Predição de risco
        """
        # Se não fornecido, predizer estado atual
        if current_fouling_mm is None or current_roughness_um is None:
            current_prediction = predict_fouling(vessel_features)
            current_fouling_mm = current_prediction.estimated_thickness_mm
            current_roughness_um = current_prediction.estimated_roughness_um
        
        # Predizer estado futuro
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
        
        future_prediction = predict_fouling(future_features)
        future_fouling = future_prediction.estimated_thickness_mm
        future_roughness = future_prediction.estimated_roughness_um
        
        # Verificar conformidade futura
        compliance = self._check_compliance(
            future_fouling,
            future_roughness,
            vessel_features.vessel_type
        )
        
        # Calcular score de risco (0-1, 1 = risco máximo)
        risk_score = self._calculate_risk_score(
            future_fouling,
            future_roughness,
            compliance
        )
        
        # Determinar nível de risco
        risk_level = self._determine_risk_level(risk_score)
        
        # Identificar fatores de risco
        risk_factors = self._identify_risk_factors(
            vessel_features,
            current_fouling_mm,
            future_fouling,
            days_ahead
        )
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(
            risk_level,
            risk_score,
            future_fouling,
            future_roughness,
            days_ahead,
            risk_factors
        )
        
        # Calcular confiança (baseada na consistência das predições)
        confidence = self._calculate_confidence(
            current_prediction if current_fouling_mm is None else None,
            future_prediction
        )
        
        return NORMAM401RiskPrediction(
            vessel_id=vessel_id,
            prediction_date=datetime.now(),
            days_ahead=days_ahead,
            risk_score=risk_score,
            risk_level=risk_level,
            predicted_fouling_mm=future_fouling,
            predicted_roughness_um=future_roughness,
            predicted_compliance_status=compliance['status'],
            risk_factors=risk_factors,
            recommendations=recommendations,
            confidence=confidence
        )
    
    def _check_compliance(
        self,
        fouling_mm: float,
        roughness_um: float,
        vessel_type: str
    ) -> Dict:
        """
        Verifica conformidade com NORMAM 401.
        
        Returns:
            Dict com status, score, violations, warnings
        """
        # Limites por tipo
        limits = {
            'tanker': {'thickness': 5.0, 'roughness': 500.0},
            'cargo': {'thickness': 5.0, 'roughness': 500.0},
            'container': {'thickness': 4.5, 'roughness': 450.0},
            'tug': {'thickness': 6.0, 'roughness': 600.0},
            'standard': {'thickness': 5.0, 'roughness': 500.0}
        }
        
        limit = limits.get(vessel_type.lower(), limits['standard'])
        
        violations = []
        warnings = []
        
        # Verificação
        if fouling_mm > limit['thickness']:
            violations.append(f"Espessura excede limite")
            status = 'non_compliant'
        elif fouling_mm > limit['thickness'] * 0.8:
            warnings.append(f"Espessura próxima do limite")
            status = 'at_risk'
        else:
            status = 'compliant'
        
        if roughness_um > limit['roughness']:
            violations.append(f"Rugosidade excede limite")
            if status == 'compliant':
                status = 'non_compliant'
        elif roughness_um > limit['roughness'] * 0.8:
            warnings.append(f"Rugosidade próxima do limite")
            if status == 'compliant':
                status = 'at_risk'
        
        # Score de conformidade
        thickness_score = 1.0 - min(1.0, fouling_mm / limit['thickness'])
        roughness_score = 1.0 - min(1.0, roughness_um / limit['roughness'])
        compliance_score = (thickness_score * 0.6 + roughness_score * 0.4)
        
        return {
            'status': status,
            'score': max(0.0, min(1.0, compliance_score)),
            'violations': violations,
            'warnings': warnings
        }
    
    def _calculate_risk_score(
        self,
        fouling_mm: float,
        roughness_um: float,
        compliance: Dict
    ) -> float:
        """
        Calcula score de risco (0-1, 1 = risco máximo).
        """
        # Risco baseado no score de conformidade (invertido)
        base_risk = 1.0 - compliance['score']
        
        # Ajustes adicionais
        # Se muito próximo do limite, aumenta risco
        if fouling_mm > self.MAX_FOULING_THICKNESS_MM * 0.9:
            base_risk = min(1.0, base_risk + 0.2)
        
        if roughness_um > self.MAX_ROUGHNESS_UM * 0.9:
            base_risk = min(1.0, base_risk + 0.15)
        
        return base_risk
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determina nível de risco baseado no score.
        """
        if risk_score >= self.RISK_THRESHOLDS['high']:
            return RiskLevel.CRITICAL
        elif risk_score >= self.RISK_THRESHOLDS['medium']:
            return RiskLevel.HIGH
        elif risk_score >= self.RISK_THRESHOLDS['low']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_risk_factors(
        self,
        vessel_features: VesselFeatures,
        current_fouling: float,
        future_fouling: float,
        days_ahead: int
    ) -> List[RiskFactor]:
        """
        Identifica fatores que contribuem para o risco.
        """
        factors = []
        
        # Fator 1: Tempo desde última limpeza
        if vessel_features.time_since_cleaning_days > 120:
            contribution = min(0.4, (vessel_features.time_since_cleaning_days - 90) / 100.0)
            factors.append(RiskFactor(
                factor_name="Tempo desde última limpeza",
                severity="high",
                description=f"{vessel_features.time_since_cleaning_days} dias desde última limpeza (recomendado: <90 dias)",
                contribution=contribution,
                recommendation="Considerar limpeza preventiva"
            ))
        
        # Fator 2: Taxa de crescimento
        growth_rate = (future_fouling - current_fouling) / days_ahead  # mm/dia
        if growth_rate > 0.1:
            contribution = min(0.3, growth_rate * 2.0)
            factors.append(RiskFactor(
                factor_name="Taxa de crescimento acelerada",
                severity="medium",
                description=f"Crescimento de {growth_rate:.2f} mm/dia (normal: <0.05 mm/dia)",
                contribution=contribution,
                recommendation="Investigar causas do crescimento acelerado"
            ))
        
        # Fator 3: Rota de alto risco
        high_risk_routes = ['tropical', 'high_productivity', 'warm_water']
        if vessel_features.route_region.lower() in high_risk_routes:
            factors.append(RiskFactor(
                factor_name="Rota de alto risco",
                severity="medium",
                description=f"Rota {vessel_features.route_region} tem maior crescimento de bioincrustação",
                contribution=0.2,
                recommendation="Monitoramento intensificado recomendado"
            ))
        
        # Fator 4: Temperatura alta
        if vessel_features.water_temperature_c > 28:
            contribution = (vessel_features.water_temperature_c - 25) / 10.0 * 0.15
            factors.append(RiskFactor(
                factor_name="Temperatura da água alta",
                severity="medium",
                description=f"Temperatura {vessel_features.water_temperature_c}°C acelera crescimento (ótimo: 20-25°C)",
                contribution=min(0.2, contribution),
                recommendation="Monitorar mais de perto em águas quentes"
            ))
        
        # Fator 5: Tempo em porto excessivo
        if vessel_features.time_in_port_hours > 168:  # >7 dias
            contribution = (vessel_features.time_in_port_hours - 120) / 200.0 * 0.15
            factors.append(RiskFactor(
                factor_name="Tempo excessivo em porto",
                severity="low",
                description=f"{vessel_features.time_in_port_hours/24:.1f} dias em porto aumenta exposição a larvas",
                contribution=min(0.15, contribution),
                recommendation="Minimizar tempo em porto quando possível"
            ))
        
        # Fator 6: Velocidade baixa
        if vessel_features.average_speed_knots < 8:
            factors.append(RiskFactor(
                factor_name="Velocidade de navegação baixa",
                severity="low",
                description=f"Velocidade média {vessel_features.average_speed_knots} nós permite maior colonização",
                contribution=0.1,
                recommendation="Velocidades >10 nós reduzem colonização"
            ))
        
        return factors
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_score: float,
        future_fouling: float,
        future_roughness: float,
        days_ahead: int,
        risk_factors: List[RiskFactor]
    ) -> List[str]:
        """
        Gera recomendações baseadas no risco.
        """
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append(
                f"⚠️ RISCO CRÍTICO: Limpeza imediata recomendada. "
                f"Em {days_ahead} dias, bioincrustação prevista: {future_fouling:.1f} mm "
                f"(limite: 5.0 mm). Ação imediata necessária para evitar não conformidade."
            )
            recommendations.append(
                "Notificar autoridades competentes sobre risco de não conformidade."
            )
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append(
                f"🔶 RISCO ALTO: Planejar limpeza dentro de {max(7, days_ahead - 14)} dias. "
                f"Bioincrustação prevista: {future_fouling:.1f} mm."
            )
            recommendations.append(
                "Aumentar frequência de monitoramento para diária."
            )
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append(
                f"🟡 RISCO MODERADO: Monitoramento intensificado recomendado. "
                f"Bioincrustação prevista em {days_ahead} dias: {future_fouling:.1f} mm."
            )
            recommendations.append(
                "Considerar limpeza preventiva nos próximos 30-60 dias."
            )
        
        else:  # LOW
            recommendations.append(
                f"🟢 RISCO BAIXO: Situação estável. Manter monitoramento regular."
            )
        
        # Recomendações baseadas em fatores
        high_severity_factors = [f for f in risk_factors if f.severity == 'high']
        if high_severity_factors:
            recommendations.append(
                f"Atenção: {len(high_severity_factors)} fator(es) de alta severidade identificado(s)."
            )
        
        return recommendations
    
    def _calculate_confidence(
        self,
        current_prediction: Optional,
        future_prediction
    ) -> float:
        """
        Calcula confiança na predição (0-1).
        """
        # Baseado na confiança das predições
        if current_prediction:
            confidence = (current_prediction.confidence_score + future_prediction.confidence_score) / 2.0
        else:
            confidence = future_prediction.confidence_score
        
        # Ajuste baseado em quão longe estamos predizendo
        # Predições mais próximas são mais confiáveis
        if hasattr(future_prediction, 'confidence_score'):
            confidence = confidence * 0.9  # Pequena penalização por ser predição futura
        
        return max(0.5, min(1.0, confidence))
    
    def predict_risk_timeline(
        self,
        vessel_id: str,
        vessel_features: VesselFeatures,
        horizon_days: int = 90,
        intervals: List[int] = [7, 14, 30, 60, 90]
    ) -> List[NORMAM401RiskPrediction]:
        """
        Prediz risco ao longo de um horizonte temporal.
        
        Args:
            vessel_id: ID da embarcação
            vessel_features: Features da embarcação
            horizon_days: Horizonte total em dias
            intervals: Intervalos específicos para predizer
            
        Returns:
            Lista de predições de risco para cada intervalo
        """
        predictions = []
        
        for days_ahead in intervals:
            if days_ahead <= horizon_days:
                prediction = self.predict_risk(
                    vessel_id,
                    vessel_features,
                    days_ahead
                )
                predictions.append(prediction)
        
        return predictions


# Função de conveniência
def predict_normam401_risk(
    vessel_id: str,
    vessel_features: VesselFeatures,
    days_ahead: int = 30
) -> NORMAM401RiskPrediction:
    """
    Prediz risco de não conformidade NORMAM 401.
    
    Args:
        vessel_id: ID da embarcação
        vessel_features: Features da embarcação
        days_ahead: Quantos dias à frente predizer
        
    Returns:
        Predição de risco
    """
    predictor = NORMAM401RiskPredictor()
    return predictor.predict_risk(vessel_id, vessel_features, days_ahead)


if __name__ == "__main__":
    # Exemplo de uso
    features = VesselFeatures(
        vessel_id="VESSEL001",
        time_since_cleaning_days=120,
        water_temperature_c=28.0,
        salinity_psu=32.5,
        time_in_port_hours=200,
        average_speed_knots=10.0,
        route_region="tropical",
        paint_type="Antifouling_Type_A",
        vessel_type="Tanker",
        hull_area_m2=5000.0
    )
    
    risk = predict_normam401_risk("VESSEL001", features, days_ahead=30)
    
    print("Predição de Risco NORMAM 401:")
    print(f"Score de Risco: {risk.risk_score:.2%}")
    print(f"Nível de Risco: {risk.risk_level.value}")
    print(f"Bioincrustação Prevista: {risk.predicted_fouling_mm:.2f} mm")
    print(f"Status de Conformidade: {risk.predicted_compliance_status}")
    print(f"\nFatores de Risco: {len(risk.risk_factors)}")
    for factor in risk.risk_factors:
        print(f"  - {factor.factor_name}: {factor.description}")
    print(f"\nRecomendações:")
    for rec in risk.recommendations:
        print(f"  - {rec}")

