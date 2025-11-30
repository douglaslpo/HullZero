"""
Modelo de Otimização de Inspeções NORMAM 401 - HullZero

Este módulo implementa otimização de cronograma de inspeções NORMAM 401,
considerando risco, disponibilidade e custos.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .normam401_risk import NORMAM401RiskPredictor, NORMAM401RiskPrediction
from .fouling_prediction import VesselFeatures


class InspectionPriority(Enum):
    """Prioridade de inspeção"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class InspectionWindow:
    """Janela de oportunidade para inspeção"""
    start_date: datetime
    end_date: datetime
    priority: InspectionPriority
    risk_score: float
    estimated_cost: float
    availability_score: float  # 0-1, quão disponível está a embarcação
    notes: str


@dataclass
class ScheduledInspection:
    """Inspeção agendada"""
    inspection_id: str
    vessel_id: str
    scheduled_date: datetime
    priority: InspectionPriority
    risk_score_at_inspection: float
    estimated_cost: float
    reason: str
    recommended_location: Optional[str] = None


@dataclass
class InspectionSchedule:
    """Cronograma de inspeções"""
    vessel_id: str
    horizon_start: datetime
    horizon_end: datetime
    scheduled_inspections: List[ScheduledInspection]
    total_estimated_cost: float
    risk_reduction: float  # Redução de risco esperada
    compliance_improvement: float  # Melhoria esperada na conformidade


class InspectionOptimizer:
    """
    Otimiza cronograma de inspeções NORMAM 401.
    
    Considera:
    - Requisitos NORMAM 401 (mínimo trimestral)
    - Risco de não conformidade
    - Disponibilidade de embarcações
    - Custos de inspeção
    - Capacidade de estaleiros
    """
    
    MIN_INSPECTION_INTERVAL_DAYS = 90  # Trimestral mínimo
    MAX_INSPECTION_INTERVAL_DAYS = 120  # Máximo recomendado
    
    def __init__(self):
        self.risk_predictor = NORMAM401RiskPredictor()
    
    def optimize_inspection_schedule(
        self,
        vessel_id: str,
        vessel_features: VesselFeatures,
        horizon_days: int = 365,
        availability_windows: Optional[List[Tuple[datetime, datetime]]] = None,
        drydock_capacity: Optional[Dict] = None
    ) -> InspectionSchedule:
        """
        Otimiza cronograma de inspeções.
        
        Args:
            vessel_id: ID da embarcação
            vessel_features: Features da embarcação
            horizon_days: Horizonte de planejamento (dias)
            availability_windows: Janelas de disponibilidade [(start, end), ...]
            drydock_capacity: Capacidade de estaleiros {date: available_slots}
            
        Returns:
            Cronograma otimizado
        """
        horizon_start = datetime.now()
        horizon_end = horizon_start + timedelta(days=horizon_days)
        
        # Predizer risco ao longo do horizonte
        risk_timeline = self.predict_risk_timeline(
            vessel_id,
            vessel_features,
            horizon_days
        )
        
        # Encontrar janelas ótimas
        optimal_windows = self.find_optimal_windows(
            risk_timeline,
            availability_windows or [],
            horizon_start,
            horizon_end
        )
        
        # Agendar inspeções
        scheduled_inspections = self.schedule_inspections(
            vessel_id,
            optimal_windows,
            risk_timeline,
            drydock_capacity or {}
        )
        
        # Calcular métricas
        total_cost = sum(ins.estimated_cost for ins in scheduled_inspections)
        risk_reduction = self._calculate_risk_reduction(risk_timeline, scheduled_inspections)
        compliance_improvement = self._calculate_compliance_improvement(risk_timeline, scheduled_inspections)
        
        return InspectionSchedule(
            vessel_id=vessel_id,
            horizon_start=horizon_start,
            horizon_end=horizon_end,
            scheduled_inspections=scheduled_inspections,
            total_estimated_cost=total_cost,
            risk_reduction=risk_reduction,
            compliance_improvement=compliance_improvement
        )
    
    def predict_risk_timeline(
        self,
        vessel_id: str,
        vessel_features: VesselFeatures,
        horizon_days: int
    ) -> List[NORMAM401RiskPrediction]:
        """
        Prediz risco ao longo do horizonte.
        """
        intervals = []
        # Intervalos: semanal nos primeiros 30 dias, depois mensal
        for i in range(0, min(30, horizon_days), 7):
            intervals.append(i)
        for i in range(30, horizon_days, 30):
            intervals.append(i)
        if horizon_days not in intervals:
            intervals.append(horizon_days)
        
        predictions = []
        for days_ahead in intervals:
            prediction = self.risk_predictor.predict_risk(
                vessel_id,
                vessel_features,
                days_ahead
            )
            predictions.append(prediction)
        
        return predictions
    
    def find_optimal_windows(
        self,
        risk_timeline: List[NORMAM401RiskPrediction],
        availability_windows: List[Tuple[datetime, datetime]],
        horizon_start: datetime,
        horizon_end: datetime
    ) -> List[InspectionWindow]:
        """
        Encontra janelas ótimas para inspeção.
        """
        windows = []
        
        # Janela 1: Baseada em requisito trimestral
        current_date = horizon_start
        while current_date < horizon_end:
            window_end = current_date + timedelta(days=30)  # Janela de 30 dias
            
            # Calcular risco médio na janela
            window_risks = [
                r for r in risk_timeline
                if horizon_start + timedelta(days=r.days_ahead) >= current_date
                and horizon_start + timedelta(days=r.days_ahead) <= window_end
            ]
            
            avg_risk = sum(r.risk_score for r in window_risks) / len(window_risks) if window_risks else 0.5
            
            # Verificar disponibilidade
            availability = self._check_availability(current_date, window_end, availability_windows)
            
            # Prioridade baseada em risco
            if avg_risk >= 0.8:
                priority = InspectionPriority.URGENT
            elif avg_risk >= 0.6:
                priority = InspectionPriority.HIGH
            elif avg_risk >= 0.4:
                priority = InspectionPriority.MEDIUM
            else:
                priority = InspectionPriority.LOW
            
            # Custo estimado (simplificado)
            estimated_cost = self._estimate_inspection_cost(priority)
            
            windows.append(InspectionWindow(
                start_date=current_date,
                end_date=window_end,
                priority=priority,
                risk_score=avg_risk,
                estimated_cost=estimated_cost,
                availability_score=availability,
                notes=f"Janela trimestral - Risco médio: {avg_risk:.2%}"
            ))
            
            current_date += timedelta(days=self.MIN_INSPECTION_INTERVAL_DAYS)
        
        # Janelas adicionais baseadas em picos de risco
        for i, risk_pred in enumerate(risk_timeline):
            if risk_pred.risk_score >= 0.7 and i > 0:
                pred_date = horizon_start + timedelta(days=risk_pred.days_ahead)
                
                # Verificar se já não está coberto por janela trimestral
                covered = any(
                    w.start_date <= pred_date <= w.end_date
                    for w in windows
                )
                
                if not covered:
                    window_start = pred_date - timedelta(days=7)
                    window_end = pred_date + timedelta(days=7)
                    
                    availability = self._check_availability(window_start, window_end, availability_windows)
                    
                    windows.append(InspectionWindow(
                        start_date=window_start,
                        end_date=window_end,
                        priority=InspectionPriority.HIGH,
                        risk_score=risk_pred.risk_score,
                        estimated_cost=self._estimate_inspection_cost(InspectionPriority.HIGH),
                        availability_score=availability,
                        notes=f"Janela baseada em pico de risco ({risk_pred.risk_score:.2%})"
                    ))
        
        # Ordenar por prioridade e risco
        windows.sort(key=lambda w: (w.priority.value, -w.risk_score), reverse=True)
        
        return windows
    
    def schedule_inspections(
        self,
        vessel_id: str,
        optimal_windows: List[InspectionWindow],
        risk_timeline: List[NORMAM401RiskPrediction],
        drydock_capacity: Dict
    ) -> List[ScheduledInspection]:
        """
        Agenda inspeções baseado em janelas ótimas.
        """
        scheduled = []
        last_inspection_date = None
        
        for window in optimal_windows:
            # Verificar intervalo mínimo desde última inspeção
            if last_inspection_date:
                days_since = (window.start_date - last_inspection_date).days
                if days_since < self.MIN_INSPECTION_INTERVAL_DAYS:
                    continue  # Pular se muito próximo da última
            
            # Verificar capacidade de estaleiro
            if not self._check_drydock_capacity(window.start_date, drydock_capacity):
                # Tentar próximo dia disponível
                window.start_date = self._find_next_available_date(window.start_date, drydock_capacity)
            
            # Encontrar risco na data agendada
            scheduled_date = window.start_date
            risk_at_date = self._get_risk_at_date(scheduled_date, risk_timeline)
            
            # Criar inspeção agendada
            inspection = ScheduledInspection(
                inspection_id=f"INS_{vessel_id}_{scheduled_date.strftime('%Y%m%d')}",
                vessel_id=vessel_id,
                scheduled_date=scheduled_date,
                priority=window.priority,
                risk_score_at_inspection=risk_at_date,
                estimated_cost=window.estimated_cost,
                reason=window.notes,
                recommended_location=self._recommend_location(scheduled_date)
            )
            
            scheduled.append(inspection)
            last_inspection_date = scheduled_date
        
        return scheduled
    
    def _check_availability(
        self,
        start: datetime,
        end: datetime,
        availability_windows: List[Tuple[datetime, datetime]]
    ) -> float:
        """
        Verifica disponibilidade na janela (0-1).
        """
        if not availability_windows:
            return 0.5  # Assumir disponibilidade média se não especificado
        
        # Verificar sobreposição com janelas de disponibilidade
        overlaps = []
        for avail_start, avail_end in availability_windows:
            if start <= avail_end and end >= avail_start:
                overlap_start = max(start, avail_start)
                overlap_end = min(end, avail_end)
                overlap_days = (overlap_end - overlap_start).days
                total_days = (end - start).days
                overlaps.append(overlap_days / total_days if total_days > 0 else 0)
        
        return max(overlaps) if overlaps else 0.0
    
    def _estimate_inspection_cost(self, priority: InspectionPriority) -> float:
        """
        Estima custo de inspeção baseado em prioridade.
        """
        base_costs = {
            InspectionPriority.LOW: 50000.0,  # R$ 50k
            InspectionPriority.MEDIUM: 75000.0,  # R$ 75k
            InspectionPriority.HIGH: 100000.0,  # R$ 100k
            InspectionPriority.URGENT: 150000.0  # R$ 150k
        }
        return base_costs.get(priority, 75000.0)
    
    def _check_drydock_capacity(self, date: datetime, capacity: Dict) -> bool:
        """
        Verifica se há capacidade de estaleiro na data.
        """
        date_key = date.strftime('%Y-%m-%d')
        return capacity.get(date_key, {}).get('available_slots', 0) > 0
    
    def _find_next_available_date(
        self,
        start_date: datetime,
        capacity: Dict
    ) -> datetime:
        """
        Encontra próxima data disponível.
        """
        current = start_date
        for _ in range(30):  # Buscar até 30 dias à frente
            if self._check_drydock_capacity(current, capacity):
                return current
            current += timedelta(days=1)
        return start_date  # Retornar data original se não encontrar
    
    def _get_risk_at_date(
        self,
        date: datetime,
        risk_timeline: List[NORMAM401RiskPrediction]
    ) -> float:
        """
        Obtém risco na data específica.
        """
        days_ahead = (date - datetime.now()).days
        closest = min(risk_timeline, key=lambda r: abs(r.days_ahead - days_ahead))
        return closest.risk_score
    
    def _recommend_location(self, date: datetime) -> Optional[str]:
        """
        Recomenda localização para inspeção.
        """
        # Simplificado - em produção, considerar rota e portos próximos
        return "Porto base recomendado"
    
    def _calculate_risk_reduction(
        self,
        risk_timeline: List[NORMAM401RiskPrediction],
        scheduled_inspections: List[ScheduledInspection]
    ) -> float:
        """
        Calcula redução de risco esperada.
        """
        if not scheduled_inspections:
            return 0.0
        
        # Risco médio antes das inspeções
        avg_risk_before = sum(r.risk_score for r in risk_timeline) / len(risk_timeline)
        
        # Risco médio após inspeções (assumindo redução de 50% após cada inspeção)
        risk_reduction_per_inspection = 0.5
        total_reduction = len(scheduled_inspections) * risk_reduction_per_inspection
        
        return min(1.0, total_reduction)
    
    def _calculate_compliance_improvement(
        self,
        risk_timeline: List[NORMAM401RiskPrediction],
        scheduled_inspections: List[ScheduledInspection]
    ) -> float:
        """
        Calcula melhoria esperada na conformidade.
        """
        if not scheduled_inspections:
            return 0.0
        
        # Melhoria baseada no número de inspeções
        improvement_per_inspection = 0.15  # 15% de melhoria por inspeção
        total_improvement = len(scheduled_inspections) * improvement_per_inspection
        
        return min(1.0, total_improvement)
    
    def optimize_global_schedule(
        self,
        vessels_schedules: List[InspectionSchedule],
        drydock_capacity: Dict
    ) -> List[InspectionSchedule]:
        """
        Otimiza cronograma global considerando capacidade de estaleiros.
        """
        # Agrupar inspeções por data
        inspections_by_date = {}
        for schedule in vessels_schedules:
            for inspection in schedule.scheduled_inspections:
                date_key = inspection.scheduled_date.strftime('%Y-%m-%d')
                if date_key not in inspections_by_date:
                    inspections_by_date[date_key] = []
                inspections_by_date[date_key].append(inspection)
        
        # Ajustar datas para respeitar capacidade
        optimized_schedules = []
        for schedule in vessels_schedules:
            adjusted_inspections = []
            for inspection in schedule.scheduled_inspections:
                date_key = inspection.scheduled_date.strftime('%Y-%m-%d')
                capacity = drydock_capacity.get(date_key, {}).get('available_slots', 0)
                
                # Se exceder capacidade, mover para próxima data disponível
                if capacity <= 0:
                    new_date = self._find_next_available_date(
                        inspection.scheduled_date,
                        drydock_capacity
                    )
                    inspection.scheduled_date = new_date
                
                adjusted_inspections.append(inspection)
            
            # Atualizar schedule
            schedule.scheduled_inspections = adjusted_inspections
            schedule.total_estimated_cost = sum(ins.estimated_cost for ins in adjusted_inspections)
            optimized_schedules.append(schedule)
        
        return optimized_schedules


# Função de conveniência
def optimize_inspections(
    vessel_id: str,
    vessel_features: VesselFeatures,
    horizon_days: int = 365
) -> InspectionSchedule:
    """
    Otimiza cronograma de inspeções.
    """
    optimizer = InspectionOptimizer()
    return optimizer.optimize_inspection_schedule(
        vessel_id,
        vessel_features,
        horizon_days
    )


if __name__ == "__main__":
    # Exemplo de uso
    from .fouling_prediction import VesselFeatures
    
    features = VesselFeatures(
        vessel_id="VESSEL001",
        time_since_cleaning_days=90,
        water_temperature_c=25.0,
        salinity_psu=32.5,
        time_in_port_hours=120,
        average_speed_knots=12.0,
        route_region="South_Atlantic",
        paint_type="Antifouling_Type_A",
        vessel_type="Tanker",
        hull_area_m2=5000.0
    )
    
    schedule = optimize_inspections("VESSEL001", features, horizon_days=365)
    
    print("Cronograma Otimizado de Inspeções:")
    print(f"Horizonte: {schedule.horizon_start.date()} a {schedule.horizon_end.date()}")
    print(f"Total de Inspeções: {len(schedule.scheduled_inspections)}")
    print(f"Custo Total Estimado: R$ {schedule.total_estimated_cost:,.2f}")
    print(f"\nInspeções Agendadas:")
    for ins in schedule.scheduled_inspections:
        print(f"  - {ins.scheduled_date.date()}: {ins.priority.value} (Risco: {ins.risk_score_at_inspection:.2%}, Custo: R$ {ins.estimated_cost:,.2f})")
        print(f"    Motivo: {ins.reason}")

