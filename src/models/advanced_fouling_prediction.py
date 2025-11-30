"""
Modelo Avançado de Predição de Bioincrustação - HullZero

Este módulo implementa modelos de IA avançados baseados em pesquisas científicas,
incluindo dados sobre extratos de macrófitas aquáticas, espécies invasoras (coral sol),
e técnicas de machine learning de última geração.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# ML Libraries Avançadas
from sklearn.ensemble import (
    RandomForestRegressor, 
    GradientBoostingRegressor,
    ExtraTreesRegressor,
    VotingRegressor
)
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from xgboost import XGBRegressor

# Deep Learning (opcional)
try:
    from sklearn.neural_network import MLPRegressor
    MLP_AVAILABLE = True
except ImportError:
    MLP_AVAILABLE = False

# Time Series Avançado
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

# Physical Constants
CO2_EMISSION_FACTOR = 3.15  # kg CO2 per kg fuel

# Dados baseados em pesquisas científicas
# Fonte: Tese Mikael Luiz Morales Pereira (2025) - FURG
MACROPHYTE_EXTRACTS_EFFICACY = {
    "Potamogeton_pectinatus": 0.85,  # Alta eficácia anti-incrustante
    "Hydrilla_verticillata": 0.78,
    "Egeria_densa": 0.72,
    "Myriophyllum_aquaticum": 0.68,
    "Ceratophyllum_demersum": 0.75
}

# Espécies invasoras críticas (Coral Sol - Tubastraea coccinea)
INVASIVE_SPECIES_RISK = {
    "Tubastraea_coccinea": {
        "growth_rate_multiplier": 1.5,  # 50% mais rápido
        "hardness_factor": 1.3,  # Mais difícil de remover
        "regions": ["Brazil_Coast", "South_Atlantic", "Tropical"]
    },
    "Mytilopsis_leucophaeata": {
        "growth_rate_multiplier": 1.2,
        "hardness_factor": 1.1,
        "regions": ["Inland_Waterways", "Estuaries"]
    }
}


@dataclass
class AdvancedFoulingPrediction:
    """Resultado avançado de predição de bioincrustação"""
    timestamp: datetime
    estimated_thickness_mm: float
    estimated_roughness_um: float
    fouling_severity: str
    confidence_score: float
    predicted_fuel_impact_percent: float
    predicted_co2_impact_kg: float
    invasive_species_risk: Dict[str, float]  # Risco por espécie invasora
    natural_control_recommendations: List[str]  # Recomendações de controle natural
    model_ensemble_contributions: Dict[str, float]  # Contribuição de cada modelo
    feature_importance: Dict[str, float]  # Importância das features


@dataclass
class AdvancedVesselFeatures:
    """Features avançadas para predição"""
    vessel_id: str
    time_since_cleaning_days: int
    water_temperature_c: float
    salinity_psu: float
    time_in_port_hours: float
    average_speed_knots: float
    route_region: str
    paint_type: str
    vessel_type: str
    hull_area_m2: float
    # Features adicionais baseadas em pesquisas
    last_cleaning_method: Optional[str] = None
    paint_age_days: Optional[int] = None
    port_water_quality_index: Optional[float] = None  # 0-1, qualidade da água do porto
    seasonal_factor: Optional[str] = None  # 'summer', 'winter', 'spring', 'autumn'
    chlorophyll_a_concentration: Optional[float] = None  # mg/m³ (nutrientes)
    dissolved_oxygen: Optional[float] = None  # mg/L
    ph_level: Optional[float] = None  # pH da água
    turbidity: Optional[float] = None  # NTU
    current_velocity: Optional[float] = None  # m/s
    depth_m: Optional[float] = None  # Profundidade média de operação


class AdvancedPhysicalModel:
    """
    Modelo físico avançado baseado em princípios de biologia marinha,
    incluindo fatores de espécies invasoras e condições ambientais.
    """
    
    def __init__(self):
        # Parâmetros baseados em pesquisas científicas
        self.growth_rate_base = 0.05  # mm/day
        self.temperature_optimum = 25.0  # °C
        self.temperature_range = (18.0, 32.0)  # Faixa ótima
        self.salinity_optimum = 32.5  # PSU
        self.salinity_range = (28.0, 38.0)
        
    def calculate_temperature_factor(self, temperature: float) -> float:
        """Fator de temperatura (curva gaussiana melhorada)"""
        if self.temperature_range[0] <= temperature <= self.temperature_range[1]:
            # Dentro da faixa ótima
            temp_factor = np.exp(-0.5 * ((temperature - self.temperature_optimum) / 4.0) ** 2)
        else:
            # Fora da faixa ótima - crescimento reduzido
            if temperature < self.temperature_range[0]:
                temp_factor = 0.3 * np.exp(-0.5 * ((temperature - self.temperature_range[0]) / 3.0) ** 2)
            else:
                temp_factor = 0.3 * np.exp(-0.5 * ((temperature - self.temperature_range[1]) / 3.0) ** 2)
        return max(0.1, min(1.0, temp_factor))
    
    def calculate_salinity_factor(self, salinity: float) -> float:
        """Fator de salinidade"""
        if self.salinity_range[0] <= salinity <= self.salinity_range[1]:
            salinity_factor = np.exp(-0.5 * ((salinity - self.salinity_optimum) / 3.0) ** 2)
        else:
            salinity_factor = 0.5
        return max(0.1, min(1.0, salinity_factor))
    
    def calculate_nutrient_factor(self, chlorophyll_a: Optional[float], do: Optional[float]) -> float:
        """Fator de nutrientes (clorofila-a e oxigênio dissolvido)"""
        nutrient_factor = 1.0
        
        if chlorophyll_a is not None:
            # Mais nutrientes = mais crescimento (até certo ponto)
            # Ótimo: 2-5 mg/m³
            if 2.0 <= chlorophyll_a <= 5.0:
                nutrient_factor *= 1.2
            elif chlorophyll_a > 10.0:
                nutrient_factor *= 1.4  # Eutrofização
            elif chlorophyll_a < 0.5:
                nutrient_factor *= 0.8  # Águas oligotróficas
        
        if do is not None:
            # Oxigênio dissolvido afeta crescimento
            if do < 4.0:  # Hipóxia
                nutrient_factor *= 0.7
            elif do > 8.0:  # Águas bem oxigenadas
                nutrient_factor *= 1.1
        
        return nutrient_factor
    
    def calculate_invasive_species_risk(
        self,
        route_region: str,
        water_temperature_c: float
    ) -> Dict[str, float]:
        """Calcula risco de espécies invasoras baseado em região e temperatura"""
        risks = {}
        
        for species, data in INVASIVE_SPECIES_RISK.items():
            if route_region in data["regions"]:
                # Temperatura adequada para coral sol: 20-30°C
                if species == "Tubastraea_coccinea":
                    if 20.0 <= water_temperature_c <= 30.0:
                        temp_suitability = 1.0
                    else:
                        temp_suitability = 0.5
                else:
                    temp_suitability = 1.0
                
                risk = data["growth_rate_multiplier"] * temp_suitability
                risks[species] = min(1.0, risk)
            else:
                risks[species] = 0.1  # Risco baixo fora da região
        
        return risks
    
    def predict_growth(
        self,
        features: AdvancedVesselFeatures
    ) -> Tuple[float, Dict[str, float]]:
        """
        Prediz crescimento usando modelo físico avançado.
        
        Returns:
            (thickness_mm, invasive_species_risks)
        """
        days = features.time_since_cleaning_days
        
        # Fatores ambientais
        temp_factor = self.calculate_temperature_factor(features.water_temperature_c)
        salinity_factor = self.calculate_salinity_factor(features.salinity_psu)
        nutrient_factor = self.calculate_nutrient_factor(
            features.chlorophyll_a_concentration,
            features.dissolved_oxygen
        )
        
        # Fator de tempo em porto
        port_factor = 1.0 + (features.time_in_port_hours / 24.0) * 0.15
        
        # Fator de velocidade (reduz crescimento)
        speed_factor = max(0.2, 1.0 - (features.average_speed_knots / 20.0) * 0.8)
        
        # Fator sazonal
        seasonal_multiplier = 1.0
        if features.seasonal_factor:
            seasonal_factors = {
                'summer': 1.3,  # Maior crescimento no verão
                'spring': 1.1,
                'autumn': 0.9,
                'winter': 0.7
            }
            seasonal_multiplier = seasonal_factors.get(features.seasonal_factor, 1.0)
        
        # Risco de espécies invasoras
        invasive_risks = self.calculate_invasive_species_risk(
            features.route_region,
            features.water_temperature_c
        )
        
        # Ajuste por espécies invasoras
        max_invasive_risk = max(invasive_risks.values()) if invasive_risks else 0.0
        invasive_factor = 1.0 + (max_invasive_risk - 1.0) * 0.5  # Até 25% de aumento
        
        # Taxa de crescimento combinada
        growth_rate = (
            self.growth_rate_base *
            temp_factor *
            salinity_factor *
            nutrient_factor *
            port_factor *
            speed_factor *
            seasonal_multiplier *
            invasive_factor
        )
        
        # Modelo de crescimento (exponencial com saturação)
        max_thickness = 15.0  # mm
        thickness = max_thickness * (1 - np.exp(-growth_rate * days / 30.0))
        
        return max(0.0, thickness), invasive_risks


class AdvancedMLModel:
    """
    Modelo de Machine Learning avançado com ensemble de múltiplos algoritmos.
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.is_trained = False
        self.feature_importance = {}
        
    def prepare_features(self, features: AdvancedVesselFeatures) -> np.ndarray:
        """Prepara features avançadas"""
        # Features numéricas
        numeric_features = [
            features.time_since_cleaning_days,
            features.water_temperature_c,
            features.salinity_psu,
            features.time_in_port_hours,
            features.average_speed_knots,
            features.hull_area_m2,
        ]
        
        # Features opcionais
        if features.paint_age_days is not None:
            numeric_features.append(features.paint_age_days)
        else:
            numeric_features.append(180.0)  # Default
        
        if features.port_water_quality_index is not None:
            numeric_features.append(features.port_water_quality_index)
        else:
            numeric_features.append(0.7)  # Default
        
        if features.chlorophyll_a_concentration is not None:
            numeric_features.append(features.chlorophyll_a_concentration)
        else:
            numeric_features.append(2.0)  # Default
        
        if features.dissolved_oxygen is not None:
            numeric_features.append(features.dissolved_oxygen)
        else:
            numeric_features.append(6.0)  # Default
        
        if features.ph_level is not None:
            numeric_features.append(features.ph_level)
        else:
            numeric_features.append(7.5)  # Default
        
        if features.turbidity is not None:
            numeric_features.append(features.turbidity)
        else:
            numeric_features.append(5.0)  # Default
        
        if features.current_velocity is not None:
            numeric_features.append(features.current_velocity)
        else:
            numeric_features.append(0.5)  # Default
        
        if features.depth_m is not None:
            numeric_features.append(features.depth_m)
        else:
            numeric_features.append(20.0)  # Default
        
        # Encoding categórico
        route_encoded = hash(features.route_region) % 100
        paint_encoded = hash(features.paint_type) % 100
        vessel_encoded = hash(features.vessel_type) % 100
        
        if features.seasonal_factor:
            season_encoded = hash(features.seasonal_factor) % 10
        else:
            season_encoded = 5
        
        numeric_features.extend([route_encoded, paint_encoded, vessel_encoded, season_encoded])
        
        return np.array(numeric_features).reshape(1, -1)
    
    def train_ensemble(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2
    ):
        """Treina ensemble de modelos"""
        # Split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Normalização
        scaler = RobustScaler()  # Mais robusto que StandardScaler
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        self.scalers['main'] = scaler
        
        # Modelos individuais
        models = {
            'xgb': XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            ),
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gbr': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            ),
            'etr': ExtraTreesRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # Treinar e avaliar cada modelo
        model_scores = {}
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_val_scaled)
            score = r2_score(y_val, y_pred)
            model_scores[name] = score
            self.models[name] = model
        
        # Ensemble com pesos baseados em performance
        total_score = sum(model_scores.values())
        weights = {name: score / total_score for name, score in model_scores.items()}
        
        # Criar ensemble
        ensemble_models = [
            (name, model) for name, model in self.models.items()
        ]
        
        self.models['ensemble'] = VotingRegressor(
            estimators=ensemble_models,
            weights=[weights.get(name, 0.25) for name, _ in ensemble_models]
        )
        
        # Feature importance (do melhor modelo)
        best_model_name = max(model_scores, key=model_scores.get)
        if hasattr(self.models[best_model_name], 'feature_importances_'):
            importances = self.models[best_model_name].feature_importances_
            feature_names = [
                'days_since_cleaning', 'temperature', 'salinity', 'time_in_port',
                'speed', 'hull_area', 'paint_age', 'water_quality', 'chlorophyll_a',
                'dissolved_oxygen', 'ph', 'turbidity', 'current_velocity', 'depth',
                'route', 'paint', 'vessel', 'season'
            ]
            self.feature_importance = dict(zip(feature_names, importances))
        
        self.is_trained = True
    
    def predict(self, features: AdvancedVesselFeatures) -> Tuple[float, Dict[str, float]]:
        """Prediz usando ensemble"""
        if not self.is_trained:
            # Fallback para modelo simples
            return self._simple_predict(features), {}
        
        X = self.prepare_features(features)
        X_scaled = self.scalers['main'].transform(X)
        
        # Predição do ensemble
        ensemble_pred = self.models['ensemble'].predict(X_scaled)[0]
        
        # Contribuições individuais
        contributions = {}
        for name, model in self.models.items():
            if name != 'ensemble':
                pred = model.predict(X_scaled)[0]
                contributions[name] = float(pred)
        
        return max(0.0, ensemble_pred), contributions


class AdvancedHybridModel:
    """
    Modelo híbrido avançado combinando física e ML com ensemble.
    """
    
    def __init__(self):
        self.physical_model = AdvancedPhysicalModel()
        self.ml_model = AdvancedMLModel()
        self.physical_weight = 0.25  # Reduzido para dar mais peso ao ML
        self.ml_weight = 0.75
    
    def get_natural_control_recommendations(
        self,
        route_region: str,
        fouling_thickness_mm: float
    ) -> List[str]:
        """Recomendações de controle natural baseadas em pesquisas"""
        recommendations = []
        
        if fouling_thickness_mm > 3.0:
            recommendations.append(
                "Considerar uso de extratos de Potamogeton pectinatus "
                "(eficácia comprovada: 85%) como alternativa natural"
            )
        
        if route_region in ["Inland_Waterways", "Estuaries"]:
            recommendations.append(
                "Extratos de Hydrilla verticillata podem ser eficazes "
                "em ambientes de água doce/estuarinos"
            )
        
        if fouling_thickness_mm > 5.0:
            recommendations.append(
                "Aplicação de revestimentos com aditivos naturais de macrófitas "
                "pode reduzir crescimento em até 30%"
            )
        
        return recommendations
    
    def predict(
        self,
        features: AdvancedVesselFeatures,
        historical_data: Optional[pd.DataFrame] = None
    ) -> AdvancedFoulingPrediction:
        """
        Prediz bioincrustação usando modelo híbrido avançado.
        """
        # Predição física
        physical_thickness, invasive_risks = self.physical_model.predict_growth(features)
        
        # Predição ML
        ml_thickness, model_contributions = self.ml_model.predict(features)
        
        # Combinação híbrida
        hybrid_thickness = (
            self.physical_weight * physical_thickness +
            self.ml_weight * ml_thickness
        )
        
        # Rugosidade (modelo físico)
        roughness = 50.0 * hybrid_thickness + 100.0
        roughness = min(roughness, 1000.0)
        
        # Severidade
        if hybrid_thickness < 2.0:
            severity = 'light'
        elif hybrid_thickness < 5.0:
            severity = 'moderate'
        elif hybrid_thickness < 8.0:
            severity = 'severe'
        else:
            severity = 'critical'
        
        # Confiança (baseada na consistência)
        if model_contributions:
            std_dev = np.std(list(model_contributions.values()))
            consistency = 1.0 / (1.0 + std_dev)
        else:
            consistency = 0.8
        
        agreement = 1.0 - abs(physical_thickness - ml_thickness) / max(physical_thickness, ml_thickness, 1.0)
        confidence = (consistency * 0.6 + agreement * 0.4)
        confidence = max(0.6, min(0.98, confidence))
        
        # Impacto no combustível (estimativa melhorada)
        # Baseado em pesquisas: até 50% de aumento com bioincrustação severa
        if hybrid_thickness < 2.0:
            fuel_impact = hybrid_thickness * 2.0  # 2% por mm
        elif hybrid_thickness < 5.0:
            fuel_impact = 4.0 + (hybrid_thickness - 2.0) * 3.0  # 4-13%
        else:
            fuel_impact = 13.0 + (hybrid_thickness - 5.0) * 7.0  # 13-50%
        
        fuel_impact = min(50.0, fuel_impact)
        
        # CO2 impact
        # Assumindo consumo típico de 1000 kg/h
        typical_consumption = 1000.0  # kg/h
        co2_impact = (typical_consumption * fuel_impact / 100.0) * CO2_EMISSION_FACTOR
        
        # Recomendações de controle natural
        natural_recommendations = self.get_natural_control_recommendations(
            features.route_region,
            hybrid_thickness
        )
        
        # Feature importance
        feature_importance = self.ml_model.feature_importance.copy() if self.ml_model.feature_importance else {}
        
        return AdvancedFoulingPrediction(
            timestamp=datetime.now(),
            estimated_thickness_mm=round(hybrid_thickness, 2),
            estimated_roughness_um=round(roughness, 2),
            fouling_severity=severity,
            confidence_score=round(confidence, 3),
            predicted_fuel_impact_percent=round(fuel_impact, 2),
            predicted_co2_impact_kg=round(co2_impact, 2),
            invasive_species_risk=invasive_risks,
            natural_control_recommendations=natural_recommendations,
            model_ensemble_contributions=model_contributions,
            feature_importance=feature_importance
        )


# Função de conveniência
def predict_advanced_fouling(
    features: AdvancedVesselFeatures,
    historical_data: Optional[pd.DataFrame] = None
) -> AdvancedFoulingPrediction:
    """
    Prediz bioincrustação usando modelo avançado.
    
    Args:
        features: Features avançadas da embarcação
        historical_data: Dados históricos para treinamento (opcional)
        
    Returns:
        Predição avançada
    """
    model = AdvancedHybridModel()
    
    # Se dados históricos disponíveis, treinar
    if historical_data is not None and len(historical_data) > 50:
        # Preparar dados de treinamento
        X = []
        y = []
        for _, row in historical_data.iterrows():
            # Criar features do histórico
            hist_features = AdvancedVesselFeatures(
                vessel_id=row.get('vessel_id', ''),
                time_since_cleaning_days=int(row.get('days_since_cleaning', 0)),
                water_temperature_c=float(row.get('temperature', 25.0)),
                salinity_psu=float(row.get('salinity', 32.5)),
                time_in_port_hours=float(row.get('time_in_port', 0)),
                average_speed_knots=float(row.get('speed', 12.0)),
                route_region=row.get('route', 'South_Atlantic'),
                paint_type=row.get('paint', 'Antifouling_Type_A'),
                vessel_type=row.get('vessel_type', 'tanker'),
                hull_area_m2=float(row.get('hull_area', 5000.0))
            )
            X.append(model.ml_model.prepare_features(hist_features)[0])
            y.append(float(row.get('fouling_thickness', 0)))
        
        X = np.array(X)
        y = np.array(y)
        
        # Treinar modelo
        model.ml_model.train_ensemble(X, y)
    
    return model.predict(features, historical_data)

