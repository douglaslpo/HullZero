"""
Modelos de IA/ML para predição de bioincrustação e impacto no combustível
"""

from .fouling_prediction import predict_fouling, VesselFeatures, FoulingPrediction
from .fuel_impact import calculate_fuel_impact, ConsumptionFeatures, FuelImpactResult

__all__ = [
    'predict_fouling',
    'VesselFeatures',
    'FoulingPrediction',
    'calculate_fuel_impact',
    'ConsumptionFeatures',
    'FuelImpactResult'
]

