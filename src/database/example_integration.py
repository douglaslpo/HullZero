"""
Exemplo de Integração do Banco de Dados na API - HullZero

Este arquivo mostra como migrar endpoints da API para usar o banco de dados.
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .database import get_db
from .repositories import (
    VesselRepository,
    FoulingDataRepository,
    OperationalDataRepository,
    MaintenanceEventRepository
)
from .models import Vessel, FoulingData, OperationalData, MaintenanceEvent


# ========== EXEMPLO 1: Listar Embarcações ==========

def get_vessels_example(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Exemplo: Listar todas as embarcações usando o banco de dados.
    """
    vessels = VesselRepository.get_all(db, skip=skip, limit=limit)
    return [{
        "id": v.id,
        "name": v.name,
        "vessel_type": v.vessel_type,
        "vessel_class": v.vessel_class,
        "status": v.status,
        "hull_area_m2": v.hull_area_m2
    } for v in vessels]


# ========== EXEMPLO 2: Obter Embarcação por ID ==========

def get_vessel_example(vessel_id: str, db: Session = Depends(get_db)):
    """
    Exemplo: Obter uma embarcação específica.
    """
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    return {
        "id": vessel.id,
        "name": vessel.name,
        "imo_number": vessel.imo_number,
        "vessel_type": vessel.vessel_type,
        "vessel_class": vessel.vessel_class,
        "hull_area_m2": vessel.hull_area_m2,
        "status": vessel.status,
        # ... outros campos
    }


# ========== EXEMPLO 3: Criar Dados de Bioincrustação ==========

def create_fouling_data_example(
    vessel_id: str,
    thickness_mm: float,
    roughness_um: float,
    severity: str,
    db: Session = Depends(get_db)
):
    """
    Exemplo: Criar registro de bioincrustação.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    # Criar registro
    fouling_data = FoulingDataRepository.create(db, {
        "vessel_id": vessel_id,
        "timestamp": datetime.utcnow(),
        "estimated_thickness_mm": thickness_mm,
        "estimated_roughness_um": roughness_um,
        "fouling_severity": severity,
        "confidence_score": 0.85,
        "model_type": "hybrid"
    })
    
    return {
        "id": fouling_data.id,
        "vessel_id": fouling_data.vessel_id,
        "timestamp": fouling_data.timestamp.isoformat(),
        "estimated_thickness_mm": fouling_data.estimated_thickness_mm,
        "estimated_roughness_um": fouling_data.estimated_roughness_um,
        "fouling_severity": fouling_data.fouling_severity
    }


# ========== EXEMPLO 4: Obter Histórico de Bioincrustação ==========

def get_fouling_history_example(
    vessel_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Exemplo: Obter histórico de bioincrustação dos últimos N dias.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    fouling_data = FoulingDataRepository.get_by_vessel(
        db, vessel_id, start_date=start_date
    )
    
    return [{
        "timestamp": fd.timestamp.isoformat(),
        "estimated_thickness_mm": fd.estimated_thickness_mm,
        "estimated_roughness_um": fd.estimated_roughness_um,
        "fouling_severity": fd.fouling_severity,
        "confidence_score": fd.confidence_score
    } for fd in fouling_data]


# ========== EXEMPLO 5: Criar Evento de Manutenção ==========

def create_maintenance_event_example(
    vessel_id: str,
    event_type: str,
    start_date: datetime,
    cleaning_method: str,
    db: Session = Depends(get_db)
):
    """
    Exemplo: Criar evento de manutenção/limpeza.
    """
    # Verificar se embarcação existe
    vessel = VesselRepository.get_by_id(db, vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Embarcação não encontrada")
    
    # Criar evento
    event = MaintenanceEventRepository.create(db, {
        "vessel_id": vessel_id,
        "event_type": event_type,
        "maintenance_type": "preventive",
        "start_date": start_date,
        "cleaning_method": cleaning_method,
        "status": "completed"
    })
    
    return {
        "id": event.id,
        "vessel_id": event.vessel_id,
        "event_type": event.event_type,
        "start_date": event.start_date.isoformat(),
        "cleaning_method": event.cleaning_method,
        "status": event.status
    }


# ========== EXEMPLO 6: Query Complexa ==========

def get_vessels_with_recent_fouling_example(
    severity: str = "severe",
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Exemplo: Obter embarcações com bioincrustação severa recente.
    """
    from sqlalchemy import and_
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query com join
    results = db.query(Vessel, FoulingData).join(
        FoulingData, Vessel.id == FoulingData.vessel_id
    ).filter(
        and_(
            FoulingData.fouling_severity == severity,
            FoulingData.timestamp >= cutoff_date
        )
    ).all()
    
    return [{
        "vessel_id": vessel.id,
        "vessel_name": vessel.name,
        "fouling_thickness_mm": fouling.estimated_thickness_mm,
        "fouling_severity": fouling.fouling_severity,
        "timestamp": fouling.timestamp.isoformat()
    } for vessel, fouling in results]


# ========== EXEMPLO 7: Estatísticas Agregadas ==========

def get_fleet_statistics_example(db: Session = Depends(get_db)):
    """
    Exemplo: Estatísticas agregadas da frota.
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
    
    return {
        "total_vessels": total_vessels,
        "active_vessels": active_vessels,
        "total_hull_area_m2": float(total_hull_area),
        "total_dwt": float(total_dwt),
        "by_class": {cls: count for cls, count in by_class}
    }

