"""
Repositórios - Camada de Acesso aos Dados - HullZero

Implementa padrão Repository para acesso aos dados.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from .models import (
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


class VesselRepository:
    """Repositório para embarcações"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Vessel]:
        return db.query(Vessel).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, vessel_id: str) -> Optional[Vessel]:
        return db.query(Vessel).filter(Vessel.id == vessel_id).first()
    
    @staticmethod
    def get_by_imo(db: Session, imo_number: str) -> Optional[Vessel]:
        return db.query(Vessel).filter(Vessel.imo_number == imo_number).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Vessel]:
        return db.query(Vessel).filter(Vessel.name == name).first()
    
    @staticmethod
    def get_by_type(db: Session, vessel_type: str) -> List[Vessel]:
        return db.query(Vessel).filter(Vessel.vessel_type == vessel_type).all()
    
    @staticmethod
    def get_by_class(db: Session, vessel_class: str) -> List[Vessel]:
        return db.query(Vessel).filter(Vessel.vessel_class == vessel_class).all()
    
    @staticmethod
    def get_by_category(db: Session, category: str) -> List[Vessel]:
        return db.query(Vessel).filter(Vessel.fleet_category == category).all()
    
    @staticmethod
    def get_by_status(db: Session, status: str) -> List[Vessel]:
        return db.query(Vessel).filter(Vessel.status == status).all()
    
    @staticmethod
    def create(db: Session, vessel_data: Dict) -> Vessel:
        vessel = Vessel(**vessel_data)
        db.add(vessel)
        db.commit()
        db.refresh(vessel)
        return vessel
    
    @staticmethod
    def update(db: Session, vessel_id: str, vessel_data: Dict) -> Optional[Vessel]:
        vessel = VesselRepository.get_by_id(db, vessel_id)
        if vessel:
            for key, value in vessel_data.items():
                setattr(vessel, key, value)
            vessel.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(vessel)
        return vessel
    
    @staticmethod
    def delete(db: Session, vessel_id: str) -> bool:
        vessel = VesselRepository.get_by_id(db, vessel_id)
        if vessel:
            db.delete(vessel)
            db.commit()
            return True
        return False


class FoulingDataRepository:
    """Repositório para dados de bioincrustação"""
    
    @staticmethod
    def create(db: Session, fouling_data: Dict) -> FoulingData:
        data = FoulingData(**fouling_data)
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[FoulingData]:
        query = db.query(FoulingData).filter(FoulingData.vessel_id == vessel_id)
        
        if start_date:
            query = query.filter(FoulingData.timestamp >= start_date)
        if end_date:
            query = query.filter(FoulingData.timestamp <= end_date)
        
        return query.order_by(desc(FoulingData.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_latest(db: Session, vessel_id: str) -> Optional[FoulingData]:
        return (
            db.query(FoulingData)
            .filter(FoulingData.vessel_id == vessel_id)
            .order_by(desc(FoulingData.timestamp))
            .first()
        )


class OperationalDataRepository:
    """Repositório para dados operacionais"""
    
    @staticmethod
    def create(db: Session, operational_data: Dict) -> OperationalData:
        data = OperationalData(**operational_data)
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OperationalData]:
        query = db.query(OperationalData).filter(OperationalData.vessel_id == vessel_id)
        
        if start_date:
            query = query.filter(OperationalData.timestamp >= start_date)
        if end_date:
            query = query.filter(OperationalData.timestamp <= end_date)
        
        return query.order_by(desc(OperationalData.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_latest(db: Session, vessel_id: str) -> Optional[OperationalData]:
        return (
            db.query(OperationalData)
            .filter(OperationalData.vessel_id == vessel_id)
            .order_by(desc(OperationalData.timestamp))
            .first()
        )


class MaintenanceEventRepository:
    """Repositório para eventos de manutenção"""
    
    @staticmethod
    def create(db: Session, maintenance_data: Dict) -> MaintenanceEvent:
        event = MaintenanceEvent(**maintenance_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[MaintenanceEvent]:
        query = db.query(MaintenanceEvent).filter(MaintenanceEvent.vessel_id == vessel_id)
        
        if event_type:
            query = query.filter(MaintenanceEvent.event_type == event_type)
        
        if start_date:
            query = query.filter(MaintenanceEvent.start_date >= start_date)
        
        if end_date:
            query = query.filter(MaintenanceEvent.start_date <= end_date)
        
        return query.order_by(desc(MaintenanceEvent.start_date)).limit(limit).all()
    
    @staticmethod
    def get_latest(db: Session, vessel_id: str) -> Optional[MaintenanceEvent]:
        return (
            db.query(MaintenanceEvent)
            .filter(MaintenanceEvent.vessel_id == vessel_id)
            .order_by(desc(MaintenanceEvent.start_date))
            .first()
        )
    
    @staticmethod
    def get_latest_by_type(
        db: Session, 
        vessel_id: str, 
        event_type: str
    ) -> Optional[MaintenanceEvent]:
        return (
            db.query(MaintenanceEvent)
            .filter(
                and_(
                    MaintenanceEvent.vessel_id == vessel_id,
                    MaintenanceEvent.event_type == event_type
                )
            )
            .order_by(desc(MaintenanceEvent.start_date))
            .first()
        )


class NORMAM401RiskRepository:
    """Repositório para riscos NORMAM 401"""
    
    @staticmethod
    def create(db: Session, risk_data: Dict) -> NORMAM401Risk:
        risk = NORMAM401Risk(**risk_data)
        db.add(risk)
        db.commit()
        db.refresh(risk)
        return risk
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        limit: int = 10
    ) -> List[NORMAM401Risk]:
        return (
            db.query(NORMAM401Risk)
            .filter(NORMAM401Risk.vessel_id == vessel_id)
            .order_by(desc(NORMAM401Risk.created_at))
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def get_latest(db: Session, vessel_id: str) -> Optional[NORMAM401Risk]:
        return (
            db.query(NORMAM401Risk)
            .filter(NORMAM401Risk.vessel_id == vessel_id)
            .order_by(desc(NORMAM401Risk.created_at))
            .first()
        )


class AnomalyRepository:
    """Repositório para anomalias"""
    
    @staticmethod
    def create(db: Session, anomaly_data: Dict) -> Anomaly:
        anomaly = Anomaly(**anomaly_data)
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        return anomaly
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Anomaly]:
        query = db.query(Anomaly).filter(Anomaly.vessel_id == vessel_id)
        
        if status:
            query = query.filter(Anomaly.status == status)
        
        return query.order_by(desc(Anomaly.detected_at)).limit(limit).all()
    
    @staticmethod
    def get_open(db: Session, vessel_id: Optional[str] = None) -> List[Anomaly]:
        query = db.query(Anomaly).filter(Anomaly.status == "open")
        
        if vessel_id:
            query = query.filter(Anomaly.vessel_id == vessel_id)
        
        return query.order_by(desc(Anomaly.detected_at)).all()


class CorrectiveActionRepository:
    """Repositório para ações corretivas"""
    
    @staticmethod
    def create(db: Session, action_data: Dict) -> CorrectiveAction:
        action = CorrectiveAction(**action_data)
        db.add(action)
        db.commit()
        db.refresh(action)
        return action
    
    @staticmethod
    def get_by_vessel(
        db: Session,
        vessel_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        query = db.query(CorrectiveAction).filter(CorrectiveAction.vessel_id == vessel_id)
        
        if status:
            query = query.filter(CorrectiveAction.status == status)
        
        return query.order_by(desc(CorrectiveAction.created_at)).limit(limit).all()
    
    @staticmethod
    def get_pending(db: Session, vessel_id: Optional[str] = None) -> List[CorrectiveAction]:
        query = db.query(CorrectiveAction).filter(CorrectiveAction.status == "pending")
        
        if vessel_id:
            query = query.filter(CorrectiveAction.vessel_id == vessel_id)
        
        return query.order_by(CorrectiveAction.deadline).all()


class CleaningMethodRepository:
    """Repositório para métodos de limpeza"""
    
    @staticmethod
    def get_all(db: Session, status: Optional[str] = "available") -> List[CleaningMethod]:
        query = db.query(CleaningMethod)
        if status:
            query = query.filter(CleaningMethod.status == status)
        return query.all()
    
    @staticmethod
    def get_by_id(db: Session, method_id: str) -> Optional[CleaningMethod]:
        return db.query(CleaningMethod).filter(CleaningMethod.id == method_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[CleaningMethod]:
        return db.query(CleaningMethod).filter(CleaningMethod.code == code).first()
    
    @staticmethod
    def get_by_category(db: Session, category: str) -> List[CleaningMethod]:
        return (
            db.query(CleaningMethod)
            .filter(CleaningMethod.category == category)
            .filter(CleaningMethod.status == "available")
            .all()
        )

