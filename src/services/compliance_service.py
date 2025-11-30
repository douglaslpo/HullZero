"""
Serviço de Conformidade NORMAM 401 - HullZero

Este módulo implementa verificação de conformidade com a NORMAM 401,
geração de relatórios regulatórios e alertas de não conformidade.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..models.fouling_prediction import predict_fouling, VesselFeatures


class ComplianceStatus(Enum):
    """Status de conformidade"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    NON_COMPLIANT = "non_compliant"
    CRITICAL = "critical"


@dataclass
class ComplianceCheck:
    """Resultado de verificação de conformidade"""
    vessel_id: str
    check_date: datetime
    status: ComplianceStatus
    fouling_thickness_mm: float
    roughness_um: float
    max_allowed_thickness_mm: float
    max_allowed_roughness_um: float
    violations: List[str]
    warnings: List[str]
    compliance_score: float  # 0-1
    next_inspection_due: datetime
    recommendations: List[str]


@dataclass
class ComplianceReport:
    """Relatório de conformidade"""
    report_id: str
    vessel_id: str
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime
    overall_status: ComplianceStatus
    checks: List[ComplianceCheck]
    summary: Dict
    recommendations: List[str]


class NORMAM401ComplianceService:
    """
    Serviço de conformidade com NORMAM 401.
    
    NORMAM 401 estabelece limites para bioincrustação em cascos:
    - Espessura máxima: 5mm (dependendo do tipo de embarcação)
    - Rugosidade máxima: 500 μm
    - Inspeções mínimas: Trimestrais
    """
    
    # Limites NORMAM 401/DPC (baseados em Portaria DPC/DGN/MB nº 180, de 10/06/2025)
    # Capítulo 3 - Sistemas Antiincrustantes Danosos
    
    # Limites máximos por tipo de embarcação (NORMAM 401)
    MAX_FOULING_THICKNESS_MM = 5.0  # Limite máximo geral de espessura
    MAX_ROUGHNESS_UM = 500.0  # Limite máximo de rugosidade (500 μm)
    
    # Limites específicos por tipo (baseados em práticas da indústria e NORMAM)
    VESSEL_TYPE_LIMITS = {
        "tanker": {"thickness": 5.0, "roughness": 500.0},
        "cargo": {"thickness": 5.0, "roughness": 500.0},
        "container": {"thickness": 4.5, "roughness": 450.0},  # Mais rigoroso
        "barge": {"thickness": 6.0, "roughness": 600.0},  # Menos rigoroso (operações internas)
        "tug": {"thickness": 6.0, "roughness": 600.0},  # Menos rigoroso
        "standard": {"thickness": 5.0, "roughness": 500.0}
    }
    
    # Limites de alerta (80% do máximo) - Zona de atenção
    WARNING_THICKNESS_MM = MAX_FOULING_THICKNESS_MM * 0.8  # 4.0 mm
    WARNING_ROUGHNESS_UM = MAX_ROUGHNESS_UM * 0.8  # 400 μm
    
    # Frequência de inspeção (NORMAM 401 - mínimo trimestral)
    MIN_INSPECTION_INTERVAL_DAYS = 90  # Trimestral (3 meses)
    
    # Frequência recomendada para embarcações em alto risco
    HIGH_RISK_INSPECTION_INTERVAL_DAYS = 30  # Mensal
    
    def check_compliance(
        self,
        vessel_id: str,
        fouling_thickness_mm: float,
        roughness_um: float,
        vessel_type: str = "standard",
        last_inspection_date: Optional[datetime] = None
    ) -> ComplianceCheck:
        """
        Verifica conformidade com NORMAM 401.
        
        Args:
            vessel_id: ID da embarcação
            fouling_thickness_mm: Espessura de bioincrustação (mm)
            roughness_um: Rugosidade (μm)
            vessel_type: Tipo de embarcação
            last_inspection_date: Data da última inspeção
            
        Returns:
            Resultado da verificação
        """
        check_date = datetime.now()
        
        # Ajusta limites por tipo de embarcação (NORMAM 401)
        max_thickness = self._get_max_thickness_for_vessel_type(vessel_type)
        max_roughness = self._get_max_roughness_for_vessel_type(vessel_type)
        
        # Verifica violações
        violations = []
        warnings = []
        
        # Violação crítica: excede limites
        if fouling_thickness_mm > max_thickness:
            violations.append(
                f"Espessura de bioincrustação ({fouling_thickness_mm:.2f} mm) "
                f"excede limite máximo permitido ({max_thickness:.2f} mm)"
            )
        
        if roughness_um > max_roughness:
            violations.append(
                f"Rugosidade ({roughness_um:.2f} μm) "
                f"excede limite máximo permitido ({max_roughness:.2f} μm)"
            )
        
        # Avisos: próximo dos limites
        if fouling_thickness_mm > self.WARNING_THICKNESS_MM and fouling_thickness_mm <= max_thickness:
            warnings.append(
                f"Espessura de bioincrustação ({fouling_thickness_mm:.2f} mm) "
                f"próxima do limite máximo ({max_thickness:.2f} mm)"
            )
        
        if roughness_um > self.WARNING_ROUGHNESS_UM and roughness_um <= max_roughness:
            warnings.append(
                f"Rugosidade ({roughness_um:.2f} μm) "
                f"próxima do limite máximo ({max_roughness:.2f} μm)"
            )
        
        # Verifica frequência de inspeção
        if last_inspection_date:
            days_since_inspection = (check_date - last_inspection_date).days
            if days_since_inspection > self.MIN_INSPECTION_INTERVAL_DAYS:
                violations.append(
                    f"Período desde última inspeção ({days_since_inspection} dias) "
                    f"excede intervalo mínimo requerido ({self.MIN_INSPECTION_INTERVAL_DAYS} dias)"
                )
        
        # Determina status
        if violations:
            if any("excede limite máximo" in v for v in violations):
                status = ComplianceStatus.CRITICAL
            else:
                status = ComplianceStatus.NON_COMPLIANT
        elif warnings:
            status = ComplianceStatus.AT_RISK
        else:
            status = ComplianceStatus.COMPLIANT
        
        # Calcula score de conformidade (0-1)
        compliance_score = self._calculate_compliance_score(
            fouling_thickness_mm,
            roughness_um,
            max_thickness,
            max_roughness
        )
        
        # Próxima inspeção devida
        if last_inspection_date:
            next_inspection_due = last_inspection_date + timedelta(days=self.MIN_INSPECTION_INTERVAL_DAYS)
        else:
            next_inspection_due = check_date + timedelta(days=self.MIN_INSPECTION_INTERVAL_DAYS)
        
        # Gera recomendações
        recommendations = self._generate_recommendations(
            status,
            fouling_thickness_mm,
            roughness_um,
            max_thickness,
            max_roughness,
            violations,
            warnings
        )
        
        return ComplianceCheck(
            vessel_id=vessel_id,
            check_date=check_date,
            status=status,
            fouling_thickness_mm=fouling_thickness_mm,
            roughness_um=roughness_um,
            max_allowed_thickness_mm=max_thickness,
            max_allowed_roughness_um=max_roughness,
            violations=violations,
            warnings=warnings,
            compliance_score=compliance_score,
            next_inspection_due=next_inspection_due,
            recommendations=recommendations
        )
    
    def _get_max_thickness_for_vessel_type(self, vessel_type: str) -> float:
        """
        Retorna limite máximo de espessura por tipo de embarcação.
        Baseado em NORMAM 401 e práticas da indústria.
        
        Args:
            vessel_type: Tipo de embarcação
            
        Returns:
            Limite máximo em mm
        """
        limits = self.VESSEL_TYPE_LIMITS.get(
            vessel_type.lower(),
            self.VESSEL_TYPE_LIMITS["standard"]
        )
        return limits["thickness"]
    
    def _get_max_roughness_for_vessel_type(self, vessel_type: str) -> float:
        """
        Retorna limite máximo de rugosidade por tipo de embarcação.
        
        Args:
            vessel_type: Tipo de embarcação
            
        Returns:
            Limite máximo em μm
        """
        limits = self.VESSEL_TYPE_LIMITS.get(
            vessel_type.lower(),
            self.VESSEL_TYPE_LIMITS["standard"]
        )
        return limits["roughness"]
    
    def _calculate_compliance_score(
        self,
        fouling_thickness_mm: float,
        roughness_um: float,
        max_thickness: float,
        max_roughness: float
    ) -> float:
        """
        Calcula score de conformidade (0-1, 1 = totalmente conforme).
        
        Args:
            fouling_thickness_mm: Espessura atual
            roughness_um: Rugosidade atual
            max_thickness: Limite máximo de espessura
            max_roughness: Limite máximo de rugosidade
            
        Returns:
            Score de conformidade
        """
        # Score de espessura
        thickness_score = 1.0 - min(1.0, fouling_thickness_mm / max_thickness)
        
        # Score de rugosidade
        roughness_score = 1.0 - min(1.0, roughness_um / max_roughness)
        
        # Score combinado (média ponderada)
        compliance_score = (thickness_score * 0.6 + roughness_score * 0.4)
        
        return max(0.0, min(1.0, compliance_score))
    
    def _generate_recommendations(
        self,
        status: ComplianceStatus,
        fouling_thickness_mm: float,
        roughness_um: float,
        max_thickness: float,
        max_roughness: float,
        violations: List[str],
        warnings: List[str]
    ) -> List[str]:
        """
        Gera recomendações baseadas no status de conformidade.
        
        Args:
            status: Status de conformidade
            fouling_thickness_mm: Espessura atual
            roughness_um: Rugosidade atual
            max_thickness: Limite máximo
            max_roughness: Limite máximo
            violations: Lista de violações
            warnings: Lista de avisos
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if status == ComplianceStatus.CRITICAL:
            recommendations.append(
                "AÇÃO IMEDIATA REQUERIDA: Limpeza do casco deve ser realizada "
                "imediatamente para garantir conformidade com NORMAM 401."
            )
            recommendations.append(
                "Notificar autoridades competentes sobre não conformidade."
            )
        
        elif status == ComplianceStatus.NON_COMPLIANT:
            recommendations.append(
                "Limpeza do casco recomendada dentro de 7 dias para garantir conformidade."
            )
            recommendations.append(
                "Aumentar frequência de inspeções até conformidade ser restaurada."
            )
        
        elif status == ComplianceStatus.AT_RISK:
            recommendations.append(
                "Monitoramento intensificado recomendado. Planejar limpeza preventiva."
            )
            recommendations.append(
                f"Espessura atual ({fouling_thickness_mm:.2f} mm) está próxima do limite "
                f"({max_thickness:.2f} mm). Considerar limpeza preventiva."
            )
        
        else:  # COMPLIANT
            recommendations.append(
                "Embarcação em conformidade com NORMAM 401. Manter monitoramento regular."
            )
        
        # Recomendações específicas por métrica
        if fouling_thickness_mm > max_thickness * 0.9:
            recommendations.append(
                "Espessura de bioincrustação muito próxima do limite. "
                "Ação preventiva recomendada."
            )
        
        if roughness_um > max_roughness * 0.9:
            recommendations.append(
                "Rugosidade muito próxima do limite. "
                "Considerar limpeza ou tratamento adicional."
            )
        
        return recommendations
    
    def generate_compliance_report(
        self,
        vessel_id: str,
        period_start: datetime,
        period_end: datetime,
        checks: List[ComplianceCheck]
    ) -> ComplianceReport:
        """
        Gera relatório de conformidade para um período.
        
        Args:
            vessel_id: ID da embarcação
            period_start: Início do período
            period_end: Fim do período
            checks: Lista de verificações no período
            
        Returns:
            Relatório de conformidade
        """
        # Determina status geral
        if any(c.status == ComplianceStatus.CRITICAL for c in checks):
            overall_status = ComplianceStatus.CRITICAL
        elif any(c.status == ComplianceStatus.NON_COMPLIANT for c in checks):
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(c.status == ComplianceStatus.AT_RISK for c in checks):
            overall_status = ComplianceStatus.AT_RISK
        else:
            overall_status = ComplianceStatus.COMPLIANT
        
        # Calcula estatísticas
        avg_compliance_score = sum(c.compliance_score for c in checks) / len(checks) if checks else 0.0
        num_violations = sum(len(c.violations) for c in checks)
        num_warnings = sum(len(c.warnings) for c in checks)
        
        summary = {
            "total_checks": len(checks),
            "overall_status": overall_status.value,
            "average_compliance_score": avg_compliance_score,
            "total_violations": num_violations,
            "total_warnings": num_warnings,
            "compliance_rate": sum(1 for c in checks if c.status == ComplianceStatus.COMPLIANT) / len(checks) if checks else 0.0
        }
        
        # Compila recomendações
        all_recommendations = []
        for check in checks:
            all_recommendations.extend(check.recommendations)
        
        # Remove duplicatas mantendo ordem
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return ComplianceReport(
            report_id=f"COMP_{vessel_id}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}",
            vessel_id=vessel_id,
            report_period_start=period_start,
            report_period_end=period_end,
            generated_at=datetime.now(),
            overall_status=overall_status,
            checks=checks,
            summary=summary,
            recommendations=unique_recommendations
        )
    
    def check_fleet_compliance(
        self,
        fleet_data: List[Dict]
    ) -> Dict:
        """
        Verifica conformidade de toda a frota.
        
        Args:
            fleet_data: Lista de dados de embarcações
                [{"vessel_id": str, "fouling_mm": float, "roughness_um": float, ...}, ...]
            
        Returns:
            Resumo de conformidade da frota
        """
        fleet_checks = []
        
        for vessel_data in fleet_data:
            check = self.check_compliance(
                vessel_id=vessel_data["vessel_id"],
                fouling_thickness_mm=vessel_data["fouling_mm"],
                roughness_um=vessel_data["roughness_um"],
                vessel_type=vessel_data.get("vessel_type", "standard"),
                last_inspection_date=vessel_data.get("last_inspection_date")
            )
            fleet_checks.append(check)
        
        # Estatísticas da frota
        total_vessels = len(fleet_checks)
        compliant = sum(1 for c in fleet_checks if c.status == ComplianceStatus.COMPLIANT)
        at_risk = sum(1 for c in fleet_checks if c.status == ComplianceStatus.AT_RISK)
        non_compliant = sum(1 for c in fleet_checks if c.status == ComplianceStatus.NON_COMPLIANT)
        critical = sum(1 for c in fleet_checks if c.status == ComplianceStatus.CRITICAL)
        
        avg_compliance_score = sum(c.compliance_score for c in fleet_checks) / total_vessels if total_vessels > 0 else 0.0
        
        return {
            "total_vessels": total_vessels,
            "compliant": compliant,
            "at_risk": at_risk,
            "non_compliant": non_compliant,
            "critical": critical,
            "compliance_rate": compliant / total_vessels if total_vessels > 0 else 0.0,
            "average_compliance_score": avg_compliance_score,
            "checks": fleet_checks
        }
    
    def calculate_compliance_rate(
        self,
        vessel_ids: List[str],
        fleet_data: List[Dict]
    ) -> Dict:
        """
        Calcula taxa de conformidade agregada da frota.
        
        Args:
            vessel_ids: Lista de IDs de embarcações
            fleet_data: Lista de dados de embarcações
                [{"vessel_id": str, "fouling_mm": float, "roughness_um": float, ...}, ...]
            
        Returns:
            Dicionário com taxa de conformidade e estatísticas
        """
        # Filtrar dados das embarcações especificadas
        filtered_data = [
            d for d in fleet_data
            if d.get("vessel_id") in vessel_ids
        ]
        
        if not filtered_data:
            return {
                "compliance_rate": 0.0,
                "total_vessels": 0,
                "compliant": 0,
                "at_risk": 0,
                "non_compliant": 0,
                "critical": 0,
                "average_compliance_score": 0.0
            }
        
        # Verificar conformidade de cada embarcação
        fleet_compliance = self.check_fleet_compliance(filtered_data)
        
        total = fleet_compliance["total_vessels"]
        compliant = fleet_compliance["compliant"]
        
        # Taxa de conformidade (apenas embarcações totalmente conformes)
        compliance_rate = (compliant / total * 100.0) if total > 0 else 0.0
        
        return {
            "compliance_rate": compliance_rate,
            "compliance_rate_percent": compliance_rate,  # Alias para compatibilidade
            "total_vessels": total,
            "compliant": compliant,
            "at_risk": fleet_compliance["at_risk"],
            "non_compliant": fleet_compliance["non_compliant"],
            "critical": fleet_compliance["critical"],
            "average_compliance_score": fleet_compliance["average_compliance_score"],
            "checks": fleet_compliance["checks"]
        }


# Função de conveniência
def check_normam401_compliance(
    vessel_id: str,
    fouling_thickness_mm: float,
    roughness_um: float,
    vessel_type: str = "standard",
    last_inspection_date: Optional[datetime] = None
) -> ComplianceCheck:
    """
    Verifica conformidade com NORMAM 401.
    
    Args:
        vessel_id: ID da embarcação
        fouling_thickness_mm: Espessura de bioincrustação (mm)
        roughness_um: Rugosidade (μm)
        vessel_type: Tipo de embarcação
        last_inspection_date: Data da última inspeção
        
    Returns:
        Resultado da verificação
    """
    service = NORMAM401ComplianceService()
    return service.check_compliance(
        vessel_id,
        fouling_thickness_mm,
        roughness_um,
        vessel_type,
        last_inspection_date
    )


if __name__ == "__main__":
    # Exemplo de uso
    check = check_normam401_compliance(
        vessel_id="VESSEL001",
        fouling_thickness_mm=4.5,
        roughness_um=450.0,
        vessel_type="tanker",
        last_inspection_date=datetime.now() - timedelta(days=60)
    )
    
    print("Verificação de Conformidade NORMAM 401:")
    print(f"Status: {check.status.value}")
    print(f"Espessura: {check.fouling_thickness_mm:.2f} mm (limite: {check.max_allowed_thickness_mm:.2f} mm)")
    print(f"Rugosidade: {check.roughness_um:.2f} μm (limite: {check.max_allowed_roughness_um:.2f} μm)")
    print(f"Score de Conformidade: {check.compliance_score:.2%}")
    print(f"\nViolações: {len(check.violations)}")
    for violation in check.violations:
        print(f"  - {violation}")
    print(f"\nAvisos: {len(check.warnings)}")
    for warning in check.warnings:
        print(f"  - {warning}")
    print(f"\nRecomendações:")
    for rec in check.recommendations:
        print(f"  - {rec}")

