"""
Endpoints da API usando Banco de Dados - HullZero

Exemplos de endpoints migrados para usar o banco de dados.
Estes endpoints podem substituir os endpoints atuais em main.py.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..database.repositories import (
    VesselRepository,
    FoulingDataRepository,
    OperationalDataRepository,
    MaintenanceEventRepository
)
from ..database.models import Vessel, FoulingData
from ..models.data_loader import (
    get_vessel_features_from_db,
    get_operational_history,
    calculate_average_operational_metrics
)
from ..models.fouling_prediction import (
    predict_fouling,
    VesselFeatures,
    HybridFoulingModel
)
from ..models.advanced_fouling_prediction import (
    predict_advanced_fouling,
    AdvancedVesselFeatures,
    AdvancedHybridModel
)
from ..models.fuel_impact import (
    calculate_fuel_impact,
    ConsumptionFeatures
)


# Router para endpoints com banco de dados
router = APIRouter(prefix="/api/db", tags=["Database"])


# ========== SCHEMAS ==========

class VesselResponse(BaseModel):
    id: str
    name: str
    imo_number: Optional[str]
    vessel_type: Optional[str]
    vessel_class: Optional[str]
    fleet_category: Optional[str]
    hull_area_m2: Optional[float]
    status: str
    
    class Config:
        from_attributes = True


class FoulingDataCreate(BaseModel):
    estimated_thickness_mm: float
    estimated_roughness_um: float
    fouling_severity: str
    confidence_score: float = 0.85
    predicted_fuel_impact_percent: Optional[float] = None
    predicted_co2_impact_kg: Optional[float] = None
    model_type: str = "hybrid"
    features: Optional[dict] = None


class FoulingDataResponse(BaseModel):
    id: str
    vessel_id: str
    timestamp: datetime
    estimated_thickness_mm: float
    estimated_roughness_um: float
    fouling_severity: str
    confidence_score: float
    
    class Config:
        from_attributes = True


# ========== ENDPOINTS DE EMBARCAÇÕES ==========

@router.get("/vessels", response_model=List[VesselResponse])
async def get_vessels_db(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vessel_type: Optional[str] = None,
    vessel_class: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas as embarcações usando o banco de dados.
    """
    if vessel_type:
        vessels = VesselRepository.get_by_type(db, vessel_type)
    elif vessel_class:
        vessels = VesselRepository.get_by_class(db, vessel_class)
    elif status:
        vessels = VesselRepository.get_by_status(db, status)
    else:
        vessels = VesselRepository.get_all(db, skip=skip, limit=limit)
    
    return vessels


@router.get("/vessels/{vessel_id}", response_model=VesselResponse)
async def get_vessel_db(
    vessel_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém uma embarcação específica por ID.
    """
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    return vessel


@router.get("/vessels/imo/{imo_number}", response_model=VesselResponse)
async def get_vessel_by_imo_db(
    imo_number: str,
    db: Session = Depends(get_db)
):
    """
    Obtém uma embarcação por número IMO.
    """
    vessel = VesselRepository.get_by_imo(db, imo_number)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    return vessel


# ========== ENDPOINTS DE BIOINCRUSTAÇÃO ==========

@router.get("/vessels/{vessel_id}/fouling", response_model=List[FoulingDataResponse])
async def get_fouling_history_db(
    vessel_id: str,
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtém histórico de bioincrustação de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    fouling_data = FoulingDataRepository.get_by_vessel(
        db, vessel_id, start_date=start_date
    )
    
    return fouling_data


@router.get("/vessels/{vessel_id}/fouling/latest", response_model=FoulingDataResponse)
async def get_latest_fouling_db(
    vessel_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém a última predição de bioincrustação.
    Se não houver predição, gera uma nova baseada em dados reais.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    # Buscar última predição
    latest = FoulingDataRepository.get_latest(db, vessel_id)
    
    # Se não houver predição, gerar uma nova baseada em dados reais
    if not latest:
        # Carregar features reais do banco
        features_dict = get_vessel_features_from_db(db, vessel_id)
        
        if not features_dict:
            raise HTTPException(
                status_code=404,
                detail="Não foi possível carregar features da embarcação"
            )
        
        # Converter para VesselFeatures
        features = VesselFeatures(**features_dict)
        
        # Gerar predição
        prediction = predict_fouling(features)
        
        # Salvar predição no banco
        fouling_data = {
            "vessel_id": vessel_id,
            "timestamp": prediction.timestamp,
            "estimated_thickness_mm": prediction.estimated_thickness_mm,
            "estimated_roughness_um": prediction.estimated_roughness_um,
            "fouling_severity": prediction.fouling_severity,
            "confidence_score": prediction.confidence_score,
            "predicted_fuel_impact_percent": prediction.predicted_fuel_impact_percent,
            "predicted_co2_impact_kg": prediction.predicted_co2_impact_kg,
            "model_type": "hybrid",
            "features": features_dict,
        }
        
        latest = FoulingDataRepository.create(db, fouling_data)
    
    return latest


@router.post("/vessels/{vessel_id}/fouling/predict", response_model=FoulingDataResponse)
async def predict_fouling_db(
    vessel_id: str,
    use_advanced: bool = Query(False, description="Usar modelo avançado"),
    db: Session = Depends(get_db)
):
    """
    Gera nova predição de bioincrustação baseada em dados reais do banco.
    O endpoint carrega automaticamente todas as features necessárias do banco de dados.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    # Carregar features reais do banco
    features_dict = get_vessel_features_from_db(db, vessel_id)
    
    if not features_dict:
        raise HTTPException(
            status_code=404,
            detail="Não foi possível carregar features da embarcação"
        )
    
    try:
        if use_advanced:
            # Usar modelo avançado
            # Adicionar features adicionais se disponíveis
            operational_history = get_operational_history(db, vessel_id, days=30)
            if operational_history and len(operational_history) > 0:
                latest_op = operational_history[0]
                features_dict.update({
                    "port_water_quality_index": latest_op.get("port_water_quality_index"),
                    "chlorophyll_a_concentration": latest_op.get("chlorophyll_a_concentration"),
                    "dissolved_oxygen": latest_op.get("dissolved_oxygen"),
                    "ph_level": latest_op.get("ph_level"),
                    "turbidity": latest_op.get("turbidity"),
                    "current_velocity": latest_op.get("current_velocity"),
                    "depth_m": latest_op.get("depth_m"),
                })
            
            # Garantir que features opcionais existam
            advanced_features_dict = {
                **features_dict,
                "last_cleaning_method": features_dict.get("last_cleaning_method"),
                "paint_age_days": features_dict.get("paint_age_days", 0),
                "port_water_quality_index": features_dict.get("port_water_quality_index"),
                "seasonal_factor": features_dict.get("seasonal_factor", "summer"),
                "chlorophyll_a_concentration": features_dict.get("chlorophyll_a_concentration"),
                "dissolved_oxygen": features_dict.get("dissolved_oxygen"),
                "ph_level": features_dict.get("ph_level"),
                "turbidity": features_dict.get("turbidity"),
                "current_velocity": features_dict.get("current_velocity"),
                "depth_m": features_dict.get("depth_m"),
            }
            
            # Remover chaves que não pertencem ao AdvancedVesselFeatures
            if "vessel_class" in advanced_features_dict:
                del advanced_features_dict["vessel_class"]
            
            advanced_features = AdvancedVesselFeatures(**advanced_features_dict)
            prediction = predict_advanced_fouling(advanced_features)
            
            fouling_data = {
                "vessel_id": vessel_id,
                "timestamp": prediction.timestamp,
                "estimated_thickness_mm": prediction.estimated_thickness_mm,
                "estimated_roughness_um": prediction.estimated_roughness_um,
                "fouling_severity": prediction.fouling_severity,
                "confidence_score": prediction.confidence_score,
                "predicted_fuel_impact_percent": prediction.predicted_fuel_impact_percent,
                "predicted_co2_impact_kg": prediction.predicted_co2_impact_kg,
                "model_type": "advanced",
                "features": advanced_features_dict,
            }
        else:
            # Usar modelo padrão
            features = VesselFeatures(**features_dict)
            prediction = predict_fouling(features)
            
            fouling_data = {
                "vessel_id": vessel_id,
                "timestamp": prediction.timestamp,
                "estimated_thickness_mm": prediction.estimated_thickness_mm,
                "estimated_roughness_um": prediction.estimated_roughness_um,
                "fouling_severity": prediction.fouling_severity,
                "confidence_score": prediction.confidence_score,
                "predicted_fuel_impact_percent": prediction.predicted_fuel_impact_percent,
                "predicted_co2_impact_kg": prediction.predicted_co2_impact_kg,
                "model_type": "hybrid",
                "features": features_dict,
            }
        
        # Salvar predição no banco
        saved = FoulingDataRepository.create(db, fouling_data)
        
        return saved
        
    except Exception as e:
        import traceback
        error_detail = f"Erro ao gerar predição: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ Erro na predição: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar predição: {str(e)}"
        )


# ========== ENDPOINTS DE DADOS OPERACIONAIS ==========

@router.get("/vessels/{vessel_id}/operational-data/latest")
async def get_latest_operational_data_db(
    vessel_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém os últimos dados operacionais de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    latest = OperationalDataRepository.get_latest(db, vessel_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Nenhum dado operacional encontrado")
    
    return {
        "id": latest.id,
        "vessel_id": latest.vessel_id,
        "timestamp": latest.timestamp.isoformat(),
        "latitude": latest.latitude,
        "longitude": latest.longitude,
        "speed_knots": latest.speed_knots,
        "heading": latest.heading,
        "engine_power_kw": latest.engine_power_kw,
        "fuel_consumption_kg_h": latest.fuel_consumption_kg_h,
        "water_temperature_c": latest.water_temperature_c,
        "salinity_psu": latest.salinity_psu,
        "wind_speed_knots": latest.wind_speed_knots,
        "wave_height_m": latest.wave_height_m,
    }


@router.get("/vessels/{vessel_id}/operational-data")
async def get_operational_data_db(
    vessel_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtém histórico de dados operacionais de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    operational_data = OperationalDataRepository.get_by_vessel(
        db, vessel_id, start_date=start_date
    )
    
    return [
        {
            "id": op.id,
            "vessel_id": op.vessel_id,
            "timestamp": op.timestamp.isoformat(),
            "latitude": op.latitude,
            "longitude": op.longitude,
            "speed_knots": op.speed_knots,
            "heading": op.heading,
            "engine_power_kw": op.engine_power_kw,
            "fuel_consumption_kg_h": op.fuel_consumption_kg_h,
            "water_temperature_c": op.water_temperature_c,
            "salinity_psu": op.salinity_psu,
        }
        for op in operational_data
    ]


@router.get("/vessels/{vessel_id}/operational-metrics")
async def get_operational_metrics_db(
    vessel_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtém métricas operacionais médias de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    metrics = calculate_average_operational_metrics(db, vessel_id, days)
    
    return metrics


# ========== ENDPOINTS DE MANUTENÇÃO ==========

@router.get("/vessels/{vessel_id}/maintenance/latest")
async def get_latest_maintenance_db(
    vessel_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém o último evento de manutenção de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    latest = MaintenanceEventRepository.get_latest(db, vessel_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Nenhum evento de manutenção encontrado")
    
    return {
        "id": latest.id,
        "vessel_id": latest.vessel_id,
        "event_type": latest.event_type,
        "start_date": latest.start_date.isoformat() if latest.start_date else None,
        "end_date": latest.end_date.isoformat() if latest.end_date else None,
        "duration_hours": latest.duration_hours,
        "description": latest.description,
        "status": latest.status,
    }


@router.get("/vessels/{vessel_id}/maintenance")
async def get_maintenance_history_db(
    vessel_id: str,
    days: int = Query(365, ge=1, le=3650),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtém histórico de eventos de manutenção de uma embarcação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    maintenance_events = MaintenanceEventRepository.get_by_vessel(
        db, vessel_id, event_type=event_type, start_date=start_date
    )
    
    return [
        {
            "id": event.id,
            "vessel_id": event.vessel_id,
            "event_type": event.event_type,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "duration_hours": event.duration_hours,
            "description": event.description,
            "status": event.status,
        }
        for event in maintenance_events
    ]


# ========== ESTATÍSTICAS ==========

@router.get("/statistics/fleet")
async def get_fleet_statistics_db(db: Session = Depends(get_db)):
    """
    Retorna estatísticas agregadas da frota.
    """
    from sqlalchemy import func
    
    total_vessels = db.query(func.count(Vessel.id)).scalar()
    active_vessels = db.query(func.count(Vessel.id)).filter(
        Vessel.status == "active"
    ).scalar()
    
    total_hull_area = db.query(func.sum(Vessel.hull_area_m2)).scalar() or 0
    total_dwt = db.query(func.sum(Vessel.dwt)).scalar() or 0
    
    # Por classe
    by_class = db.query(
        Vessel.vessel_class,
        func.count(Vessel.id).label("count")
    ).group_by(Vessel.vessel_class).all()
    
    # Por tipo
    by_type = db.query(
        Vessel.vessel_type,
        func.count(Vessel.id).label("count")
    ).group_by(Vessel.vessel_type).all()
    
    return {
        "total_vessels": total_vessels,
        "active_vessels": active_vessels,
        "total_hull_area_m2": float(total_hull_area),
        "total_dwt": float(total_dwt),
        "by_class": {cls: count for cls, count in by_class if cls},
        "by_type": {vtype: count for vtype, count in by_type if vtype}
    }
