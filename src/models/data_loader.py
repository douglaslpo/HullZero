"""
Carregador de Dados para Modelos de IA - HullZero

Este módulo fornece funções para carregar dados reais do banco de dados
e prepará-los para uso nos modelos de IA.
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database.repositories import (
    VesselRepository,
    FoulingDataRepository,
    OperationalDataRepository,
    MaintenanceEventRepository
)
from ..database.models import Vessel, OperationalData, MaintenanceEvent


def get_vessel_features_from_db(
    db: Session,
    vessel_id: str,
    timestamp: Optional[datetime] = None
) -> Optional[Dict]:
    """
    Carrega features de uma embarcação do banco de dados para uso em modelos de IA.
    
    Args:
        db: Sessão do banco de dados
        vessel_id: ID da embarcação
        timestamp: Timestamp para buscar dados operacionais (padrão: mais recente)
        
    Returns:
        Dicionário com features da embarcação ou None
    """
    # Buscar embarcação
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        return None
    
    # Buscar dados operacionais mais recentes
    if timestamp:
        # Buscar dados operacionais próximos ao timestamp
        operational = OperationalDataRepository.get_by_vessel(
            db, vessel_id,
            start_date=timestamp - timedelta(hours=24),
            end_date=timestamp + timedelta(hours=24),
            limit=1
        )
    else:
        # Buscar dados operacionais mais recentes
        operational = OperationalDataRepository.get_latest(db, vessel_id)
        if operational:
            operational = [operational]
    
    # Buscar última manutenção/limpeza
    latest_cleaning = MaintenanceEventRepository.get_by_vessel(
        db, vessel_id,
        event_type="cleaning",
        limit=1
    )
    
    # Calcular dias desde última limpeza
    time_since_cleaning_days = 0
    if latest_cleaning and len(latest_cleaning) > 0 and latest_cleaning[0].start_date:
        time_since_cleaning_days = (datetime.utcnow() - latest_cleaning[0].start_date).days
    
    # Extrair dados operacionais
    water_temperature = None
    salinity = None
    time_in_port_hours = 0.0
    average_speed_knots = 0.0
    
    if operational and len(operational) > 0:
        op_data = operational[0]
        water_temperature = op_data.water_temperature_c
        salinity = op_data.salinity_psu
        average_speed_knots = op_data.speed_knots or 0.0
        
        # Se velocidade é zero ou muito baixa, considerar em porto
        if average_speed_knots < 1.0:
            time_in_port_hours = 24.0  # Estimativa
    
    # Valores padrão se não encontrados
    if water_temperature is None:
        water_temperature = 25.0  # Temperatura típica do Atlântico Sul
    if salinity is None:
        salinity = 35.0  # Salinidade típica do oceano
    
    # Calcular idade da tinta
    paint_age_days = 0
    if vessel.paint_application_date:
        paint_age_days = (datetime.utcnow() - vessel.paint_application_date).days
    elif vessel.paint_age_days:
        paint_age_days = vessel.paint_age_days
    
    # Construir features básicas
    features = {
        "vessel_id": vessel_id,
        "time_since_cleaning_days": time_since_cleaning_days,
        "water_temperature_c": water_temperature,
        "salinity_psu": salinity,
        "time_in_port_hours": time_in_port_hours,
        "average_speed_knots": average_speed_knots,
        "route_region": vessel.operating_routes[0] if vessel.operating_routes and len(vessel.operating_routes) > 0 else "South_Atlantic",
        "paint_type": vessel.paint_type or "Antifouling_Type_B",
        "vessel_type": vessel.vessel_type or "tanker",
        "hull_area_m2": vessel.hull_area_m2 or 10000.0,
        # Features adicionais para modelo avançado
        "paint_age_days": paint_age_days,
        "vessel_class": vessel.vessel_class or "Unknown",
        "construction_year": vessel.construction_year or 2015,
        # Features opcionais (podem ser None)
        "last_cleaning_method": None,
        "port_water_quality_index": None,
        "seasonal_factor": None,  # Será calculado abaixo
        "chlorophyll_a_concentration": None,
        "dissolved_oxygen": None,
        "ph_level": None,
        "turbidity": None,
        "current_velocity": None,
        "depth_m": None,
    }
    
    # Adicionar dados operacionais adicionais se disponíveis
    if operational and len(operational) > 0:
        op_data = operational[0]
        features.update({
            "port_water_quality_index": op_data.port_water_quality_index,
            "chlorophyll_a_concentration": op_data.chlorophyll_a_concentration,
            "dissolved_oxygen": op_data.dissolved_oxygen,
            "ph_level": op_data.ph_level,
            "turbidity": op_data.turbidity,
            "current_velocity": op_data.current_velocity,
            "depth_m": op_data.depth_m,
        })
    
    # Calcular fator sazonal baseado na data atual
    month = datetime.utcnow().month
    if month in [12, 1, 2]:
        features["seasonal_factor"] = "summer"  # Verão no hemisfério sul
    elif month in [3, 4, 5]:
        features["seasonal_factor"] = "autumn"
    elif month in [6, 7, 8]:
        features["seasonal_factor"] = "winter"
    else:
        features["seasonal_factor"] = "spring"
    
    return features


def get_operational_history(
    db: Session,
    vessel_id: str,
    days: int = 90
) -> List[Dict]:
    """
    Carrega histórico operacional de uma embarcação.
    
    Args:
        db: Sessão do banco de dados
        vessel_id: ID da embarcação
        days: Número de dias de histórico
        
    Returns:
        Lista de dicionários com dados operacionais
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    operational_data = OperationalDataRepository.get_by_vessel(
        db, vessel_id,
        start_date=start_date,
        limit=10000
    )
    
    return [
        {
            "timestamp": op.timestamp,
            "latitude": op.latitude,
            "longitude": op.longitude,
            "speed_knots": op.speed_knots,
            "heading": op.heading,
            "fuel_consumption_kg_h": op.fuel_consumption_kg_h,
            "engine_power_kw": op.engine_power_kw,
            "water_temperature_c": op.water_temperature_c,
            "salinity_psu": op.salinity_psu,
        }
        for op in operational_data
    ]


def calculate_average_operational_metrics(
    db: Session,
    vessel_id: str,
    days: int = 30
) -> Dict:
    """
    Calcula métricas operacionais médias de uma embarcação.
    
    Args:
        db: Sessão do banco de dados
        vessel_id: ID da embarcação
        days: Número de dias para calcular média
        
    Returns:
        Dicionário com métricas médias
    """
    history = get_operational_history(db, vessel_id, days)
    
    if not history:
        return {
            "average_speed_knots": 0.0,
            "average_fuel_consumption_kg_h": 0.0,
            "average_engine_power_kw": 0.0,
            "average_water_temperature_c": 25.0,
            "average_salinity_psu": 35.0,
            "total_distance_nm": 0.0,
        }
    
    # Calcular médias
    speeds = [h["speed_knots"] for h in history if h["speed_knots"]]
    fuels = [h["fuel_consumption_kg_h"] for h in history if h["fuel_consumption_kg_h"]]
    powers = [h["engine_power_kw"] for h in history if h["engine_power_kw"]]
    temps = [h["water_temperature_c"] for h in history if h["water_temperature_c"]]
    salinities = [h["salinity_psu"] for h in history if h["salinity_psu"]]
    
    # Calcular distância total (aproximada)
    total_distance = 0.0
    for i in range(len(history) - 1):
        if history[i]["speed_knots"] and history[i+1]["timestamp"]:
            hours = (history[i+1]["timestamp"] - history[i]["timestamp"]).total_seconds() / 3600
            if hours > 0 and hours < 24:  # Evitar outliers
                total_distance += history[i]["speed_knots"] * hours
    
    return {
        "average_speed_knots": sum(speeds) / len(speeds) if speeds else 0.0,
        "average_fuel_consumption_kg_h": sum(fuels) / len(fuels) if fuels else 0.0,
        "average_engine_power_kw": sum(powers) / len(powers) if powers else 0.0,
        "average_water_temperature_c": sum(temps) / len(temps) if temps else 25.0,
        "average_salinity_psu": sum(salinities) / len(salinities) if salinities else 35.0,
        "total_distance_nm": total_distance,
        "data_points": len(history),
    }


def get_fouling_history(
    db: Session,
    vessel_id: str,
    days: int = 90
) -> List[Dict]:
    """
    Carrega histórico de bioincrustação de uma embarcação.
    
    Args:
        db: Sessão do banco de dados
        vessel_id: ID da embarcação
        days: Número de dias de histórico
        
    Returns:
        Lista de dicionários com dados de bioincrustação
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    fouling_data = FoulingDataRepository.get_by_vessel(
        db, vessel_id,
        start_date=start_date,
        limit=10000
    )
    
    return [
        {
            "timestamp": fd.timestamp,
            "estimated_thickness_mm": fd.estimated_thickness_mm,
            "estimated_roughness_um": fd.estimated_roughness_um,
            "fouling_severity": fd.fouling_severity,
            "confidence_score": fd.confidence_score,
            "predicted_fuel_impact_percent": fd.predicted_fuel_impact_percent,
        }
        for fd in fouling_data
    ]

