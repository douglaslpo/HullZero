"""
Módulo de Banco de Dados - HullZero

Sistema de persistência de dados usando SQLAlchemy com suporte para:
- SQLite (desenvolvimento)
- PostgreSQL/TimescaleDB (produção)
"""

from .database import get_db, init_db, engine, SessionLocal
from .models import (
    Base,
    Vessel,
    FoulingData,
    OperationalData,
    MaintenanceEvent,
    NORMAM401Risk,
    Anomaly,
    CorrectiveAction,
    PredictionExplanation,
    CleaningMethod
)

# Importar modelos normalizados (opcional - para uso futuro)
try:
    from .models_normalized import (
        VesselType,
        VesselClass,
        PaintType,
        Port,
        Route,
        Contractor,
        CargoType,
        FuelType,
        InvasiveSpecies as InvasiveSpeciesModel,
        VesselRoute,
        VesselCargoType,
        VesselFuelAlternative,
        PaintApplication,
        SensorCalibration,
        Inspection,
        ComplianceCheck,
        ComplianceViolation,
        ComplianceWarning,
        ComplianceRecommendation,
        RiskFactor,
        RiskRecommendation,
        InvasiveSpeciesRisk,
        InvasiveSpeciesRecommendation
    )
    NORMALIZED_MODELS_AVAILABLE = True
except ImportError:
    NORMALIZED_MODELS_AVAILABLE = False

__all__ = [
    "get_db",
    "init_db",
    "engine",
    "SessionLocal",
    "Base",
    "Vessel",
    "FoulingData",
    "OperationalData",
    "MaintenanceEvent",
    "NORMAM401Risk",
    "Anomaly",
    "CorrectiveAction",
    "PredictionExplanation",
    "CleaningMethod",
    "NORMALIZED_MODELS_AVAILABLE",
]

# Adicionar modelos normalizados ao __all__ se disponíveis
if NORMALIZED_MODELS_AVAILABLE:
    __all__.extend([
        "VesselType",
        "VesselClass",
        "PaintType",
        "Port",
        "Route",
        "Contractor",
        "CargoType",
        "FuelType",
        "InvasiveSpeciesModel",
        "VesselRoute",
        "VesselCargoType",
        "VesselFuelAlternative",
        "PaintApplication",
        "SensorCalibration",
        "Inspection",
        "ComplianceCheck",
        "ComplianceViolation",
        "ComplianceWarning",
        "ComplianceRecommendation",
        "RiskFactor",
        "RiskRecommendation",
        "InvasiveSpeciesRisk",
        "InvasiveSpeciesRecommendation",
    ])

