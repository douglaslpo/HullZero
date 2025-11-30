"""
Endpoints de Conformidade Normalizados - HullZero

Endpoints que usam os novos repositórios normalizados para conformidade.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from ..database import get_db
from ..database.repositories_normalized import (
    ComplianceCheckRepository,
    ComplianceViolationRepository,
    ComplianceWarningRepository,
    ComplianceRecommendationRepository,
    InspectionRepository
)

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


# ========== SCHEMAS ==========

class ComplianceCheckDetailResponse(BaseModel):
    id: str
    vessel_id: str
    check_date: str
    status: str
    fouling_thickness_mm: float
    roughness_um: float
    max_allowed_thickness_mm: float
    max_allowed_roughness_um: float
    compliance_score: float
    next_inspection_due: Optional[str]
    violations: List[dict]
    warnings: List[dict]
    recommendations: List[dict]
    
    class Config:
        from_attributes = True


class InspectionResponse(BaseModel):
    id: str
    vessel_id: str
    inspection_type: str
    inspection_date: str
    next_inspection_due: Optional[str]
    fouling_thickness_mm: Optional[float]
    roughness_um: Optional[float]
    compliance_status: Optional[str]
    compliance_score: Optional[float]
    inspector_name: Optional[str]
    port_name: Optional[str]
    
    class Config:
        from_attributes = True


# ========== ENDPOINTS ==========

@router.get("/vessels/{vessel_id}/checks", response_model=List[ComplianceCheckDetailResponse])
async def get_compliance_checks(
    vessel_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtém histórico de verificações de conformidade de uma embarcação.
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        checks = ComplianceCheckRepository.get_by_vessel(
            db, vessel_id, start_date=start, end_date=end, limit=limit
        )
        
        result = []
        for check in checks:
            # Buscar violações, avisos e recomendações
            violations = ComplianceViolationRepository.get_by_check(db, check.id)
            warnings = ComplianceWarningRepository.get_by_check(db, check.id)
            recommendations = ComplianceRecommendationRepository.get_by_check(db, check.id)
            
            result.append(ComplianceCheckDetailResponse(
                id=check.id,
                vessel_id=check.vessel_id,
                check_date=check.check_date.isoformat(),
                status=check.status,
                fouling_thickness_mm=check.fouling_thickness_mm,
                roughness_um=check.roughness_um,
                max_allowed_thickness_mm=check.max_allowed_thickness_mm,
                max_allowed_roughness_um=check.max_allowed_roughness_um,
                compliance_score=check.compliance_score,
                next_inspection_due=check.next_inspection_due.isoformat() if check.next_inspection_due else None,
                violations=[
                    {
                        "type": v.violation_type,
                        "description": v.violation_description,
                        "severity": v.severity
                    }
                    for v in violations
                ],
                warnings=[
                    {
                        "type": w.warning_type,
                        "description": w.warning_description
                    }
                    for w in warnings
                ],
                recommendations=[
                    {
                        "text": r.recommendation_text,
                        "priority": r.priority
                    }
                    for r in recommendations
                ]
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vessels/{vessel_id}/checks/latest", response_model=ComplianceCheckDetailResponse)
async def get_latest_compliance_check(
    vessel_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém a última verificação de conformidade de uma embarcação.
    """
    try:
        check = ComplianceCheckRepository.get_latest(db, vessel_id)
        
        if not check:
            raise HTTPException(status_code=404, detail="Nenhuma verificação de conformidade encontrada")
        
        # Buscar violações, avisos e recomendações
        violations = ComplianceViolationRepository.get_by_check(db, check.id)
        warnings = ComplianceWarningRepository.get_by_check(db, check.id)
        recommendations = ComplianceRecommendationRepository.get_by_check(db, check.id)
        
        return ComplianceCheckDetailResponse(
            id=check.id,
            vessel_id=check.vessel_id,
            check_date=check.check_date.isoformat(),
            status=check.status,
            fouling_thickness_mm=check.fouling_thickness_mm,
            roughness_um=check.roughness_um,
            max_allowed_thickness_mm=check.max_allowed_thickness_mm,
            max_allowed_roughness_um=check.max_allowed_roughness_um,
            compliance_score=check.compliance_score,
            next_inspection_due=check.next_inspection_due.isoformat() if check.next_inspection_due else None,
            violations=[
                {
                    "type": v.violation_type,
                    "description": v.violation_description,
                    "severity": v.severity
                }
                for v in violations
            ],
            warnings=[
                {
                    "type": w.warning_type,
                    "description": w.warning_description
                }
                for w in warnings
            ],
            recommendations=[
                {
                    "text": r.recommendation_text,
                    "priority": r.priority
                }
                for r in recommendations
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vessels/{vessel_id}/inspections", response_model=List[InspectionResponse])
async def get_inspections(
    vessel_id: str,
    inspection_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtém histórico de inspeções de uma embarcação.
    """
    try:
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None
        
        inspections = InspectionRepository.get_by_vessel(
            db, vessel_id, start_date=start, end_date=end, limit=limit
        )
        
        if inspection_type:
            inspections = [i for i in inspections if i.inspection_type == inspection_type]
        
        return [
            InspectionResponse(
                id=inspection.id,
                vessel_id=inspection.vessel_id,
                inspection_type=inspection.inspection_type,
                inspection_date=inspection.inspection_date.isoformat(),
                next_inspection_due=inspection.next_inspection_due.isoformat() if inspection.next_inspection_due else None,
                fouling_thickness_mm=inspection.fouling_thickness_mm,
                roughness_um=inspection.roughness_um,
                compliance_status=inspection.compliance_status,
                compliance_score=inspection.compliance_score,
                inspector_name=inspection.inspector_name,
                port_name=inspection.inspection_port_id  # TODO: Buscar nome do porto
            )
            for inspection in inspections
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/summary")
async def get_compliance_summary(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtém resumo de conformidade da frota.
    """
    try:
        if status:
            checks = ComplianceCheckRepository.get_by_status(db, status)
        else:
            # Buscar todas as verificações recentes (últimos 30 dias)
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=30)
            # Como não temos método get_all, vamos buscar por vessel_id conhecidos
            # Por enquanto, retornar estatísticas básicas
            checks = []
        
        # Agrupar por status
        status_counts = {}
        total_score = 0.0
        count = 0
        
        for check in checks:
            status_counts[check.status] = status_counts.get(check.status, 0) + 1
            total_score += check.compliance_score
            count += 1
        
        avg_score = total_score / count if count > 0 else 0.0
        
        return {
            "total_checks": count,
            "status_distribution": status_counts,
            "average_compliance_score": round(avg_score, 2),
            "compliant_count": status_counts.get("compliant", 0),
            "at_risk_count": status_counts.get("at_risk", 0),
            "non_compliant_count": status_counts.get("non_compliant", 0),
            "critical_count": status_counts.get("critical", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

