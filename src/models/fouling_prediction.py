"""
Modelo de Predição de Bioincrustação - HullZero

Este módulo implementa modelos híbridos (física + ML) para predição
de crescimento de bioincrustação em cascos de embarcações.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Time Series
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

# Physical Constants
CO2_EMISSION_FACTOR = 3.15  # kg CO2 per kg fuel


@dataclass
class FoulingPrediction:
    """Resultado de predição de bioincrustação"""
    timestamp: datetime
    estimated_thickness_mm: float
    estimated_roughness_um: float
    fouling_severity: str  # 'light', 'moderate', 'severe'
    confidence_score: float
    predicted_fuel_impact_percent: float
    predicted_co2_impact_kg: float


@dataclass
class VesselFeatures:
    """Features de uma embarcação para predição"""
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


class PhysicalFoulingModel:
    """
    Modelo físico baseado em princípios de biologia marinha
    e hidrodinâmica.
    """
    
    def __init__(self):
        # Parâmetros do modelo físico
        self.growth_rate_base = 0.05  # mm/day (base)
        self.temperature_optimum = 25.0  # °C
        self.salinity_optimum = 32.5  # PSU
        self.velocity_reduction_factor = 0.8  # Redução por velocidade
        
    def predict_growth(
        self,
        days_since_cleaning: int,
        temperature: float,
        salinity: float,
        time_in_port: float,
        average_speed: float
    ) -> float:
        """
        Prediz crescimento de bioincrustação usando modelo físico.
        
        Args:
            days_since_cleaning: Dias desde última limpeza
            temperature: Temperatura da água (°C)
            salinity: Salinidade (PSU)
            time_in_port: Tempo em porto (horas)
            average_speed: Velocidade média (nós)
            
        Returns:
            Espessura estimada em mm
        """
        # Fator de temperatura (curva gaussiana)
        temp_factor = np.exp(-0.5 * ((temperature - self.temperature_optimum) / 5.0) ** 2)
        
        # Fator de salinidade (curva gaussiana)
        salinity_factor = np.exp(-0.5 * ((salinity - self.salinity_optimum) / 3.0) ** 2)
        
        # Fator de tempo em porto (aumenta crescimento)
        port_factor = 1.0 + (time_in_port / 24.0) * 0.1  # +10% por dia em porto
        
        # Fator de velocidade (reduz crescimento)
        speed_factor = 1.0 - (average_speed / 20.0) * self.velocity_reduction_factor
        speed_factor = max(0.2, speed_factor)  # Mínimo 20%
        
        # Crescimento exponencial com saturação
        growth_rate = self.growth_rate_base * temp_factor * salinity_factor * port_factor * speed_factor
        
        # Modelo de crescimento (exponencial com saturação)
        max_thickness = 15.0  # mm (saturação)
        thickness = max_thickness * (1 - np.exp(-growth_rate * days_since_cleaning / 30.0))
        
        return thickness
    
    def calculate_roughness(self, thickness_mm: float) -> float:
        """
        Calcula rugosidade baseada na espessura.
        
        Args:
            thickness_mm: Espessura de bioincrustação (mm)
            
        Returns:
            Rugosidade em micrômetros
        """
        # Relação empírica: rugosidade ~ 50 * espessura
        roughness = 50.0 * thickness_mm + 100.0  # Base de 100 um
        return min(roughness, 1000.0)  # Máximo 1000 um


class MLFoulingModel:
    """
    Modelo de Machine Learning para predição de bioincrustação.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, features: VesselFeatures) -> np.ndarray:
        """
        Prepara features para o modelo ML.
        
        Args:
            features: Features da embarcação
            
        Returns:
            Array de features normalizadas
        """
        feature_array = np.array([
            features.time_since_cleaning_days,
            features.water_temperature_c,
            features.salinity_psu,
            features.time_in_port_hours,
            features.average_speed_knots,
            # Encoding de variáveis categóricas (simplificado)
            hash(features.route_region) % 100,
            hash(features.paint_type) % 100,
            hash(features.vessel_type) % 100,
            features.hull_area_m2
        ])
        
        return feature_array.reshape(1, -1)
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Treina o modelo ML.
        
        Args:
            X: Features (n_samples, n_features)
            y: Targets (n_samples,)
        """
        # Normalização
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinamento com XGBoost
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, features: VesselFeatures) -> float:
        """
        Prediz espessura de bioincrustação.
        
        Args:
            features: Features da embarcação
            
        Returns:
            Espessura estimada em mm
        """
        if not self.is_trained:
            # Retorna predição base (modelo não treinado)
            return 2.0
        
        X = self.prepare_features(features)
        X_scaled = self.scaler.transform(X)
        
        thickness = self.model.predict(X_scaled)[0]
        return max(0.0, thickness)  # Não negativo


class HybridFoulingModel:
    """
    Modelo híbrido que combina física e ML.
    """
    
    def __init__(self):
        self.physical_model = PhysicalFoulingModel()
        self.ml_model = MLFoulingModel()
        self.physical_weight = 0.3
        self.ml_weight = 0.7
    
    def predict(
        self,
        features: VesselFeatures,
        historical_data: Optional[pd.DataFrame] = None
    ) -> FoulingPrediction:
        """
        Prediz bioincrustação usando modelo híbrido.
        
        Args:
            features: Features da embarcação
            historical_data: Dados históricos (opcional, para treinamento)
            
        Returns:
            Predição de bioincrustação
        """
        # Predição física
        physical_thickness = self.physical_model.predict_growth(
            days_since_cleaning=features.time_since_cleaning_days,
            temperature=features.water_temperature_c,
            salinity=features.salinity_psu,
            time_in_port=features.time_in_port_hours,
            average_speed=features.average_speed_knots
        )
        
        # Predição ML
        ml_thickness = self.ml_model.predict(features)
        
        # Combinação híbrida
        hybrid_thickness = (
            self.physical_weight * physical_thickness +
            self.ml_weight * ml_thickness
        )
        
        # Rugosidade
        roughness = self.physical_model.calculate_roughness(hybrid_thickness)
        
        # Severidade
        if hybrid_thickness < 3.0:
            severity = 'light'
        elif hybrid_thickness < 8.0:
            severity = 'moderate'
        else:
            severity = 'severe'
        
        # Confiança (baseada na consistência entre modelos)
        confidence = 1.0 - abs(physical_thickness - ml_thickness) / max(physical_thickness, ml_thickness, 1.0)
        confidence = max(0.5, min(1.0, confidence))
        
        # Impacto no combustível (estimativa)
        fuel_impact_percent = self._estimate_fuel_impact(hybrid_thickness, roughness)
        
        # Impacto em CO2 (estimativa)
        co2_impact = self._estimate_co2_impact(fuel_impact_percent, features)
        
        return FoulingPrediction(
            timestamp=datetime.now(),
            estimated_thickness_mm=hybrid_thickness,
            estimated_roughness_um=roughness,
            fouling_severity=severity,
            confidence_score=confidence,
            predicted_fuel_impact_percent=fuel_impact_percent,
            predicted_co2_impact_kg=co2_impact
        )
    
    def _estimate_fuel_impact(self, thickness_mm: float, roughness_um: float) -> float:
        """
        Estima impacto percentual no consumo de combustível.
        
        Args:
            thickness_mm: Espessura de bioincrustação (mm)
            roughness_um: Rugosidade (μm)
            
        Returns:
            Aumento percentual no consumo
        """
        # Relação empírica: ~1% de aumento por mm de espessura
        # + ~0.1% por 100 um de rugosidade
        impact = (thickness_mm * 1.0) + (roughness_um / 100.0 * 0.1)
        return min(impact, 40.0)  # Máximo 40%
    
    def _estimate_co2_impact(
        self,
        fuel_impact_percent: float,
        features: VesselFeatures
    ) -> float:
        """
        Estima impacto em CO2.
        
        Args:
            fuel_impact_percent: Aumento percentual no consumo
            features: Features da embarcação
            
        Returns:
            Impacto em kg de CO2 (anual estimado)
        """
        # Consumo anual estimado (simplificado)
        # Baseado no tipo de embarcação e área do casco
        base_consumption_kg_year = features.hull_area_m2 * 50  # Estimativa
        
        # Impacto em kg de combustível
        fuel_impact_kg = base_consumption_kg_year * (fuel_impact_percent / 100.0)
        
        # Conversão para CO2
        co2_impact = fuel_impact_kg * CO2_EMISSION_FACTOR
        
        return co2_impact


class TimeSeriesFoulingModel:
    """
    Modelo de séries temporais para predição futura.
    """
    
    def __init__(self):
        self.prophet_model = None
        if not PROPHET_AVAILABLE:
            import warnings
            warnings.warn("Prophet não está disponível. Funcionalidade de séries temporais limitada.")
    
    def train(self, historical_data: pd.DataFrame):
        """
        Treina modelo Prophet com dados históricos.
        
        Args:
            historical_data: DataFrame com colunas 'ds' (data) e 'y' (espessura)
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet não está instalado. Instale com: pip install prophet")
        
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )
        self.prophet_model.fit(historical_data)
    
    def predict_future(
        self,
        periods: int = 30,
        freq: str = 'D'
    ) -> pd.DataFrame:
        """
        Prediz valores futuros.
        
        Args:
            periods: Número de períodos a predizer
            freq: Frequência ('D' para dias)
            
        Returns:
            DataFrame com predições
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet não está instalado. Instale com: pip install prophet")
        
        if self.prophet_model is None:
            raise ValueError("Modelo não treinado. Chame train() primeiro.")
        
        future = self.prophet_model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.prophet_model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


# Função de conveniência
def predict_fouling(
    vessel_features: VesselFeatures,
    historical_data: Optional[pd.DataFrame] = None
) -> FoulingPrediction:
    """
    Função principal para predição de bioincrustação.
    
    Args:
        vessel_features: Features da embarcação
        historical_data: Dados históricos (opcional)
        
    Returns:
        Predição de bioincrustação
    """
    model = HybridFoulingModel()
    return model.predict(vessel_features, historical_data)


if __name__ == "__main__":
    # Exemplo de uso
    features = VesselFeatures(
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
    
    prediction = predict_fouling(features)
    
    print("Predição de Bioincrustação:")
    print(f"Espessura: {prediction.estimated_thickness_mm:.2f} mm")
    print(f"Rugosidade: {prediction.estimated_roughness_um:.2f} μm")
    print(f"Severidade: {prediction.fouling_severity}")
    print(f"Confiança: {prediction.confidence_score:.2%}")
    print(f"Impacto no combustível: {prediction.predicted_fuel_impact_percent:.2f}%")
    print(f"Impacto em CO2: {prediction.predicted_co2_impact_kg:.2f} kg")

