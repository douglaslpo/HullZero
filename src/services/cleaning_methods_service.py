"""
Serviço de Métodos de Remoção de Bioincrustação - HullZero

Este módulo implementa recomendações de métodos de limpeza baseados em
características da embarcação, nível de bioincrustação e requisitos NORMAM 401.
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class CleaningMethod(Enum):
    """Métodos de limpeza disponíveis"""
    BRUSH_CLEANING = "brush_cleaning"
    WATER_JETTING = "water_jetting"
    CAVITATION = "cavitation"
    BLASTING = "blasting"
    UNDERWATER_CLEANING = "underwater_cleaning"
    DRY_DOCK_CLEANING = "dry_dock_cleaning"
    ROBOTIC_CLEANING = "robotic_cleaning"
    ULTRASONIC_CLEANING = "ultrasonic_cleaning"


class CleaningSeverity(Enum):
    """Severidade da limpeza necessária"""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CRITICAL = "critical"


@dataclass
class CleaningMethodInfo:
    """Informações sobre um método de limpeza"""
    method: CleaningMethod
    name: str
    description: str
    effectiveness: float  # 0-1
    cost_per_m2: float  # R$/m²
    duration_hours: float  # Horas por 1000 m²
    environmental_impact: str  # 'low', 'medium', 'high'
    suitable_for_thickness: tuple  # (min_mm, max_mm)
    suitable_for_vessel_types: List[str]
    pros: List[str]
    cons: List[str]
    normam_compliance: bool


@dataclass
class CleaningRecommendation:
    """Recomendação de método de limpeza"""
    vessel_id: str
    recommended_method: CleaningMethod
    alternative_methods: List[CleaningMethod]
    severity: CleaningSeverity
    estimated_cost_brl: float
    estimated_duration_hours: float
    effectiveness_score: float
    environmental_impact: str
    normam_compliant: bool
    reasoning: str
    steps: List[str]
    post_cleaning_requirements: List[str]


class CleaningMethodsService:
    """
    Serviço que recomenda métodos de limpeza baseado em características
    da embarcação e nível de bioincrustação.
    """
    
    # Base de conhecimento de métodos
    METHODS_DATABASE = {
        CleaningMethod.BRUSH_CLEANING: CleaningMethodInfo(
            method=CleaningMethod.BRUSH_CLEANING,
            name="Limpeza com Escova Rotativa",
            description="Limpeza mecânica com escovas rotativas, adequada para bioincrustação leve a moderada",
            effectiveness=0.75,
            cost_per_m2=45.0,
            duration_hours=8.0,
            environmental_impact="low",
            suitable_for_thickness=(0.5, 3.0),
            suitable_for_vessel_types=["tanker", "cargo", "barge", "tug"],
            pros=[
                "Baixo custo",
                "Baixo impacto ambiental",
                "Pode ser feita em água (underwater)",
                "Rápida execução",
                "Não danifica a tinta anti-incrustante"
            ],
            cons=[
                "Eficácia limitada para bioincrustação pesada",
                "Pode não remover completamente cracas",
                "Requer mergulhadores qualificados"
            ],
            normam_compliance=True
        ),
        CleaningMethod.WATER_JETTING: CleaningMethodInfo(
            method=CleaningMethod.WATER_JETTING,
            name="Jateamento com Água de Alta Pressão",
            description="Remoção com jatos de água de alta pressão (200-500 bar)",
            effectiveness=0.85,
            cost_per_m2=65.0,
            duration_hours=6.0,
            environmental_impact="low",
            suitable_for_thickness=(1.0, 4.0),
            suitable_for_vessel_types=["tanker", "cargo", "container"],
            pros=[
                "Alta eficácia",
                "Baixo impacto ambiental",
                "Rápida execução",
                "Remove bioincrustação moderada a pesada",
                "Pode ser feita em água"
            ],
            cons=[
                "Custo médio-alto",
                "Requer equipamento especializado",
                "Pode danificar tinta se pressão muito alta"
            ],
            normam_compliance=True
        ),
        CleaningMethod.CAVITATION: CleaningMethodInfo(
            method=CleaningMethod.CAVITATION,
            name="Limpeza por Cavitação",
            description="Uso de cavitação ultrassônica para remover bioincrustação",
            effectiveness=0.90,
            cost_per_m2=85.0,
            duration_hours=5.0,
            environmental_impact="low",
            suitable_for_thickness=(1.5, 5.0),
            suitable_for_vessel_types=["tanker", "cargo", "container"],
            pros=[
                "Muito eficaz",
                "Não danifica a tinta",
                "Baixo impacto ambiental",
                "Remove até bioincrustação pesada",
                "Tecnologia inovadora"
            ],
            cons=[
                "Custo mais alto",
                "Requer equipamento especializado",
                "Disponibilidade limitada no Brasil"
            ],
            normam_compliance=True
        ),
        CleaningMethod.BLASTING: CleaningMethodInfo(
            method=CleaningMethod.BLASTING,
            name="Jateamento Abrasivo",
            description="Remoção com jateamento de partículas abrasivas (granalha, etc.)",
            effectiveness=0.95,
            cost_per_m2=120.0,
            duration_hours=12.0,
            environmental_impact="medium",
            suitable_for_thickness=(3.0, 10.0),
            suitable_for_vessel_types=["tanker", "cargo"],
            pros=[
                "Muito eficaz para bioincrustação pesada",
                "Remove completamente cracas e algas",
                "Prepara superfície para nova pintura"
            ],
            cons=[
                "Alto custo",
                "Requer docagem seca",
                "Impacto ambiental médio (resíduos)",
                "Remove tinta anti-incrustante",
                "Requer repintura após limpeza"
            ],
            normam_compliance=True
        ),
        CleaningMethod.UNDERWATER_CLEANING: CleaningMethodInfo(
            method=CleaningMethod.UNDERWATER_CLEANING,
            name="Limpeza Subaquática",
            description="Limpeza realizada por mergulhadores sem necessidade de docagem",
            effectiveness=0.70,
            cost_per_m2=55.0,
            duration_hours=10.0,
            environmental_impact="low",
            suitable_for_thickness=(0.5, 3.5),
            suitable_for_vessel_types=["tanker", "cargo", "barge", "tug"],
            pros=[
                "Não requer docagem",
                "Pode ser feita durante operação",
                "Reduz tempo fora de serviço",
                "Custo-benefício para limpezas preventivas"
            ],
            cons=[
                "Eficácia limitada para bioincrustação pesada",
                "Dependente de condições climáticas",
                "Requer mergulhadores qualificados"
            ],
            normam_compliance=True
        ),
        CleaningMethod.DRY_DOCK_CLEANING: CleaningMethodInfo(
            method=CleaningMethod.DRY_DOCK_CLEANING,
            name="Limpeza em Docagem Seca",
            description="Limpeza completa em doca seca com múltiplos métodos",
            effectiveness=0.98,
            cost_per_m2=150.0,
            duration_hours=48.0,
            environmental_impact="medium",
            suitable_for_thickness=(2.0, 15.0),
            suitable_for_vessel_types=["tanker", "cargo", "container"],
            pros=[
                "Máxima eficácia",
                "Permite inspeção completa",
                "Pode combinar múltiplos métodos",
                "Permite repintura se necessário"
            ],
            cons=[
                "Alto custo",
                "Embarcação fora de serviço",
                "Requer agendamento de doca",
                "Tempo de parada longo"
            ],
            normam_compliance=True
        ),
        CleaningMethod.ROBOTIC_CLEANING: CleaningMethodInfo(
            method=CleaningMethod.ROBOTIC_CLEANING,
            name="Limpeza Robótica",
            description="Limpeza automatizada com robôs subaquáticos",
            effectiveness=0.80,
            cost_per_m2=70.0,
            duration_hours=7.0,
            environmental_impact="low",
            suitable_for_thickness=(0.5, 4.0),
            suitable_for_vessel_types=["tanker", "cargo", "container"],
            pros=[
                "Tecnologia inovadora",
                "Consistência na limpeza",
                "Reduz necessidade de mergulhadores",
                "Pode ser feita em água"
            ],
            cons=[
                "Custo inicial alto",
                "Disponibilidade limitada",
                "Requer treinamento especializado",
                "Pode ter limitações em áreas complexas"
            ],
            normam_compliance=True
        ),
        CleaningMethod.ULTRASONIC_CLEANING: CleaningMethodInfo(
            method=CleaningMethod.ULTRASONIC_CLEANING,
            name="Limpeza Ultrassônica",
            description="Remoção com ondas ultrassônicas de alta frequência",
            effectiveness=0.88,
            cost_per_m2=90.0,
            duration_hours=6.5,
            environmental_impact="low",
            suitable_for_thickness=(1.0, 4.5),
            suitable_for_vessel_types=["tanker", "cargo"],
            pros=[
                "Alta eficácia",
                "Não danifica tinta",
                "Baixo impacto ambiental",
                "Tecnologia avançada"
            ],
            cons=[
                "Custo alto",
                "Equipamento especializado",
                "Disponibilidade limitada"
            ],
            normam_compliance=True
        )
    }
    
    def recommend_cleaning_method(
        self,
        vessel_id: str,
        fouling_thickness_mm: float,
        roughness_um: float,
        vessel_type: str,
        hull_area_m2: float,
        urgency: str = "normal",  # 'preventive', 'normal', 'urgent', 'critical'
        budget_constraint: Optional[float] = None,
        time_constraint: Optional[float] = None,
        prefer_underwater: bool = False
    ) -> CleaningRecommendation:
        """
        Recomenda método de limpeza baseado em características e restrições.
        
        Args:
            vessel_id: ID da embarcação
            fouling_thickness_mm: Espessura de bioincrustação (mm)
            roughness_um: Rugosidade (μm)
            vessel_type: Tipo de embarcação
            hull_area_m2: Área do casco (m²)
            urgency: Urgência da limpeza
            budget_constraint: Orçamento máximo (R$)
            time_constraint: Tempo máximo disponível (horas)
            prefer_underwater: Preferir métodos que podem ser feitos em água
            
        Returns:
            Recomendação de método de limpeza
        """
        # Determinar severidade
        severity = self._determine_severity(fouling_thickness_mm, roughness_um)
        
        # Filtrar métodos adequados
        suitable_methods = self._filter_suitable_methods(
            fouling_thickness_mm,
            vessel_type,
            urgency,
            prefer_underwater
        )
        
        if not suitable_methods:
            # Se nenhum método adequado, usar método mais eficaz disponível
            suitable_methods = [CleaningMethod.DRY_DOCK_CLEANING]
        
        # Ordenar por score de adequação
        method_scores = []
        for method in suitable_methods:
            method_info = self.METHODS_DATABASE[method]
            score = self._calculate_method_score(
                method_info,
                fouling_thickness_mm,
                vessel_type,
                urgency,
                budget_constraint,
                time_constraint,
                hull_area_m2
            )
            method_scores.append((method, method_info, score))
        
        # Ordenar por score (maior primeiro)
        method_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Método recomendado
        recommended_method, recommended_info, recommended_score = method_scores[0]
        
        # Métodos alternativos (top 3)
        alternative_methods = [m[0] for m in method_scores[1:4]]
        
        # Calcular custo e duração
        estimated_cost = recommended_info.cost_per_m2 * hull_area_m2
        estimated_duration = (recommended_info.duration_hours / 1000.0) * hull_area_m2
        
        # Gerar raciocínio
        reasoning = self._generate_reasoning(
            recommended_method,
            recommended_info,
            fouling_thickness_mm,
            severity,
            urgency
        )
        
        # Gerar passos
        steps = self._generate_cleaning_steps(recommended_method, severity)
        
        # Requisitos pós-limpeza
        post_requirements = self._generate_post_cleaning_requirements(
            recommended_method,
            fouling_thickness_mm
        )
        
        return CleaningRecommendation(
            vessel_id=vessel_id,
            recommended_method=recommended_method,
            alternative_methods=alternative_methods,
            severity=severity,
            estimated_cost_brl=estimated_cost,
            estimated_duration_hours=estimated_duration,
            effectiveness_score=recommended_info.effectiveness,
            environmental_impact=recommended_info.environmental_impact,
            normam_compliant=recommended_info.normam_compliance,
            reasoning=reasoning,
            steps=steps,
            post_cleaning_requirements=post_requirements
        )
    
    def _determine_severity(
        self,
        fouling_thickness_mm: float,
        roughness_um: float
    ) -> CleaningSeverity:
        """Determina severidade da limpeza necessária"""
        if fouling_thickness_mm >= 5.0 or roughness_um >= 500.0:
            return CleaningSeverity.CRITICAL
        elif fouling_thickness_mm >= 3.5 or roughness_um >= 400.0:
            return CleaningSeverity.HEAVY
        elif fouling_thickness_mm >= 2.0 or roughness_um >= 300.0:
            return CleaningSeverity.MODERATE
        else:
            return CleaningSeverity.LIGHT
    
    def _filter_suitable_methods(
        self,
        fouling_thickness_mm: float,
        vessel_type: str,
        urgency: str,
        prefer_underwater: bool
    ) -> List[CleaningMethod]:
        """Filtra métodos adequados às condições"""
        suitable = []
        
        for method, info in self.METHODS_DATABASE.items():
            # Verificar se espessura está no range adequado
            min_thick, max_thick = info.suitable_for_thickness
            if not (min_thick <= fouling_thickness_mm <= max_thick):
                continue
            
            # Verificar tipo de embarcação
            if vessel_type.lower() not in [vt.lower() for vt in info.suitable_for_vessel_types]:
                continue
            
            # Se preferir underwater, priorizar métodos que podem ser feitos em água
            if prefer_underwater and method in [
                CleaningMethod.DRY_DOCK_CLEANING,
                CleaningMethod.BLASTING
            ]:
                continue
            
            suitable.append(method)
        
        return suitable
    
    def _calculate_method_score(
        self,
        method_info: CleaningMethodInfo,
        fouling_thickness_mm: float,
        vessel_type: str,
        urgency: str,
        budget_constraint: Optional[float],
        time_constraint: Optional[float],
        hull_area_m2: float
    ) -> float:
        """Calcula score de adequação do método"""
        score = 0.0
        
        # Eficácia (40%)
        score += method_info.effectiveness * 0.4
        
        # Custo-benefício (25%)
        cost = method_info.cost_per_m2 * hull_area_m2
        if budget_constraint:
            if cost <= budget_constraint:
                score += 0.25
            else:
                score += max(0, 0.25 * (1 - (cost - budget_constraint) / budget_constraint))
        else:
            # Normalizar custo (assumindo range 0-200 R$/m²)
            cost_score = 1.0 - min(1.0, cost / (200.0 * hull_area_m2))
            score += cost_score * 0.25
        
        # Tempo (15%)
        duration = (method_info.duration_hours / 1000.0) * hull_area_m2
        if time_constraint:
            if duration <= time_constraint:
                score += 0.15
            else:
                score += max(0, 0.15 * (1 - (duration - time_constraint) / time_constraint))
        else:
            # Normalizar duração (assumindo range 0-72h)
            duration_score = 1.0 - min(1.0, duration / 72.0)
            score += duration_score * 0.15
        
        # Impacto ambiental (10%)
        env_scores = {"low": 1.0, "medium": 0.6, "high": 0.3}
        score += env_scores.get(method_info.environmental_impact, 0.5) * 0.1
        
        # Urgência (10%)
        if urgency == "critical" and method_info.effectiveness >= 0.9:
            score += 0.1
        elif urgency == "urgent" and method_info.effectiveness >= 0.8:
            score += 0.1
        elif urgency == "normal":
            score += 0.05
        else:
            score += 0.0
        
        return score
    
    def _generate_reasoning(
        self,
        method: CleaningMethod,
        method_info: CleaningMethodInfo,
        fouling_thickness_mm: float,
        severity: CleaningSeverity,
        urgency: str
    ) -> str:
        """Gera raciocínio para a recomendação"""
        reasoning = f"O método {method_info.name} foi recomendado porque:\n\n"
        
        reasoning += f"• Eficácia de {method_info.effectiveness:.0%} adequada para bioincrustação de {fouling_thickness_mm:.1f} mm\n"
        reasoning += f"• Severidade classificada como {severity.value}\n"
        
        if urgency == "critical":
            reasoning += "• Urgência crítica requer método de alta eficácia\n"
        
        if method_info.normam_compliance:
            reasoning += "• Em conformidade com NORMAM 401\n"
        
        if method_info.environmental_impact == "low":
            reasoning += "• Baixo impacto ambiental\n"
        
        return reasoning
    
    def _generate_cleaning_steps(
        self,
        method: CleaningMethod,
        severity: CleaningSeverity
    ) -> List[str]:
        """Gera passos do processo de limpeza"""
        steps = []
        
        if method == CleaningMethod.BRUSH_CLEANING:
            steps = [
                "1. Inspeção inicial do casco por mergulhador",
                "2. Posicionamento de equipamento de limpeza",
                "3. Limpeza com escovas rotativas (movimento sistemático)",
                "4. Remoção de resíduos com aspirador subaquático",
                "5. Inspeção final e verificação de conformidade",
                "6. Documentação e registro fotográfico"
            ]
        elif method == CleaningMethod.WATER_JETTING:
            steps = [
                "1. Preparação e posicionamento de equipamento de alta pressão",
                "2. Teste de pressão e segurança",
                "3. Jateamento sistemático do casco (de cima para baixo)",
                "4. Remoção de resíduos soltos",
                "5. Inspeção de áreas críticas",
                "6. Verificação de conformidade NORMAM 401",
                "7. Documentação completa"
            ]
        elif method == CleaningMethod.DRY_DOCK_CLEANING:
            steps = [
                "1. Agendamento e preparação da doca",
                "2. Docagem da embarcação",
                "3. Inspeção completa do casco",
                "4. Seleção de método de limpeza (pode combinar métodos)",
                "5. Execução da limpeza",
                "6. Inspeção pós-limpeza",
                "7. Repintura se necessário",
                "8. Verificação de conformidade",
                "9. Lançamento e testes"
            ]
        else:
            steps = [
                "1. Preparação e inspeção inicial",
                "2. Execução do método de limpeza",
                "3. Remoção de resíduos",
                "4. Inspeção final",
                "5. Verificação de conformidade NORMAM 401",
                "6. Documentação"
            ]
        
        return steps
    
    def _generate_post_cleaning_requirements(
        self,
        method: CleaningMethod,
        fouling_thickness_mm: float
    ) -> List[str]:
        """Gera requisitos pós-limpeza"""
        requirements = [
            "Medição de espessura e rugosidade pós-limpeza",
            "Verificação de conformidade com NORMAM 401",
            "Registro fotográfico do casco limpo",
            "Atualização do registro de sistema anti-incrustante"
        ]
        
        if method == CleaningMethod.BLASTING:
            requirements.append("Repintura obrigatória do casco")
            requirements.append("Aplicação de nova tinta anti-incrustante certificada")
        
        if fouling_thickness_mm >= 4.0:
            requirements.append("Inspeção adicional após 30 dias")
            requirements.append("Monitoramento intensificado nos próximos 90 dias")
        
        return requirements
    
    def get_method_info(self, method: CleaningMethod) -> CleaningMethodInfo:
        """Retorna informações detalhadas sobre um método"""
        return self.METHODS_DATABASE.get(method)


# Função de conveniência
def recommend_cleaning_method(
    vessel_id: str,
    fouling_thickness_mm: float,
    roughness_um: float,
    vessel_type: str,
    hull_area_m2: float,
    **kwargs
) -> CleaningRecommendation:
    """
    Recomenda método de limpeza.
    
    Args:
        vessel_id: ID da embarcação
        fouling_thickness_mm: Espessura de bioincrustação
        roughness_um: Rugosidade
        vessel_type: Tipo de embarcação
        hull_area_m2: Área do casco
        **kwargs: Argumentos adicionais (urgency, budget_constraint, etc.)
        
    Returns:
        Recomendação de método de limpeza
    """
    service = CleaningMethodsService()
    return service.recommend_cleaning_method(
        vessel_id,
        fouling_thickness_mm,
        roughness_um,
        vessel_type,
        hull_area_m2,
        **kwargs
    )

