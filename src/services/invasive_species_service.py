"""
Serviço de Gestão de Espécies Invasoras - HullZero

Baseado em pesquisas sobre coral sol (Tubastraea coccinea) e outras espécies invasoras
que impactam a bioincrustação em embarcações.
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class InvasiveSpecies(Enum):
    """Espécies invasoras críticas no Brasil"""
    CORAL_SOL = "Tubastraea_coccinea"  # Coral sol
    MEXILHAO_DOURADO = "Limnoperna_fortunei"  # Mexilhão dourado
    CARAMUJO_AFRICANO = "Achatina_fulica"
    MEXILHAO_VERDE = "Perna_viridis"
    BARNAQUES = "Amphibalanus_amphitrite"


@dataclass
class InvasiveSpeciesRisk:
    """Risco de espécie invasora"""
    species: InvasiveSpecies
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    risk_score: float  # 0-1
    growth_rate_multiplier: float
    removal_difficulty: float  # 0-1, 1 = muito difícil
    regions_affected: List[str]
    seasonal_factors: Dict[str, float]  # Fatores sazonais
    recommendations: List[str]


class InvasiveSpeciesService:
    """
    Serviço para gestão de espécies invasoras baseado em pesquisas científicas.
    
    Referências:
    - Coral Sol (Tubastraea coccinea): Espécie invasora crítica no Brasil
    - NORMAM 23: Gestão de espécies invasoras
    - IBAMA: Relatórios sobre bioincrustação e espécies invasoras
    """
    
    # Dados baseados em pesquisas científicas e dados reais
    SPECIES_DATA = {
        InvasiveSpecies.CORAL_SOL: {
            "scientific_name": "Tubastraea coccinea",
            "common_name": "Coral Sol",
            "growth_rate_multiplier": 1.5,  # 50% mais rápido que espécies nativas
            "removal_difficulty": 0.9,  # Muito difícil de remover
            "regions": ["Brazil_Coast", "South_Atlantic", "Tropical", "Offshore"],
            "temperature_range": (20.0, 30.0),  # °C
            "salinity_range": (30.0, 38.0),  # PSU
            "depth_range": (0.0, 50.0),  # metros
            "seasonal_factors": {
                "summer": 1.4,  # Maior crescimento no verão
                "spring": 1.2,
                "autumn": 1.0,
                "winter": 0.8
            },
            "impact_description": (
                "Coral sol (Tubastraea coccinea) é uma das espécies invasoras mais problemáticas "
                "no Brasil, especialmente na costa brasileira. Forma colônias densas que são "
                "extremamente difíceis de remover e podem aumentar significativamente o arrasto "
                "hidrodinâmico em até 40%. Espécie originária do Indo-Pacífico, introduzida no "
                "Brasil através de plataformas de petróleo e cascos de navios."
            ),
            "control_methods": [
                "Limpeza mecânica especializada (escovas de aço)",
                "Hidrojateamento de alta pressão (500+ bar)",
                "Aplicação de revestimentos anti-incrustantes específicos",
                "Monitoramento intensificado em áreas de risco"
            ],
            "biological_control": {
                "natural_predators": [
                    "Esponjas predadoras (Cliona spp.) - em desenvolvimento",
                    "Peixes herbívoros nativos (Scarus spp., Sparisoma spp.) - eficácia limitada",
                    "Ouriços-do-mar (Diadema antillarum) - estudos em andamento"
                ],
                "innovative_methods": [
                    "Aplicação de extratos de macrófitas aquáticas (Egeria densa, Myriophyllum spicatum) - inibe crescimento larval",
                    "Uso de bactérias probióticas específicas que competem por espaço",
                    "Sistema de barreira elétrica de baixa voltagem (em teste)",
                    "Aplicação de revestimentos com nanopartículas de cobre orgânico (menos tóxico)"
                ],
                "no_downtime_methods": [
                    "Limpeza subaquática com robôs autônomos durante operação normal",
                    "Sistema de jato de água pressurizado acoplado ao casco (limpeza contínua)",
                    "Aplicação de revestimentos auto-limpantes com microestruturas",
                    "Monitoramento com sensores IoT e limpeza preventiva em portos"
                ],
                "environmental_impact": "Baixo - métodos biológicos não utilizam produtos químicos tóxicos"
            },
            "real_data": {
                "first_record_brazil": "1980s (plataformas de petróleo)",
                "current_distribution": "Costa brasileira de Santa Catarina ao Espírito Santo",
                "growth_rate": "Até 2 cm/ano em condições ideais",
                "colony_density": "Até 100 colônias/m² em áreas afetadas",
                "economic_impact": "Milhões de R$ em custos de limpeza e perda de eficiência"
            }
        },
        InvasiveSpecies.MEXILHAO_DOURADO: {
            "scientific_name": "Limnoperna fortunei",
            "common_name": "Mexilhão Dourado",
            "growth_rate_multiplier": 1.3,
            "removal_difficulty": 0.7,
            "regions": ["Inland_Waterways", "Estuaries", "Freshwater"],
            "temperature_range": (15.0, 28.0),
            "salinity_range": (0.0, 5.0),
            "depth_range": (0.0, 30.0),
            "seasonal_factors": {
                "summer": 1.3,
                "spring": 1.1,
                "autumn": 1.0,
                "winter": 0.7
            },
            "impact_description": (
                "Mexilhão dourado (Limnoperna fortunei) é uma espécie invasora originária da Ásia, "
                "introduzida no Brasil através da água de lastro de navios. Forma colônias extremamente "
                "densas (até 150.000 indivíduos/m²) em sistemas de água doce, causando entupimento de "
                "sistemas de refrigeração, aumento de arrasto e corrosão acelerada. Presente em toda a "
                "Bacia do Prata e expandindo para outras bacias hidrográficas."
            ),
            "control_methods": [
                "Limpeza preventiva em intervalos curtos (30-45 dias)",
                "Tratamento térmico (água quente >40°C por 10 minutos)",
                "Filtros em sistemas de captação de água (malha <200μm)",
                "Cloração controlada em sistemas fechados"
            ],
            "biological_control": {
                "natural_predators": [
                    "Peixes nativos: Dourado (Salminus brasiliensis), Pintado (Pseudoplatystoma corruscans)",
                    "Caranguejos nativos (Trichodactylus spp.) - predação de juvenis",
                    "Aves aquáticas (Biguás, Garças) - predação ocasional"
                ],
                "innovative_methods": [
                    "Uso de extratos de plantas nativas (Eichhornia crassipes) que inibem fixação larval",
                    "Aplicação de quitosana (derivado de crustáceos) - biodegradável e eficaz",
                    "Sistema de choque térmico controlado (sem produtos químicos)",
                    "Barreiras físicas com revestimentos naturais (cera de carnaúba)"
                ],
                "no_downtime_methods": [
                    "Sistema de filtragem em linha com auto-limpeza (backwash automático)",
                    "Tratamento térmico em circuito fechado durante operação",
                    "Aplicação de revestimentos anti-adesão em sistemas de captação",
                    "Monitoramento com sensores de biofouling e alertas preventivos"
                ],
                "environmental_impact": "Muito baixo - métodos biológicos e físicos não afetam ecossistema"
            },
            "real_data": {
                "first_record_brazil": "1998 (Rio Grande do Sul)",
                "current_distribution": "Bacia do Prata, expandindo para outras bacias",
                "growth_rate": "Até 1 cm/mês em condições ideais",
                "reproduction": "Até 1 milhão de larvas/indivíduo/ano",
                "economic_impact": "Centenas de milhões de R$ em danos a infraestrutura"
            }
        },
        InvasiveSpecies.MEXILHAO_VERDE: {
            "scientific_name": "Perna viridis",
            "common_name": "Mexilhão Verde",
            "growth_rate_multiplier": 1.2,
            "removal_difficulty": 0.6,
            "regions": ["Tropical", "Brazil_Coast", "South_Atlantic"],
            "temperature_range": (22.0, 32.0),
            "salinity_range": (28.0, 38.0),
            "depth_range": (0.0, 20.0),
            "seasonal_factors": {
                "summer": 1.2,
                "spring": 1.1,
                "autumn": 1.0,
                "winter": 0.9
            },
            "impact_description": (
                "Mexilhão verde (Perna viridis) é uma espécie invasora originária do Indo-Pacífico, "
                "introduzida no Brasil através de água de lastro. Forma colônias densas em cascos de "
                "navios, estruturas portuárias e plataformas, aumentando arrasto hidrodinâmico e "
                "consumo de combustível. Presente principalmente em águas tropicais e subtropicais."
            ),
            "control_methods": [
                "Limpeza mecânica regular (a cada 60-90 dias)",
                "Revestimentos anti-incrustantes (AFS - Anti-Fouling Systems)",
                "Hidrojateamento de média pressão (300-400 bar)",
                "Tratamento térmico em docagem"
            ],
            "biological_control": {
                "natural_predators": [
                    "Estrelas-do-mar (Asterias spp.) - predação eficaz",
                    "Caranguejos (Callinectes spp.) - predação de juvenis",
                    "Peixes herbívoros (Sparidae, Labridae) - predação limitada"
                ],
                "innovative_methods": [
                    "Aplicação de extratos de algas marinhas (Ulva spp.) que inibem fixação",
                    "Uso de probióticos marinhos que competem por espaço e nutrientes",
                    "Revestimentos com microestruturas biomiméticas (inspiradas em pele de tubarão)",
                    "Sistema de ultrassom de baixa frequência (inibe fixação larval)"
                ],
                "no_downtime_methods": [
                    "Limpeza subaquática com mergulhadores durante atracação",
                    "Sistema de limpeza contínua com escovas rotativas acopladas",
                    "Aplicação de revestimentos auto-limpantes com liberação controlada",
                    "Monitoramento com câmeras subaquáticas e limpeza preventiva"
                ],
                "environmental_impact": "Baixo - métodos biológicos são sustentáveis e não tóxicos"
            },
            "real_data": {
                "first_record_brazil": "1990s (portos do Sudeste)",
                "current_distribution": "Costa brasileira, principalmente Sudeste e Nordeste",
                "growth_rate": "Até 1.5 cm/mês em condições ideais",
                "colony_density": "Até 50.000 indivíduos/m²",
                "economic_impact": "Milhões de R$ em custos de manutenção e perda de eficiência"
            }
        },
        InvasiveSpecies.BARNAQUES: {
            "scientific_name": "Amphibalanus amphitrite",
            "common_name": "Craca ou Cracas",
            "growth_rate_multiplier": 1.4,
            "removal_difficulty": 0.8,
            "regions": ["Brazil_Coast", "South_Atlantic", "Tropical", "Offshore"],
            "temperature_range": (18.0, 30.0),
            "salinity_range": (25.0, 38.0),
            "depth_range": (0.0, 40.0),
            "seasonal_factors": {
                "summer": 1.3,
                "spring": 1.2,
                "autumn": 1.0,
                "winter": 0.8
            },
            "impact_description": (
                "Cracas (Amphibalanus amphitrite) são crustáceos sésseis que formam colônias densas "
                "em cascos de navios, estruturas portuárias e plataformas. Aumentam significativamente "
                "o arrasto hidrodinâmico e podem causar corrosão acelerada. Espécie cosmopolita presente "
                "em todos os oceanos."
            ),
            "control_methods": [
                "Limpeza mecânica com raspadores especializados",
                "Hidrojateamento de alta pressão (400+ bar)",
                "Revestimentos anti-incrustantes com biocidas seletivos",
                "Tratamento térmico (água >50°C)"
            ],
            "biological_control": {
                "natural_predators": [
                    "Caranguejos (Pachygrapsus spp., Grapsus spp.) - predação eficaz",
                    "Peixes (Labridae, Blenniidae) - predação de adultos",
                    "Estrelas-do-mar (Asterias spp.) - predação ocasional"
                ],
                "innovative_methods": [
                    "Aplicação de extratos de esponjas marinhas que inibem fixação larval",
                    "Uso de enzimas específicas (barnacidas) que degradam cimento das cracas",
                    "Revestimentos com nanopartículas de sílica que impedem adesão",
                    "Sistema de campo elétrico de baixa intensidade (em desenvolvimento)"
                ],
                "no_downtime_methods": [
                    "Limpeza subaquática com robôs durante atracação",
                    "Sistema de limpeza contínua com escovas rotativas",
                    "Aplicação de revestimentos com liberação controlada de enzimas",
                    "Monitoramento com sensores e limpeza preventiva programada"
                ],
                "environmental_impact": "Muito baixo - métodos biológicos são não tóxicos"
            },
            "real_data": {
                "first_record_brazil": "Histórico (espécie cosmopolita)",
                "current_distribution": "Toda a costa brasileira",
                "growth_rate": "Até 1 cm/mês em condições ideais",
                "colony_density": "Até 200.000 indivíduos/m²",
                "economic_impact": "Bilhões de R$ globalmente em custos de manutenção"
            }
        }
    }
    
    def assess_risk(
        self,
        route_region: str,
        water_temperature_c: float,
        salinity_psu: float,
        depth_m: float,
        seasonal_factor: Optional[str] = None
    ) -> List[InvasiveSpeciesRisk]:
        """
        Avalia risco de espécies invasoras para uma embarcação.
        
        Args:
            route_region: Região de operação
            water_temperature_c: Temperatura da água
            salinity_psu: Salinidade
            depth_m: Profundidade
            seasonal_factor: Fator sazonal
            
        Returns:
            Lista de riscos por espécie
        """
        risks = []
        
        for species, data in self.SPECIES_DATA.items():
            # Verificar se região está na lista de risco
            if route_region not in data["regions"]:
                continue
            
            # Verificar condições ambientais
            temp_ok = data["temperature_range"][0] <= water_temperature_c <= data["temperature_range"][1]
            sal_ok = data["salinity_range"][0] <= salinity_psu <= data["salinity_range"][1]
            depth_ok = data["depth_range"][0] <= depth_m <= data["depth_range"][1]
            
            if not (temp_ok and sal_ok and depth_ok):
                continue  # Condições não adequadas
            
            # Calcular risco
            risk_score = 0.5  # Base
            
            # Ajuste por temperatura (ótimo = maior risco)
            temp_optimum = (data["temperature_range"][0] + data["temperature_range"][1]) / 2
            temp_factor = 1.0 - abs(water_temperature_c - temp_optimum) / (temp_optimum * 0.3)
            risk_score += temp_factor * 0.2
            
            # Ajuste sazonal
            if seasonal_factor:
                seasonal_mult = data["seasonal_factors"].get(seasonal_factor, 1.0)
                risk_score *= seasonal_mult
            
            # Normalizar
            risk_score = min(1.0, risk_score)
            
            # Determinar nível
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            risks.append(InvasiveSpeciesRisk(
                species=species,
                risk_level=risk_level,
                risk_score=risk_score,
                growth_rate_multiplier=data["growth_rate_multiplier"],
                removal_difficulty=data["removal_difficulty"],
                regions_affected=data["regions"],
                seasonal_factors=data["seasonal_factors"],
                recommendations=data["control_methods"]
            ))
        
        # Ordenar por risco
        risks.sort(key=lambda x: x.risk_score, reverse=True)
        
        return risks
    
    def get_species_info(self, species: InvasiveSpecies) -> Dict:
        """Retorna informações detalhadas sobre uma espécie"""
        return self.SPECIES_DATA.get(species, {}).copy()
    
    def get_prevention_recommendations(
        self,
        risks: List[InvasiveSpeciesRisk]
    ) -> List[str]:
        """Gera recomendações de prevenção baseadas nos riscos"""
        recommendations = []
        
        critical_risks = [r for r in risks if r.risk_level == "critical"]
        high_risks = [r for r in risks if r.risk_level == "high"]
        
        if critical_risks:
            recommendations.append(
                f"⚠️ RISCO CRÍTICO: {len(critical_risks)} espécie(s) invasora(s) "
                "com alto risco de colonização detectado(s)."
            )
            for risk in critical_risks:
                species_name = risk.species.value.replace("_", " ").title()
                recommendations.append(
                    f"  • {species_name}: {risk.risk_score:.0%} de risco. "
                    f"Recomenda-se limpeza preventiva a cada 30-45 dias."
                )
        
        if high_risks:
            recommendations.append(
                f"🔶 RISCO ALTO: {len(high_risks)} espécie(s) com risco elevado."
            )
        
        # Recomendações gerais
        if risks:
            recommendations.append(
                "📋 Ações Recomendadas:"
            )
            recommendations.append(
                "  1. Aumentar frequência de inspeções para mensal"
            )
            recommendations.append(
                "  2. Considerar limpeza preventiva antes de entrar em áreas de alto risco"
            )
            recommendations.append(
                "  3. Usar revestimentos anti-incrustantes específicos para espécies invasoras"
            )
            recommendations.append(
                "  4. Documentar presença de espécies invasoras conforme NORMAM 23"
            )
        
        return recommendations


# Função de conveniência
def assess_invasive_species_risk(
    route_region: str,
    water_temperature_c: float,
    salinity_psu: float,
    depth_m: float = 20.0,
    seasonal_factor: Optional[str] = None
) -> List[InvasiveSpeciesRisk]:
    """
    Avalia risco de espécies invasoras.
    
    Args:
        route_region: Região de operação
        water_temperature_c: Temperatura da água
        salinity_psu: Salinidade
        depth_m: Profundidade
        seasonal_factor: Fator sazonal
        
    Returns:
        Lista de riscos
    """
    service = InvasiveSpeciesService()
    return service.assess_risk(
        route_region,
        water_temperature_c,
        salinity_psu,
        depth_m,
        seasonal_factor
    )

