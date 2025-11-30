"""
Modelo de Detecção de Anomalias em Conformidade - HullZero

Este módulo detecta anomalias em dados de conformidade que podem indicar
problemas nos dados, mudanças súbitas ou tendências preocupantes.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats


class AnomalyType(Enum):
    """Tipos de anomalias"""
    SUDDEN_CHANGE = "sudden_change"
    CONCERNING_TREND = "concerning_trend"
    INCONSISTENT_VALUE = "inconsistent_value"
    MISSING_DATA = "missing_data"
    OUTLIER = "outlier"


class AnomalySeverity(Enum):
    """Severidade da anomalia"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceDataPoint:
    """Ponto de dados de conformidade"""
    timestamp: datetime
    vessel_id: str
    fouling_mm: float
    roughness_um: float
    compliance_status: str
    compliance_score: float
    source: str  # 'prediction', 'inspection', 'measurement'


@dataclass
class Anomaly:
    """Anomalia detectada"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    timestamp: datetime
    vessel_id: str
    description: str
    affected_metrics: List[str]
    recommendation: str
    confidence: float  # 0-1
    related_data_points: List[ComplianceDataPoint]


@dataclass
class TrendAnalysis:
    """Análise de tendência"""
    slope: float  # Taxa de mudança (mm/dia ou μm/dia)
    intercept: float
    r_squared: float
    p_value: float
    is_significant: bool
    direction: str  # 'increasing', 'decreasing', 'stable'


class ComplianceAnomalyDetector:
    """
    Detecta anomalias em dados de conformidade.
    
    Tipos de anomalias detectadas:
    - Mudanças súbitas não explicadas
    - Tendências preocupantes
    - Valores inconsistentes
    - Dados faltantes
    - Outliers estatísticos
    """
    
    # Thresholds
    SUDDEN_CHANGE_THRESHOLD_MM = 2.0  # Mudança > 2mm é suspeita
    SUDDEN_CHANGE_THRESHOLD_UM = 200.0  # Mudança > 200μm é suspeita
    CONCERNING_TREND_SLOPE_MM_PER_DAY = 0.1  # Crescimento > 0.1mm/dia
    OUTLIER_Z_SCORE = 3.0  # Z-score > 3 é outlier
    
    def __init__(self):
        pass
    
    def detect_anomalies(
        self,
        compliance_history: List[ComplianceDataPoint],
        min_data_points: int = 3
    ) -> List[Anomaly]:
        """
        Detecta anomalias em histórico de conformidade.
        
        Args:
            compliance_history: Histórico de dados de conformidade
            min_data_points: Número mínimo de pontos para análise
            
        Returns:
            Lista de anomalias detectadas
        """
        if len(compliance_history) < min_data_points:
            return []  # Dados insuficientes
        
        anomalies = []
        
        # Ordenar por timestamp
        sorted_history = sorted(compliance_history, key=lambda x: x.timestamp)
        
        # 1. Detectar mudanças súbitas
        sudden_changes = self._detect_sudden_changes(sorted_history)
        anomalies.extend(sudden_changes)
        
        # 2. Detectar tendências preocupantes
        concerning_trends = self._detect_concerning_trends(sorted_history)
        anomalies.extend(concerning_trends)
        
        # 3. Detectar valores inconsistentes
        inconsistencies = self._detect_inconsistencies(sorted_history)
        anomalies.extend(inconsistencies)
        
        # 4. Detectar outliers
        outliers = self._detect_outliers(sorted_history)
        anomalies.extend(outliers)
        
        # 5. Detectar dados faltantes
        missing_data = self._detect_missing_data(sorted_history)
        anomalies.extend(missing_data)
        
        # Ordenar por severidade e timestamp
        anomalies.sort(key=lambda a: (a.severity.value, a.timestamp), reverse=True)
        
        return anomalies
    
    def _detect_sudden_changes(
        self,
        history: List[ComplianceDataPoint]
    ) -> List[Anomaly]:
        """
        Detecta mudanças súbitas não explicadas.
        """
        anomalies = []
        
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            
            # Calcular mudança
            fouling_change = abs(curr.fouling_mm - prev.fouling_mm)
            roughness_change = abs(curr.roughness_um - prev.roughness_um)
            time_diff = (curr.timestamp - prev.timestamp).days
            
            # Mudança súbita em bioincrustação
            if fouling_change > self.SUDDEN_CHANGE_THRESHOLD_MM:
                severity = AnomalySeverity.HIGH if fouling_change > 3.0 else AnomalySeverity.MEDIUM
                
                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM_{curr.vessel_id}_{curr.timestamp.strftime('%Y%m%d%H%M%S')}",
                    anomaly_type=AnomalyType.SUDDEN_CHANGE,
                    severity=severity,
                    timestamp=curr.timestamp,
                    vessel_id=curr.vessel_id,
                    description=(
                        f"Mudança súbita de bioincrustação: {prev.fouling_mm:.2f} mm → "
                        f"{curr.fouling_mm:.2f} mm ({fouling_change:.2f} mm) em {time_diff} dias"
                    ),
                    affected_metrics=["fouling_mm"],
                    recommendation=(
                        "Verificar se houve limpeza/manutenção não registrada ou "
                        "se há erro na medição. Revisar dados de manutenção."
                    ),
                    confidence=0.8 if time_diff < 7 else 0.6,
                    related_data_points=[prev, curr]
                ))
            
            # Mudança súbita em rugosidade
            if roughness_change > self.SUDDEN_CHANGE_THRESHOLD_UM:
                severity = AnomalySeverity.HIGH if roughness_change > 300.0 else AnomalySeverity.MEDIUM
                
                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM_{curr.vessel_id}_{curr.timestamp.strftime('%Y%m%d%H%M%S')}_R",
                    anomaly_type=AnomalyType.SUDDEN_CHANGE,
                    severity=severity,
                    timestamp=curr.timestamp,
                    vessel_id=curr.vessel_id,
                    description=(
                        f"Mudança súbita de rugosidade: {prev.roughness_um:.2f} μm → "
                        f"{curr.roughness_um:.2f} μm ({roughness_change:.2f} μm) em {time_diff} dias"
                    ),
                    affected_metrics=["roughness_um"],
                    recommendation=(
                        "Verificar se houve tratamento de superfície não registrado. "
                        "Revisar dados de manutenção."
                    ),
                    confidence=0.8 if time_diff < 7 else 0.6,
                    related_data_points=[prev, curr]
                ))
        
        return anomalies
    
    def _detect_concerning_trends(
        self,
        history: List[ComplianceDataPoint]
    ) -> List[Anomaly]:
        """
        Detecta tendências preocupantes.
        """
        anomalies = []
        
        if len(history) < 5:
            return anomalies  # Dados insuficientes para análise de tendência
        
        # Análise de tendência para bioincrustação
        fouling_trend = self._calculate_trend(
            [h.timestamp for h in history],
            [h.fouling_mm for h in history]
        )
        
        if fouling_trend.is_significant and fouling_trend.slope > self.CONCERNING_TREND_SLOPE_MM_PER_DAY:
            severity = (
                AnomalySeverity.CRITICAL if fouling_trend.slope > 0.2
                else AnomalySeverity.HIGH if fouling_trend.slope > 0.15
                else AnomalySeverity.MEDIUM
            )
            
            anomalies.append(Anomaly(
                anomaly_id=f"TREND_{history[0].vessel_id}_{history[-1].timestamp.strftime('%Y%m%d')}",
                anomaly_type=AnomalyType.CONCERNING_TREND,
                severity=severity,
                timestamp=history[-1].timestamp,
                vessel_id=history[0].vessel_id,
                description=(
                    f"Tendência de crescimento acelerado: {fouling_trend.slope:.3f} mm/dia "
                    f"(normal: <0.05 mm/dia). R² = {fouling_trend.r_squared:.2f}"
                ),
                affected_metrics=["fouling_mm"],
                recommendation=(
                    "Investigar causas do crescimento acelerado. Considerar limpeza preventiva "
                    "ou revisão de tinta anti-incrustante. Monitoramento intensificado recomendado."
                ),
                confidence=fouling_trend.r_squared,
                related_data_points=history[-5:]  # Últimos 5 pontos
            ))
        
        # Análise de tendência para rugosidade
        roughness_trend = self._calculate_trend(
            [h.timestamp for h in history],
            [h.roughness_um for h in history]
        )
        
        if roughness_trend.is_significant and roughness_trend.slope > 2.0:  # μm/dia
            severity = (
                AnomalySeverity.HIGH if roughness_trend.slope > 5.0
                else AnomalySeverity.MEDIUM
            )
            
            anomalies.append(Anomaly(
                anomaly_id=f"TREND_{history[0].vessel_id}_{history[-1].timestamp.strftime('%Y%m%d')}_R",
                anomaly_type=AnomalyType.CONCERNING_TREND,
                severity=severity,
                timestamp=history[-1].timestamp,
                vessel_id=history[0].vessel_id,
                description=(
                    f"Tendência de aumento de rugosidade: {roughness_trend.slope:.2f} μm/dia. "
                    f"R² = {roughness_trend.r_squared:.2f}"
                ),
                affected_metrics=["roughness_um"],
                recommendation=(
                    "Investigar causas do aumento de rugosidade. Pode indicar degradação "
                    "da superfície do casco ou tinta anti-incrustante."
                ),
                confidence=roughness_trend.r_squared,
                related_data_points=history[-5:]
            ))
        
        return anomalies
    
    def _detect_inconsistencies(
        self,
        history: List[ComplianceDataPoint]
    ) -> List[Anomaly]:
        """
        Detecta valores inconsistentes.
        """
        anomalies = []
        
        for point in history:
            # Inconsistência: bioincrustação muito alta mas rugosidade baixa (ou vice-versa)
            # Normalmente, bioincrustação e rugosidade estão correlacionadas
            expected_roughness = point.fouling_mm * 100.0  # Aproximação: 1mm ≈ 100μm
            actual_roughness = point.roughness_um
            
            if abs(actual_roughness - expected_roughness) > expected_roughness * 0.5:  # Diferença > 50%
                anomalies.append(Anomaly(
                    anomaly_id=f"INCONS_{point.vessel_id}_{point.timestamp.strftime('%Y%m%d%H%M%S')}",
                    anomaly_type=AnomalyType.INCONSISTENT_VALUE,
                    severity=AnomalySeverity.MEDIUM,
                    timestamp=point.timestamp,
                    vessel_id=point.vessel_id,
                    description=(
                        f"Valores inconsistentes: bioincrustação {point.fouling_mm:.2f} mm "
                        f"mas rugosidade {point.roughness_um:.2f} μm "
                        f"(esperado: ~{expected_roughness:.2f} μm)"
                    ),
                    affected_metrics=["fouling_mm", "roughness_um"],
                    recommendation=(
                        "Verificar medições. Pode haver erro em uma das métricas ou "
                        "condições especiais do casco."
                    ),
                    confidence=0.7,
                    related_data_points=[point]
                ))
        
        return anomalies
    
    def _detect_outliers(
        self,
        history: List[ComplianceDataPoint]
    ) -> List[Anomaly]:
        """
        Detecta outliers estatísticos.
        """
        anomalies = []
        
        if len(history) < 5:
            return anomalies
        
        # Calcular Z-scores
        fouling_values = [h.fouling_mm for h in history]
        roughness_values = [h.roughness_um for h in history]
        
        fouling_mean = np.mean(fouling_values)
        fouling_std = np.std(fouling_values)
        roughness_mean = np.mean(roughness_values)
        roughness_std = np.std(roughness_values)
        
        for point in history:
            # Z-score para bioincrustação
            if fouling_std > 0:
                z_score_fouling = abs((point.fouling_mm - fouling_mean) / fouling_std)
                if z_score_fouling > self.OUTLIER_Z_SCORE:
                    anomalies.append(Anomaly(
                        anomaly_id=f"OUTLIER_{point.vessel_id}_{point.timestamp.strftime('%Y%m%d%H%M%S')}",
                        anomaly_type=AnomalyType.OUTLIER,
                        severity=AnomalySeverity.MEDIUM,
                        timestamp=point.timestamp,
                        vessel_id=point.vessel_id,
                        description=(
                            f"Outlier em bioincrustação: {point.fouling_mm:.2f} mm "
                            f"(média: {fouling_mean:.2f} mm, Z-score: {z_score_fouling:.2f})"
                        ),
                        affected_metrics=["fouling_mm"],
                        recommendation="Verificar se o valor é correto ou se há erro na medição.",
                        confidence=0.6,
                        related_data_points=[point]
                    ))
            
            # Z-score para rugosidade
            if roughness_std > 0:
                z_score_roughness = abs((point.roughness_um - roughness_mean) / roughness_std)
                if z_score_roughness > self.OUTLIER_Z_SCORE:
                    anomalies.append(Anomaly(
                        anomaly_id=f"OUTLIER_{point.vessel_id}_{point.timestamp.strftime('%Y%m%d%H%M%S')}_R",
                        anomaly_type=AnomalyType.OUTLIER,
                        severity=AnomalySeverity.MEDIUM,
                        timestamp=point.timestamp,
                        vessel_id=point.vessel_id,
                        description=(
                            f"Outlier em rugosidade: {point.roughness_um:.2f} μm "
                            f"(média: {roughness_mean:.2f} μm, Z-score: {z_score_roughness:.2f})"
                        ),
                        affected_metrics=["roughness_um"],
                        recommendation="Verificar se o valor é correto ou se há erro na medição.",
                        confidence=0.6,
                        related_data_points=[point]
                    ))
        
        return anomalies
    
    def _detect_missing_data(
        self,
        history: List[ComplianceDataPoint]
    ) -> List[Anomaly]:
        """
        Detecta períodos com dados faltantes.
        """
        anomalies = []
        
        if len(history) < 2:
            return anomalies
        
        # Ordenar por timestamp
        sorted_history = sorted(history, key=lambda x: x.timestamp)
        
        # Verificar gaps
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i-1]
            curr = sorted_history[i]
            
            days_gap = (curr.timestamp - prev.timestamp).days
            
            # Gap > 30 dias sem dados é suspeito
            if days_gap > 30:
                severity = (
                    AnomalySeverity.HIGH if days_gap > 90
                    else AnomalySeverity.MEDIUM if days_gap > 60
                    else AnomalySeverity.LOW
                )
                
                anomalies.append(Anomaly(
                    anomaly_id=f"MISSING_{curr.vessel_id}_{prev.timestamp.strftime('%Y%m%d')}",
                    anomaly_type=AnomalyType.MISSING_DATA,
                    severity=severity,
                    timestamp=prev.timestamp + timedelta(days=days_gap // 2),
                    vessel_id=curr.vessel_id,
                    description=(
                        f"Gap de dados: {days_gap} dias sem medições entre "
                        f"{prev.timestamp.date()} e {curr.timestamp.date()}"
                    ),
                    affected_metrics=["fouling_mm", "roughness_um"],
                    recommendation=(
                        "Verificar se há dados não registrados ou problemas no sistema de coleta. "
                        "Considerar interpolação ou preenchimento de dados."
                    ),
                    confidence=0.8,
                    related_data_points=[prev, curr]
                ))
        
        return anomalies
    
    def _calculate_trend(
        self,
        timestamps: List[datetime],
        values: List[float]
    ) -> TrendAnalysis:
        """
        Calcula tendência usando regressão linear.
        """
        if len(timestamps) < 3:
            return TrendAnalysis(
                slope=0.0,
                intercept=0.0,
                r_squared=0.0,
                p_value=1.0,
                is_significant=False,
                direction="stable"
            )
        
        # Converter timestamps para dias desde o primeiro
        first_timestamp = timestamps[0]
        days = [(ts - first_timestamp).days for ts in timestamps]
        
        # Regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(days, values)
        r_squared = r_value ** 2
        
        # Determinar direção
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return TrendAnalysis(
            slope=slope,
            intercept=intercept,
            r_squared=r_squared,
            p_value=p_value,
            is_significant=p_value < 0.05,
            direction=direction
        )


# Função de conveniência
def detect_compliance_anomalies(
    compliance_history: List[ComplianceDataPoint]
) -> List[Anomaly]:
    """
    Detecta anomalias em histórico de conformidade.
    """
    detector = ComplianceAnomalyDetector()
    return detector.detect_anomalies(compliance_history)


if __name__ == "__main__":
    # Exemplo de uso
    from datetime import datetime, timedelta
    
    history = [
        ComplianceDataPoint(
            timestamp=datetime.now() - timedelta(days=90),
            vessel_id="VESSEL001",
            fouling_mm=2.0,
            roughness_um=200.0,
            compliance_status="compliant",
            compliance_score=0.9,
            source="inspection"
        ),
        ComplianceDataPoint(
            timestamp=datetime.now() - timedelta(days=60),
            vessel_id="VESSEL001",
            fouling_mm=3.0,
            roughness_um=300.0,
            compliance_status="compliant",
            compliance_score=0.8,
            source="prediction"
        ),
        ComplianceDataPoint(
            timestamp=datetime.now() - timedelta(days=30),
            vessel_id="VESSEL001",
            fouling_mm=4.5,
            roughness_um=450.0,
            compliance_status="at_risk",
            compliance_score=0.7,
            source="prediction"
        ),
        ComplianceDataPoint(
            timestamp=datetime.now(),
            vessel_id="VESSEL001",
            fouling_mm=6.5,  # Mudança súbita!
            roughness_um=650.0,
            compliance_status="non_compliant",
            compliance_score=0.3,
            source="prediction"
        ),
    ]
    
    anomalies = detect_compliance_anomalies(history)
    
    print(f"Anomalias Detectadas: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"\n{anomaly.anomaly_type.value.upper()} - {anomaly.severity.value.upper()}")
        print(f"  Descrição: {anomaly.description}")
        print(f"  Recomendação: {anomaly.recommendation}")

