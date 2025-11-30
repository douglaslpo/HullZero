"""
Módulo de Dados - HullZero

Contém dados reais e representativos da frota Transpetro.
"""

from .transpetro_fleet_data import (
    get_transpetro_fleet,
    get_vessel_by_id,
    get_vessels_by_type,
    generate_realistic_fouling_data,
    TRANSPETRO_FLEET_DATA
)

__all__ = [
    "get_transpetro_fleet",
    "get_vessel_by_id",
    "get_vessels_by_type",
    "generate_realistic_fouling_data",
    "TRANSPETRO_FLEET_DATA"
]

