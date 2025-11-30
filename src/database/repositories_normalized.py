"""
Repositórios Normalizados - Camada de Acesso aos Dados - HullZero

Repositórios para as novas entidades normalizadas.
"""

from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

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
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("⚠️  Modelos normalizados não disponíveis. Execute as migrações primeiro.")


if MODELS_AVAILABLE:
    # ============================================================
    # REPOSITÓRIOS DE REFERÊNCIA
    # ============================================================

    class VesselTypeRepository:
        """Repositório para tipos de embarcação"""
        
        @staticmethod
        def get_all(db: Session) -> List[VesselType]:
            return db.query(VesselType).all()
        
        @staticmethod
        def get_by_id(db: Session, type_id: str) -> Optional[VesselType]:
            return db.query(VesselType).filter(VesselType.id == type_id).first()
        
        @staticmethod
        def get_by_category(db: Session, category: str) -> List[VesselType]:
            return db.query(VesselType).filter(VesselType.category == category).all()


    class PortRepository:
        """Repositório para portos"""
        
        @staticmethod
        def get_all(db: Session) -> List[Port]:
            return db.query(Port).all()
        
        @staticmethod
        def get_by_id(db: Session, port_id: str) -> Optional[Port]:
            return db.query(Port).filter(Port.id == port_id).first()
        
        @staticmethod
        def get_by_country(db: Session, country: str) -> List[Port]:
            return db.query(Port).filter(Port.country == country).all()
        
        @staticmethod
        def get_by_code(db: Session, port_code: str) -> Optional[Port]:
            return db.query(Port).filter(Port.port_code == port_code).first()
        
        @staticmethod
        def create(db: Session, port_data: Dict) -> Port:
            port = Port(**port_data)
            db.add(port)
            db.commit()
            db.refresh(port)
            return port


    class RouteRepository:
        """Repositório para rotas"""
        
        @staticmethod
        def get_all(db: Session) -> List[Route]:
            return db.query(Route).all()
        
        @staticmethod
        def get_by_id(db: Session, route_id: str) -> Optional[Route]:
            return db.query(Route).filter(Route.id == route_id).first()
        
        @staticmethod
        def get_by_region(db: Session, region: str) -> List[Route]:
            return db.query(Route).filter(Route.region == region).all()
        
        @staticmethod
        def get_by_ports(
            db: Session, 
            origin_port_id: Optional[str] = None,
            destination_port_id: Optional[str] = None
        ) -> List[Route]:
            query = db.query(Route)
            if origin_port_id:
                query = query.filter(Route.origin_port_id == origin_port_id)
            if destination_port_id:
                query = query.filter(Route.destination_port_id == destination_port_id)
            return query.all()


    class ContractorRepository:
        """Repositório para contratantes"""
        
        @staticmethod
        def get_all(db: Session, status: Optional[str] = "active") -> List[Contractor]:
            query = db.query(Contractor)
            if status:
                query = query.filter(Contractor.status == status)
            return query.all()
        
        @staticmethod
        def get_by_id(db: Session, contractor_id: str) -> Optional[Contractor]:
            return db.query(Contractor).filter(Contractor.id == contractor_id).first()
        
        @staticmethod
        def get_by_specialization(db: Session, specialization: str) -> List[Contractor]:
            return db.query(Contractor).filter(Contractor.specialization == specialization).all()


    class InvasiveSpeciesRepository:
        """Repositório para espécies invasoras"""
        
        @staticmethod
        def get_all(db: Session) -> List[InvasiveSpeciesModel]:
            return db.query(InvasiveSpeciesModel).all()
        
        @staticmethod
        def get_by_id(db: Session, species_id: str) -> Optional[InvasiveSpeciesModel]:
            return db.query(InvasiveSpeciesModel).filter(InvasiveSpeciesModel.id == species_id).first()
        
        @staticmethod
        def get_by_code(db: Session, code: str) -> Optional[InvasiveSpeciesModel]:
            return db.query(InvasiveSpeciesModel).filter(InvasiveSpeciesModel.code == code).first()


    # ============================================================
    # REPOSITÓRIOS DE NOVAS ENTIDADES
    # ============================================================

    class InspectionRepository:
        """Repositório para inspeções"""
        
        @staticmethod
        def create(db: Session, inspection_data: Dict) -> Inspection:
            inspection = Inspection(**inspection_data)
            db.add(inspection)
            db.commit()
            db.refresh(inspection)
            return inspection
        
        @staticmethod
        def get_by_vessel(
            db: Session,
            vessel_id: str,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            limit: int = 100
        ) -> List[Inspection]:
            query = db.query(Inspection).filter(Inspection.vessel_id == vessel_id)
            
            if start_date:
                query = query.filter(Inspection.inspection_date >= start_date)
            if end_date:
                query = query.filter(Inspection.inspection_date <= end_date)
            
            return query.order_by(desc(Inspection.inspection_date)).limit(limit).all()
        
        @staticmethod
        def get_latest(db: Session, vessel_id: str) -> Optional[Inspection]:
            return (
                db.query(Inspection)
                .filter(Inspection.vessel_id == vessel_id)
                .order_by(desc(Inspection.inspection_date))
                .first()
            )
        
        @staticmethod
        def get_by_type(
            db: Session,
            vessel_id: str,
            inspection_type: str
        ) -> List[Inspection]:
            return (
                db.query(Inspection)
                .filter(
                    and_(
                        Inspection.vessel_id == vessel_id,
                        Inspection.inspection_type == inspection_type
                    )
                )
                .order_by(desc(Inspection.inspection_date))
                .all()
            )


    class ComplianceCheckRepository:
        """Repositório para verificações de conformidade"""
        
        @staticmethod
        def create(db: Session, check_data: Dict) -> ComplianceCheck:
            check = ComplianceCheck(**check_data)
            db.add(check)
            db.commit()
            db.refresh(check)
            return check
        
        @staticmethod
        def get_by_vessel(
            db: Session,
            vessel_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            limit: int = 100
        ) -> List[ComplianceCheck]:
            query = db.query(ComplianceCheck).filter(ComplianceCheck.vessel_id == vessel_id)
            
            if start_date:
                query = query.filter(ComplianceCheck.check_date >= start_date)
            if end_date:
                query = query.filter(ComplianceCheck.check_date <= end_date)
            
            return query.order_by(desc(ComplianceCheck.check_date)).limit(limit).all()
        
        @staticmethod
        def get_latest(db: Session, vessel_id: str) -> Optional[ComplianceCheck]:
            return (
                db.query(ComplianceCheck)
                .filter(ComplianceCheck.vessel_id == vessel_id)
                .order_by(desc(ComplianceCheck.check_date))
                .first()
            )
        
        @staticmethod
        def get_by_status(
            db: Session,
            status: str,
            vessel_id: Optional[str] = None
        ) -> List[ComplianceCheck]:
            query = db.query(ComplianceCheck).filter(ComplianceCheck.status == status)
            
            if vessel_id:
                query = query.filter(ComplianceCheck.vessel_id == vessel_id)
            
            return query.order_by(desc(ComplianceCheck.check_date)).all()


    class ComplianceViolationRepository:
        """Repositório para violações de conformidade"""
        
        @staticmethod
        def create(db: Session, violation_data: Dict) -> ComplianceViolation:
            violation = ComplianceViolation(**violation_data)
            db.add(violation)
            db.commit()
            db.refresh(violation)
            return violation
        
        @staticmethod
        def get_by_check(
            db: Session,
            compliance_check_id: str
        ) -> List[ComplianceViolation]:
            return (
                db.query(ComplianceViolation)
                .filter(ComplianceViolation.compliance_check_id == compliance_check_id)
                .all()
            )


    class ComplianceWarningRepository:
        """Repositório para avisos de conformidade"""
        
        @staticmethod
        def create(db: Session, warning_data: Dict) -> ComplianceWarning:
            warning = ComplianceWarning(**warning_data)
            db.add(warning)
            db.commit()
            db.refresh(warning)
            return warning
        
        @staticmethod
        def get_by_check(
            db: Session,
            compliance_check_id: str
        ) -> List[ComplianceWarning]:
            return (
                db.query(ComplianceWarning)
                .filter(ComplianceWarning.compliance_check_id == compliance_check_id)
                .all()
            )


    class ComplianceRecommendationRepository:
        """Repositório para recomendações de conformidade"""
        
        @staticmethod
        def create(db: Session, recommendation_data: Dict) -> ComplianceRecommendation:
            recommendation = ComplianceRecommendation(**recommendation_data)
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            return recommendation
        
        @staticmethod
        def get_by_check(
            db: Session,
            compliance_check_id: str
        ) -> List[ComplianceRecommendation]:
            return (
                db.query(ComplianceRecommendation)
                .filter(ComplianceRecommendation.compliance_check_id == compliance_check_id)
                .order_by(ComplianceRecommendation.priority)
                .all()
            )


    class PaintApplicationRepository:
        """Repositório para aplicações de tinta"""
        
        @staticmethod
        def create(db: Session, application_data: Dict) -> PaintApplication:
            application = PaintApplication(**application_data)
            db.add(application)
            db.commit()
            db.refresh(application)
            return application
        
        @staticmethod
        def get_by_vessel(
            db: Session,
            vessel_id: str,
            limit: int = 10
        ) -> List[PaintApplication]:
            return (
                db.query(PaintApplication)
                .filter(PaintApplication.vessel_id == vessel_id)
                .order_by(desc(PaintApplication.application_date))
                .limit(limit)
                .all()
            )
        
        @staticmethod
        def get_latest(db: Session, vessel_id: str) -> Optional[PaintApplication]:
            return (
                db.query(PaintApplication)
                .filter(PaintApplication.vessel_id == vessel_id)
                .order_by(desc(PaintApplication.application_date))
                .first()
            )


    class SensorCalibrationRepository:
        """Repositório para calibrações de sensores"""
        
        @staticmethod
        def create(db: Session, calibration_data: Dict) -> SensorCalibration:
            calibration = SensorCalibration(**calibration_data)
            db.add(calibration)
            db.commit()
            db.refresh(calibration)
            return calibration
        
        @staticmethod
        def get_by_vessel(
            db: Session,
            vessel_id: str,
            sensor_type: Optional[str] = None,
            limit: int = 10
        ) -> List[SensorCalibration]:
            query = db.query(SensorCalibration).filter(SensorCalibration.vessel_id == vessel_id)
            
            if sensor_type:
                query = query.filter(SensorCalibration.sensor_type == sensor_type)
            
            return query.order_by(desc(SensorCalibration.calibration_date)).limit(limit).all()
        
        @staticmethod
        def get_latest(db: Session, vessel_id: str, sensor_type: Optional[str] = None) -> Optional[SensorCalibration]:
            query = db.query(SensorCalibration).filter(SensorCalibration.vessel_id == vessel_id)
            
            if sensor_type:
                query = query.filter(SensorCalibration.sensor_type == sensor_type)
            
            return query.order_by(desc(SensorCalibration.calibration_date)).first()


    class InvasiveSpeciesRiskRepository:
        """Repositório para riscos de espécies invasoras"""
        
        @staticmethod
        def create(db: Session, risk_data: Dict) -> InvasiveSpeciesRisk:
            risk = InvasiveSpeciesRisk(**risk_data)
            db.add(risk)
            db.commit()
            db.refresh(risk)
            return risk
        
        @staticmethod
        def get_by_vessel(
            db: Session,
            vessel_id: str,
            species_id: Optional[str] = None,
            limit: int = 10
        ) -> List[InvasiveSpeciesRisk]:
            query = db.query(InvasiveSpeciesRisk).filter(InvasiveSpeciesRisk.vessel_id == vessel_id)
            
            if species_id:
                query = query.filter(InvasiveSpeciesRisk.species_id == species_id)
            
            return query.order_by(desc(InvasiveSpeciesRisk.created_at)).limit(limit).all()
        
        @staticmethod
        def get_latest(
            db: Session,
            vessel_id: str,
            species_id: Optional[str] = None
        ) -> Optional[InvasiveSpeciesRisk]:
            query = db.query(InvasiveSpeciesRisk).filter(InvasiveSpeciesRisk.vessel_id == vessel_id)
            
            if species_id:
                query = query.filter(InvasiveSpeciesRisk.species_id == species_id)
            
            return query.order_by(desc(InvasiveSpeciesRisk.created_at)).first()

