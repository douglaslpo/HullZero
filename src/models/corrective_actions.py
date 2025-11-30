"""
Modelo de Recomendação de Ações Corretivas - HullZero

Este módulo recomenda ações corretivas para não conformidades NORMAM 401,
baseado no status de conformidade e fatores de risco.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.services.compliance_service import ComplianceStatus, ComplianceCheck


class ActionPriority(Enum):
    """Prioridade da ação"""
    IMMEDIATE = "immediate"  # Ação imediata (horas)
    HIGH = "high"  # Alta prioridade (dias)
    MEDIUM = "medium"  # Prioridade média (semanas)
    LOW = "low"  # Baixa prioridade (meses)


@dataclass
class CorrectiveAction:
    """Ação corretiva recomendada"""
    action_id: str
    action_type: str
    priority: ActionPriority
    title: str
    description: str
    deadline: datetime
    estimated_cost_brl: float
    estimated_duration_hours: float
    expected_compliance_restoration: str
    required_resources: List[str]
    steps: List[str]
    success_criteria: List[str]
    related_violations: List[str]


class CorrectiveActionRecommender:
    """
    Recomenda ações corretivas para não conformidades NORMAM 401.
    """
    
    # Custos estimados (R$)
    CLEANING_COSTS = {
        'underwater': 50000.0,  # Limpeza subaquática
        'dry_dock': 150000.0,  # Estaleiro
        'high_pressure': 30000.0,  # Alta pressão
        'standard': 75000.0
    }
    
    # Durações estimadas (horas)
    CLEANING_DURATIONS = {
        'underwater': 24.0,  # 1 dia
        'dry_dock': 120.0,  # 5 dias
        'high_pressure': 12.0,  # 12 horas
        'standard': 48.0  # 2 dias
    }
    
    def __init__(self):
        pass
    
    def recommend_actions(
        self,
        compliance_status: ComplianceCheck,
        risk_factors: Optional[List[Dict]] = None
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações baseadas no status de conformidade.
        
        Args:
            compliance_status: Status de conformidade
            risk_factors: Fatores de risco adicionais (opcional)
            
        Returns:
            Lista de ações corretivas recomendadas
        """
        actions = []
        
        if compliance_status.status == ComplianceStatus.CRITICAL:
            actions.extend(self._recommend_critical_actions(compliance_status))
        
        elif compliance_status.status == ComplianceStatus.NON_COMPLIANT:
            actions.extend(self._recommend_non_compliant_actions(compliance_status))
        
        elif compliance_status.status == ComplianceStatus.AT_RISK:
            actions.extend(self._recommend_at_risk_actions(compliance_status))
        
        else:  # COMPLIANT
            actions.extend(self._recommend_preventive_actions(compliance_status))
        
        # Adicionar ações baseadas em fatores de risco
        if risk_factors:
            actions.extend(self._recommend_risk_based_actions(compliance_status, risk_factors))
        
        # Ordenar por prioridade
        priority_order = {
            ActionPriority.IMMEDIATE: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3
        }
        actions.sort(key=lambda a: priority_order[a.priority])
        
        return actions
    
    def _recommend_critical_actions(
        self,
        compliance_status: ComplianceCheck
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações para status crítico.
        """
        actions = []
        
        # Ação 1: Limpeza imediata
        cleaning_method = self._determine_cleaning_method(compliance_status)
        cleaning_cost = self._estimate_cleaning_cost(compliance_status, cleaning_method)
        cleaning_duration = self.CLEANING_DURATIONS.get(cleaning_method, 48.0)
        
        actions.append(CorrectiveAction(
            action_id=f"ACTION_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="cleaning",
            priority=ActionPriority.IMMEDIATE,
            title="Limpeza Imediata do Casco",
            description=(
                f"Limpeza imediata do casco é necessária para restaurar conformidade. "
                f"Bioincrustação atual: {compliance_status.fouling_thickness_mm:.2f} mm "
                f"(limite: {compliance_status.max_allowed_thickness_mm:.2f} mm). "
                f"Rugosidade atual: {compliance_status.roughness_um:.2f} μm "
                f"(limite: {compliance_status.max_allowed_roughness_um:.2f} μm)."
            ),
            deadline=datetime.now() + timedelta(hours=24),
            estimated_cost_brl=cleaning_cost,
            estimated_duration_hours=cleaning_duration,
            expected_compliance_restoration="Após limpeza completa e verificação",
            required_resources=[
                "Equipe de limpeza especializada",
                "Equipamentos de limpeza",
                "Acesso ao casco (estaleiro ou equipe subaquática)",
                "Inspeção pós-limpeza"
            ],
            steps=[
                "1. Agendar limpeza imediata (dentro de 24 horas)",
                "2. Preparar equipamentos e equipe",
                "3. Realizar limpeza completa do casco",
                "4. Inspeção pós-limpeza para verificar conformidade",
                "5. Documentar processo e resultados",
                "6. Atualizar registros no sistema"
            ],
            success_criteria=[
                "Bioincrustação reduzida abaixo do limite",
                "Rugosidade reduzida abaixo do limite",
                "Conformidade NORMAM 401 restaurada",
                "Documentação completa"
            ],
            related_violations=compliance_status.violations
        ))
        
        # Ação 2: Notificação
        actions.append(CorrectiveAction(
            action_id=f"NOTIFY_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="notification",
            priority=ActionPriority.IMMEDIATE,
            title="Notificar Autoridades Competentes",
            description=(
                "Notificar autoridades competentes sobre não conformidade crítica "
                "conforme requisitos regulatórios."
            ),
            deadline=datetime.now() + timedelta(hours=4),
            estimated_cost_brl=0.0,
            estimated_duration_hours=1.0,
            expected_compliance_restoration="Documentação e transparência",
            required_resources=[
                "Documentação de não conformidade",
                "Canais de comunicação com autoridades"
            ],
            steps=[
                "1. Preparar documentação de não conformidade",
                "2. Notificar autoridades competentes",
                "3. Fornecer plano de ação corretiva",
                "4. Manter comunicação durante correção"
            ],
            success_criteria=[
                "Notificação enviada dentro do prazo",
                "Documentação completa",
                "Resposta recebida das autoridades"
            ],
            related_violations=compliance_status.violations
        ))
        
        # Ação 3: Monitoramento Intensificado
        actions.append(CorrectiveAction(
            action_id=f"MONITOR_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="monitoring",
            priority=ActionPriority.HIGH,
            title="Monitoramento Intensificado",
            description=(
                "Aumentar frequência de monitoramento para diária até conformidade ser restaurada."
            ),
            deadline=datetime.now() + timedelta(hours=12),
            estimated_cost_brl=5000.0,  # Custos de monitoramento adicional
            estimated_duration_hours=0.0,  # Contínuo
            expected_compliance_restoration="Detecção precoce de problemas",
            required_resources=[
                "Sistema de monitoramento",
                "Equipe de análise"
            ],
            steps=[
                "1. Configurar monitoramento diário",
                "2. Estabelecer alertas automáticos",
                "3. Revisar dados diariamente",
                "4. Reportar mudanças significativas"
            ],
            success_criteria=[
                "Monitoramento diário ativo",
                "Alertas configurados",
                "Relatórios diários gerados"
            ],
            related_violations=compliance_status.violations
        ))
        
        return actions
    
    def _recommend_non_compliant_actions(
        self,
        compliance_status: ComplianceCheck
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações para não conformidade.
        """
        actions = []
        
        # Ação 1: Agendar limpeza
        cleaning_method = self._determine_cleaning_method(compliance_status)
        cleaning_cost = self._estimate_cleaning_cost(compliance_status, cleaning_method)
        cleaning_duration = self.CLEANING_DURATIONS.get(cleaning_method, 48.0)
        
        actions.append(CorrectiveAction(
            action_id=f"ACTION_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="cleaning",
            priority=ActionPriority.HIGH,
            title="Agendar Limpeza do Casco",
            description=(
                f"Limpeza do casco deve ser agendada dentro de 7 dias. "
                f"Bioincrustação: {compliance_status.fouling_thickness_mm:.2f} mm "
                f"(limite: {compliance_status.max_allowed_thickness_mm:.2f} mm)."
            ),
            deadline=datetime.now() + timedelta(days=7),
            estimated_cost_brl=cleaning_cost,
            estimated_duration_hours=cleaning_duration,
            expected_compliance_restoration="Após limpeza",
            required_resources=[
                "Equipe de limpeza",
                "Equipamentos",
                "Acesso ao casco"
            ],
            steps=[
                "1. Agendar limpeza (dentro de 7 dias)",
                "2. Preparar recursos necessários",
                "3. Realizar limpeza",
                "4. Verificar conformidade pós-limpeza"
            ],
            success_criteria=[
                "Limpeza agendada",
                "Conformidade restaurada",
                "Documentação completa"
            ],
            related_violations=compliance_status.violations
        ))
        
        # Ação 2: Aumentar frequência de inspeções
        actions.append(CorrectiveAction(
            action_id=f"INSPECT_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="inspection",
            priority=ActionPriority.MEDIUM,
            title="Aumentar Frequência de Inspeções",
            description=(
                "Aumentar frequência de inspeções até conformidade ser restaurada."
            ),
            deadline=datetime.now() + timedelta(days=3),
            estimated_cost_brl=10000.0,
            estimated_duration_hours=8.0,
            expected_compliance_restoration="Monitoramento melhorado",
            required_resources=[
                "Inspetor qualificado",
                "Equipamentos de inspeção"
            ],
            steps=[
                "1. Agendar inspeção adicional",
                "2. Realizar inspeção",
                "3. Documentar resultados",
                "4. Planejar próxima inspeção"
            ],
            success_criteria=[
                "Inspeção realizada",
                "Resultados documentados",
                "Próxima inspeção agendada"
            ],
            related_violations=compliance_status.violations
        ))
        
        return actions
    
    def _recommend_at_risk_actions(
        self,
        compliance_status: ComplianceCheck
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações para embarcação em risco.
        """
        actions = []
        
        # Ação 1: Monitoramento intensificado
        actions.append(CorrectiveAction(
            action_id=f"MONITOR_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="monitoring",
            priority=ActionPriority.MEDIUM,
            title="Monitoramento Intensificado",
            description=(
                f"Aumentar frequência de monitoramento. "
                f"Bioincrustação próxima do limite: {compliance_status.fouling_thickness_mm:.2f} mm."
            ),
            deadline=datetime.now() + timedelta(days=1),
            estimated_cost_brl=3000.0,
            estimated_duration_hours=0.0,  # Contínuo
            expected_compliance_restoration="Preventivo",
            required_resources=[
                "Sistema de monitoramento",
                "Equipe de análise"
            ],
            steps=[
                "1. Configurar monitoramento semanal",
                "2. Estabelecer alertas",
                "3. Revisar dados semanalmente"
            ],
            success_criteria=[
                "Monitoramento ativo",
                "Alertas configurados"
            ],
            related_violations=compliance_status.warnings
        ))
        
        # Ação 2: Planejar limpeza preventiva
        cleaning_cost = self._estimate_cleaning_cost(compliance_status, "standard")
        
        actions.append(CorrectiveAction(
            action_id=f"PREVENT_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="preventive_cleaning",
            priority=ActionPriority.MEDIUM,
            title="Planejar Limpeza Preventiva",
            description=(
                "Planejar limpeza preventiva nos próximos 30 dias para evitar não conformidade."
            ),
            deadline=datetime.now() + timedelta(days=30),
            estimated_cost_brl=cleaning_cost,
            estimated_duration_hours=48.0,
            expected_compliance_restoration="Preventivo",
            required_resources=[
                "Equipe de limpeza",
                "Equipamentos",
                "Acesso ao casco"
            ],
            steps=[
                "1. Planejar limpeza preventiva (30 dias)",
                "2. Agendar recursos",
                "3. Realizar limpeza",
                "4. Verificar conformidade"
            ],
            success_criteria=[
                "Limpeza planejada",
                "Conformidade mantida"
            ],
            related_violations=compliance_status.warnings
        ))
        
        return actions
    
    def _recommend_preventive_actions(
        self,
        compliance_status: ComplianceCheck
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações preventivas para embarcação conforme.
        """
        actions = []
        
        # Ação 1: Manter monitoramento regular
        actions.append(CorrectiveAction(
            action_id=f"MAINTAIN_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            action_type="maintenance",
            priority=ActionPriority.LOW,
            title="Manter Monitoramento Regular",
            description=(
                "Embarcação em conformidade. Manter monitoramento regular conforme protocolo."
            ),
            deadline=compliance_status.next_inspection_due,
            estimated_cost_brl=0.0,
            estimated_duration_hours=0.0,
            expected_compliance_restoration="Manutenção",
            required_resources=[
                "Sistema de monitoramento"
            ],
            steps=[
                "1. Continuar monitoramento regular",
                "2. Manter inspeções trimestrais",
                "3. Documentar dados"
            ],
            success_criteria=[
                "Monitoramento contínuo",
                "Conformidade mantida"
            ],
            related_violations=[]
        ))
        
        return actions
    
    def _recommend_risk_based_actions(
        self,
        compliance_status: ComplianceCheck,
        risk_factors: List[Dict]
    ) -> List[CorrectiveAction]:
        """
        Recomenda ações baseadas em fatores de risco específicos.
        """
        actions = []
        
        for factor in risk_factors:
            if factor.get('severity') == 'high':
                # Ação específica para fator de alto risco
                actions.append(CorrectiveAction(
                    action_id=f"RISK_{compliance_status.vessel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    action_type="risk_mitigation",
                    priority=ActionPriority.HIGH,
                    title=f"Mitigar: {factor.get('factor_name', 'Fator de Risco')}",
                    description=factor.get('description', ''),
                    deadline=datetime.now() + timedelta(days=7),
                    estimated_cost_brl=10000.0,
                    estimated_duration_hours=24.0,
                    expected_compliance_restoration="Redução de risco",
                    required_resources=["Recursos específicos do fator"],
                    steps=[
                        "1. Analisar fator de risco",
                        "2. Implementar medidas de mitigação",
                        "3. Monitorar efetividade"
                    ],
                    success_criteria=[
                        "Fator de risco mitigado",
                        "Risco reduzido"
                    ],
                    related_violations=[factor.get('factor_name', '')]
                ))
        
        return actions
    
    def _determine_cleaning_method(
        self,
        compliance_status: ComplianceCheck
    ) -> str:
        """
        Determina método de limpeza apropriado.
        """
        # Se muito acima do limite, pode precisar de estaleiro
        if compliance_status.fouling_thickness_mm > compliance_status.max_allowed_thickness_mm * 1.5:
            return 'dry_dock'
        elif compliance_status.fouling_thickness_mm > compliance_status.max_allowed_thickness_mm * 1.2:
            return 'underwater'
        else:
            return 'high_pressure'
    
    def _estimate_cleaning_cost(
        self,
        compliance_status: ComplianceCheck,
        method: str
    ) -> float:
        """
        Estima custo de limpeza.
        """
        base_cost = self.CLEANING_COSTS.get(method, self.CLEANING_COSTS['standard'])
        
        # Ajustar baseado na severidade
        if compliance_status.status == ComplianceStatus.CRITICAL:
            base_cost *= 1.5  # 50% mais caro para casos críticos
        
        # Ajustar baseado na área (simplificado)
        # Em produção, considerar área real do casco
        
        return base_cost


# Função de conveniência
def recommend_corrective_actions(
    compliance_status: ComplianceCheck,
    risk_factors: Optional[List[Dict]] = None
) -> List[CorrectiveAction]:
    """
    Recomenda ações corretivas.
    """
    recommender = CorrectiveActionRecommender()
    return recommender.recommend_actions(compliance_status, risk_factors)


if __name__ == "__main__":
    # Exemplo de uso
    from src.services.compliance_service import ComplianceCheck, ComplianceStatus
    
    compliance = ComplianceCheck(
        vessel_id="VESSEL001",
        check_date=datetime.now(),
        status=ComplianceStatus.CRITICAL,
        fouling_thickness_mm=6.5,
        roughness_um=650.0,
        max_allowed_thickness_mm=5.0,
        max_allowed_roughness_um=500.0,
        violations=["Espessura excede limite", "Rugosidade excede limite"],
        warnings=[],
        compliance_score=0.3,
        next_inspection_due=datetime.now() + timedelta(days=90),
        recommendations=[]
    )
    
    actions = recommend_corrective_actions(compliance)
    
    print(f"Ações Corretivas Recomendadas: {len(actions)}")
    for action in actions:
        print(f"\n{action.priority.value.upper()}: {action.title}")
        print(f"  Prazo: {action.deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Custo Estimado: R$ {action.estimated_cost_brl:,.2f}")
        print(f"  Duração: {action.estimated_duration_hours:.1f} horas")
        print(f"  Descrição: {action.description}")

