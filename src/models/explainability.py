"""
Modelo de Explicabilidade - HullZero

Este módulo implementa técnicas de explicabilidade para os modelos de IA,
incluindo SHAP values, feature importance e explicações em linguagem natural.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP não disponível. Instale com: pip install shap")


@dataclass
class FeatureContribution:
    """Contribuição de uma feature para a predição"""
    feature_name: str
    contribution: float  # Pode ser negativo (reduz) ou positivo (aumenta)
    percentage: float  # Porcentagem da contribuição total
    description: str


@dataclass
class PredictionExplanation:
    """Explicação completa de uma predição"""
    prediction_id: str
    prediction_value: float
    base_value: float
    feature_contributions: List[FeatureContribution]
    explanation_text: str
    confidence: float
    model_type: str


class ModelExplainer:
    """
    Classe para explicar predições dos modelos.
    """
    
    def __init__(self):
        self.shap_explainer = None
    
    def explain_fouling_prediction(
        self,
        model,
        features: Dict,
        prediction: float
    ) -> PredictionExplanation:
        """
        Explica predição de bioincrustação.
        
        Args:
            model: Modelo treinado (ou None para modelo físico)
            features: Features de entrada
            prediction: Valor da predição
            
        Returns:
            Explicação da predição
        """
        # Se modelo não disponível, usar explicação baseada em física
        if model is None:
            return self._explain_physical_model(features, prediction)
        
        # Tentar usar SHAP se disponível
        if SHAP_AVAILABLE and hasattr(model, 'predict'):
            try:
                return self._explain_with_shap(model, features, prediction)
            except:
                pass
        
        # Fallback: explicação baseada em importância de features
        return self._explain_with_feature_importance(model, features, prediction)
    
    def _explain_physical_model(
        self,
        features: Dict,
        prediction: float
    ) -> PredictionExplanation:
        """
        Explica predição baseada em modelo físico.
        """
        contributions = []
        
        # Contribuição do tempo desde limpeza
        days = features.get('time_since_cleaning_days', 0)
        time_contribution = min(0.4, days / 200.0)  # Normalizado
        contributions.append(FeatureContribution(
            feature_name="Tempo desde última limpeza",
            contribution=time_contribution,
            percentage=time_contribution * 100,
            description=f"{days} dias desde última limpeza. Quanto mais tempo, maior o crescimento."
        ))
        
        # Contribuição da temperatura
        temp = features.get('water_temperature_c', 25.0)
        temp_optimum = 25.0
        temp_contribution = abs(temp - temp_optimum) / 10.0 * 0.2
        if temp > temp_optimum:
            temp_contribution = temp_contribution  # Temperatura alta aumenta
        contributions.append(FeatureContribution(
            feature_name="Temperatura da água",
            contribution=temp_contribution,
            percentage=temp_contribution * 100,
            description=f"Temperatura {temp}°C. Temperaturas entre 20-30°C aceleram crescimento."
        ))
        
        # Contribuição do tempo em porto
        port_hours = features.get('time_in_port_hours', 0)
        port_contribution = min(0.2, port_hours / 500.0)
        contributions.append(FeatureContribution(
            feature_name="Tempo em porto",
            contribution=port_contribution,
            percentage=port_contribution * 100,
            description=f"{port_hours/24:.1f} dias em porto aumenta exposição a larvas."
        ))
        
        # Contribuição da velocidade
        speed = features.get('average_speed_knots', 12.0)
        speed_contribution = max(0, (15.0 - speed) / 15.0 * 0.15)  # Velocidades baixas aumentam
        contributions.append(FeatureContribution(
            feature_name="Velocidade de navegação",
            contribution=-speed_contribution,  # Negativo = reduz crescimento
            percentage=speed_contribution * 100,
            description=f"Velocidade {speed} nós. Velocidades altas reduzem colonização."
        ))
        
        # Normalizar contribuições
        total = sum(abs(c.contribution) for c in contributions)
        if total > 0:
            for c in contributions:
                c.percentage = (abs(c.contribution) / total) * 100
        
        # Gerar texto explicativo
        explanation_text = self._generate_explanation_text(contributions, prediction)
        
        return PredictionExplanation(
            prediction_id=f"pred_{datetime.now().timestamp()}",
            prediction_value=prediction,
            base_value=0.0,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.85,
            model_type="physical"
        )
    
    def _explain_with_shap(
        self,
        model,
        features: Dict,
        prediction: float
    ) -> PredictionExplanation:
        """
        Explica usando SHAP values.
        """
        # Converter features para array
        feature_names = list(features.keys())
        feature_values = np.array([[features[f] for f in feature_names]])
        
        # Criar explainer
        if self.shap_explainer is None:
            if hasattr(model, 'predict'):
                self.shap_explainer = shap.TreeExplainer(model)
            else:
                # Fallback para modelo linear
                self.shap_explainer = shap.LinearExplainer(model, feature_values)
        
        # Calcular SHAP values
        shap_values = self.shap_explainer.shap_values(feature_values)
        base_value = self.shap_explainer.expected_value
        
        # Converter para lista de contribuições
        contributions = []
        total_abs = np.sum(np.abs(shap_values[0]))
        
        for i, (name, value) in enumerate(zip(feature_names, shap_values[0])):
            percentage = (abs(value) / total_abs * 100) if total_abs > 0 else 0
            contributions.append(FeatureContribution(
                feature_name=name.replace('_', ' ').title(),
                contribution=float(value),
                percentage=percentage,
                description=self._get_feature_description(name, features[name])
            ))
        
        # Ordenar por contribuição absoluta
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        # Gerar texto explicativo
        explanation_text = self._generate_explanation_text(contributions, prediction)
        
        return PredictionExplanation(
            prediction_id=f"pred_{datetime.now().timestamp()}",
            prediction_value=prediction,
            base_value=float(base_value),
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.90,
            model_type="shap"
        )
    
    def _explain_with_feature_importance(
        self,
        model,
        features: Dict,
        prediction: float
    ) -> PredictionExplanation:
        """
        Explica usando importância de features (fallback).
        """
        # Tentar obter feature importance do modelo
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = list(features.keys())
            
            contributions = []
            total = np.sum(importances)
            
            for name, importance in zip(feature_names, importances):
                # Estimar contribuição baseada na importância e valor da feature
                feature_value = features[name]
                normalized_value = (feature_value - np.mean([features[n] for n in feature_names])) / (np.std([features[n] for n in feature_names]) + 1e-6)
                contribution = importance * normalized_value
                
                contributions.append(FeatureContribution(
                    feature_name=name.replace('_', ' ').title(),
                    contribution=float(contribution),
                    percentage=(importance / total * 100) if total > 0 else 0,
                    description=self._get_feature_description(name, feature_value)
                ))
        else:
            # Fallback para explicação física
            return self._explain_physical_model(features, prediction)
        
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        explanation_text = self._generate_explanation_text(contributions, prediction)
        
        return PredictionExplanation(
            prediction_id=f"pred_{datetime.now().timestamp()}",
            prediction_value=prediction,
            base_value=0.0,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.75,
            model_type="feature_importance"
        )
    
    def _get_feature_description(self, feature_name: str, value: float) -> str:
        """
        Gera descrição de uma feature.
        """
        descriptions = {
            'time_since_cleaning_days': f"{value:.0f} dias desde última limpeza",
            'water_temperature_c': f"Temperatura da água: {value:.1f}°C",
            'salinity_psu': f"Salinidade: {value:.1f} PSU",
            'time_in_port_hours': f"{value/24:.1f} dias em porto",
            'average_speed_knots': f"Velocidade média: {value:.1f} nós",
            'route_region': f"Rota: {value}",
            'paint_type': f"Tinta: {value}",
            'vessel_type': f"Tipo: {value}",
            'hull_area_m2': f"Área do casco: {value:.0f} m²"
        }
        
        return descriptions.get(feature_name, f"{feature_name}: {value}")
    
    def _generate_explanation_text(
        self,
        contributions: List[FeatureContribution],
        prediction: float
    ) -> str:
        """
        Gera texto explicativo em linguagem natural.
        """
        text = f"A predição de bioincrustação de {prediction:.2f} mm é influenciada principalmente por:\n\n"
        
        # Top 3 fatores
        top_factors = sorted(contributions, key=lambda x: abs(x.contribution), reverse=True)[:3]
        
        for i, factor in enumerate(top_factors, 1):
            direction = "aumenta" if factor.contribution > 0 else "reduz"
            text += f"{i}. {factor.feature_name}: {factor.description}. "
            text += f"Este fator {direction} a bioincrustação em {abs(factor.percentage):.1f}% da predição total.\n"
        
        text += f"\nOutros fatores contribuem com {100 - sum(f.percentage for f in top_factors):.1f}% restante."
        
        return text
    
    def explain_fuel_impact(
        self,
        ideal_consumption: float,
        real_consumption: float,
        contributing_factors: Dict[str, float]
    ) -> PredictionExplanation:
        """
        Explica impacto no consumo de combustível.
        """
        delta = real_consumption - ideal_consumption
        delta_percent = (delta / ideal_consumption * 100) if ideal_consumption > 0 else 0
        
        contributions = []
        total_abs = sum(abs(v) for v in contributing_factors.values())
        
        for factor_name, contribution in contributing_factors.items():
            percentage = (abs(contribution) / total_abs * 100) if total_abs > 0 else 0
            contributions.append(FeatureContribution(
                feature_name=factor_name.replace('_', ' ').title(),
                contribution=contribution,
                percentage=percentage,
                description=self._get_fuel_factor_description(factor_name, contribution)
            ))
        
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        explanation_text = (
            f"O consumo real ({real_consumption:.2f} kg/h) é {delta_percent:.1f}% maior que o ideal "
            f"({ideal_consumption:.2f} kg/h), resultando em um aumento de {delta:.2f} kg/h.\n\n"
            f"Principais fatores:\n"
        )
        
        for factor in contributions[:3]:
            direction = "aumenta" if factor.contribution > 0 else "reduz"
            explanation_text += f"- {factor.feature_name}: {direction} consumo em {abs(factor.contribution):.1f}%\n"
        
        return PredictionExplanation(
            prediction_id=f"fuel_impact_{datetime.now().timestamp()}",
            prediction_value=delta_percent,
            base_value=ideal_consumption,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.85,
            model_type="fuel_impact"
        )
    
    def _get_fuel_factor_description(self, factor_name: str, contribution: float) -> str:
        """
        Gera descrição de fator de impacto no combustível.
        """
        descriptions = {
            'fouling': f"Bioincrustação contribui com {abs(contribution):.1f}% do aumento",
            'weather': f"Condições climáticas contribuem com {abs(contribution):.1f}%",
            'load': f"Carga da embarcação contribui com {abs(contribution):.1f}%",
            'other': f"Outros fatores contribuem com {abs(contribution):.1f}%"
        }
        
        return descriptions.get(factor_name, f"{factor_name}: {contribution:.1f}%")
    
    def explain_normam401_risk(
        self,
        risk_prediction,
        vessel_features: Dict
    ) -> PredictionExplanation:
        """
        Explica predição de risco NORMAM 401.
        
        Args:
            risk_prediction: Predição de risco (NORMAM401RiskPrediction)
            vessel_features: Features da embarcação
            
        Returns:
            Explicação da predição de risco
        """
        contributions = []
        
        # Contribuição dos fatores de risco
        for factor in risk_prediction.risk_factors:
            contributions.append(FeatureContribution(
                feature_name=factor.factor_name,
                contribution=factor.contribution,
                percentage=factor.contribution * 100,
                description=factor.description
            ))
        
        # Normalizar contribuições
        total = sum(abs(c.contribution) for c in contributions)
        if total > 0:
            for c in contributions:
                c.percentage = (abs(c.contribution) / total) * 100
        
        # Gerar texto explicativo
        explanation_text = (
            f"O risco de não conformidade NORMAM 401 é {risk_prediction.risk_score:.1%} "
            f"(nível: {risk_prediction.risk_level.value}).\n\n"
            f"Em {risk_prediction.days_ahead} dias, a bioincrustação prevista é "
            f"{risk_prediction.predicted_fouling_mm:.2f} mm "
            f"(limite: 5.0 mm), resultando em status: {risk_prediction.predicted_compliance_status}.\n\n"
            f"Principais fatores de risco:\n"
        )
        
        top_factors = sorted(contributions, key=lambda x: abs(x.contribution), reverse=True)[:3]
        for i, factor in enumerate(top_factors, 1):
            explanation_text += f"{i}. {factor.feature_name}: {factor.description}\n"
        
        return PredictionExplanation(
            prediction_id=f"risk_{risk_prediction.vessel_id}_{risk_prediction.prediction_date.timestamp()}",
            prediction_value=risk_prediction.risk_score,
            base_value=0.0,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=risk_prediction.confidence,
            model_type="normam401_risk"
        )
    
    def explain_cleaning_recommendation(
        self,
        recommendation,
        current_fouling: float,
        predicted_fouling: float,
        days_ahead: int
    ) -> PredictionExplanation:
        """
        Explica recomendação de limpeza.
        
        Args:
            recommendation: Recomendação de limpeza
            current_fouling: Bioincrustação atual (mm)
            predicted_fouling: Bioincrustação prevista (mm)
            days_ahead: Dias à frente da predição
            
        Returns:
            Explicação da recomendação
        """
        growth_rate = (predicted_fouling - current_fouling) / days_ahead if days_ahead > 0 else 0
        
        contributions = [
            FeatureContribution(
                feature_name="Bioincrustação Atual",
                contribution=current_fouling / 5.0,  # Normalizado pelo limite
                percentage=50.0,
                description=f"Bioincrustação atual: {current_fouling:.2f} mm"
            ),
            FeatureContribution(
                feature_name="Taxa de Crescimento",
                contribution=growth_rate * 10,  # Normalizado
                percentage=30.0,
                description=f"Taxa de crescimento: {growth_rate:.3f} mm/dia"
            ),
            FeatureContribution(
                feature_name="Bioincrustação Prevista",
                contribution=predicted_fouling / 5.0,
                percentage=20.0,
                description=f"Bioincrustação prevista em {days_ahead} dias: {predicted_fouling:.2f} mm"
            )
        ]
        
        explanation_text = (
            f"Recomendação: {recommendation.recommendation_type.value}\n\n"
            f"Motivo: A bioincrustação atual ({current_fouling:.2f} mm) está crescendo a uma taxa de "
            f"{growth_rate:.3f} mm/dia. Em {days_ahead} dias, prevê-se {predicted_fouling:.2f} mm, "
            f"o que {'excede' if predicted_fouling > 5.0 else 'aproxima-se do'} limite de 5.0 mm.\n\n"
            f"Benefícios esperados:\n"
            f"- Redução de consumo de combustível: {recommendation.estimated_fuel_savings_percent:.1f}%\n"
            f"- Economia estimada: R$ {recommendation.estimated_economy_brl:,.2f}\n"
            f"- Redução de CO₂: {recommendation.estimated_co2_reduction_kg:,.0f} kg\n"
        )
        
        return PredictionExplanation(
            prediction_id=f"recommendation_{recommendation.vessel_id}_{datetime.now().timestamp()}",
            prediction_value=predicted_fouling,
            base_value=current_fouling,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.85,
            model_type="cleaning_recommendation"
        )
    
    def explain_anomaly_detection(
        self,
        anomaly
    ) -> PredictionExplanation:
        """
        Explica detecção de anomalia.
        
        Args:
            anomaly: Anomalia detectada
            
        Returns:
            Explicação da anomalia
        """
        contributions = []
        
        # Contribuição baseada no tipo de anomalia
        if anomaly.anomaly_type.value == "sudden_change":
            contributions.append(FeatureContribution(
                feature_name="Mudança Súbita",
                contribution=1.0,
                percentage=100.0,
                description=anomaly.description
            ))
        elif anomaly.anomaly_type.value == "concerning_trend":
            contributions.append(FeatureContribution(
                feature_name="Tendência Preocupante",
                contribution=1.0,
                percentage=100.0,
                description=anomaly.description
            ))
        else:
            contributions.append(FeatureContribution(
                feature_name=anomaly.anomaly_type.value.replace("_", " ").title(),
                contribution=1.0,
                percentage=100.0,
                description=anomaly.description
            ))
        
        explanation_text = (
            f"Anomalia Detectada: {anomaly.anomaly_type.value.replace('_', ' ').title()}\n\n"
            f"Severidade: {anomaly.severity.value.upper()}\n"
            f"Descrição: {anomaly.description}\n\n"
            f"Métricas Afetadas: {', '.join(anomaly.affected_metrics)}\n\n"
            f"Recomendação: {anomaly.recommendation}\n\n"
            f"Confiança na Detecção: {anomaly.confidence:.1%}"
        )
        
        return PredictionExplanation(
            prediction_id=anomaly.anomaly_id,
            prediction_value=anomaly.confidence,
            base_value=0.0,
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=anomaly.confidence,
            model_type="anomaly_detection"
        )
    
    def explain_compliance_status(
        self,
        compliance_check
    ) -> PredictionExplanation:
        """
        Explica status de conformidade NORMAM 401.
        
        Args:
            compliance_check: Verificação de conformidade
            
        Returns:
            Explicação do status
        """
        contributions = []
        
        # Contribuição da bioincrustação
        thickness_ratio = compliance_check.fouling_thickness_mm / compliance_check.max_allowed_thickness_mm
        contributions.append(FeatureContribution(
            feature_name="Espessura de Bioincrustação",
            contribution=thickness_ratio - 1.0,  # Negativo se abaixo do limite
            percentage=60.0,
            description=(
                f"{compliance_check.fouling_thickness_mm:.2f} mm "
                f"(limite: {compliance_check.max_allowed_thickness_mm:.2f} mm)"
            )
        ))
        
        # Contribuição da rugosidade
        roughness_ratio = compliance_check.roughness_um / compliance_check.max_allowed_roughness_um
        contributions.append(FeatureContribution(
            feature_name="Rugosidade",
            contribution=roughness_ratio - 1.0,
            percentage=40.0,
            description=(
                f"{compliance_check.roughness_um:.2f} μm "
                f"(limite: {compliance_check.max_allowed_roughness_um:.2f} μm)"
            )
        ))
        
        # Gerar texto explicativo
        explanation_text = (
            f"Status de Conformidade: {compliance_check.status.value.upper()}\n\n"
            f"Score de Conformidade: {compliance_check.compliance_score:.1%}\n\n"
        )
        
        if compliance_check.violations:
            explanation_text += f"Violações ({len(compliance_check.violations)}):\n"
            for violation in compliance_check.violations:
                explanation_text += f"- {violation}\n"
            explanation_text += "\n"
        
        if compliance_check.warnings:
            explanation_text += f"Avisos ({len(compliance_check.warnings)}):\n"
            for warning in compliance_check.warnings:
                explanation_text += f"- {warning}\n"
            explanation_text += "\n"
        
        explanation_text += "Recomendações:\n"
        for rec in compliance_check.recommendations:
            explanation_text += f"- {rec}\n"
        
        return PredictionExplanation(
            prediction_id=f"compliance_{compliance_check.vessel_id}_{compliance_check.check_date.timestamp()}",
            prediction_value=compliance_check.compliance_score,
            base_value=1.0,  # Conformidade total
            feature_contributions=contributions,
            explanation_text=explanation_text,
            confidence=0.9,
            model_type="compliance_status"
        )


# Função de conveniência
def explain_prediction(
    model,
    features: Dict,
    prediction: float
) -> PredictionExplanation:
    """
    Explica uma predição.
    
    Args:
        model: Modelo (ou None para modelo físico)
        features: Features de entrada
        prediction: Valor da predição
        
    Returns:
        Explicação da predição
    """
    explainer = ModelExplainer()
    return explainer.explain_fouling_prediction(model, features, prediction)


if __name__ == "__main__":
    # Exemplo de uso
    features = {
        'time_since_cleaning_days': 90,
        'water_temperature_c': 25.0,
        'salinity_psu': 32.5,
        'time_in_port_hours': 120,
        'average_speed_knots': 12.0,
        'route_region': 'South_Atlantic',
        'paint_type': 'Antifouling_Type_A',
        'vessel_type': 'Tanker',
        'hull_area_m2': 5000.0
    }
    
    explanation = explain_prediction(None, features, 4.5)
    
    print("Explicação da Predição:")
    print(f"Valor Predito: {explanation.prediction_value:.2f} mm")
    print(f"\nContribuições:")
    for contrib in explanation.feature_contributions:
        print(f"  {contrib.feature_name}: {contrib.contribution:+.3f} ({contrib.percentage:.1f}%)")
    print(f"\nExplicação Textual:\n{explanation.explanation_text}")

