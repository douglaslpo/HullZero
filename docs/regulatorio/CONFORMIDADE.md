# Sistema de Conformidade NORMAM 401 - HullZero

## 1. Visão Geral

O sistema de conformidade do HullZero implementa verificação automática e contínua dos requisitos da NORMAM 401, fornecendo monitoramento em tempo real, alertas preventivos e documentação completa para todas as embarcações da frota.

## 2. Arquitetura do Sistema

### 2.1 Componentes Principais

**Serviço de Conformidade (`NORMAM401ComplianceService`):**
- Verificação de limites de espessura e rugosidade
- Classificação de status de conformidade
- Geração de recomendações
- Cálculo de scores de conformidade

**Repositório de Verificações (`ComplianceCheckRepository`):**
- Persistência de verificações de conformidade
- Histórico completo de verificações
- Rastreabilidade de mudanças

**Modelos de Predição:**
- Predição de risco de não conformidade (15 e 30 dias)
- Otimização de inspeções
- Detecção de anomalias

**API de Conformidade:**
- Endpoints REST para verificação
- Histórico de verificações
- Relatórios de conformidade

### 2.2 Fluxo de Verificação

```
1. Coleta de Dados
   ↓
2. Verificação de Limites
   ↓
3. Classificação de Status
   ↓
4. Geração de Recomendações
   ↓
5. Persistência de Resultados
   ↓
6. Notificações e Alertas
```

## 3. Limites e Classificações

### 3.1 Limites por Tipo de Embarcação

| Tipo | Espessura Máx. (mm) | Rugosidade Máx. (μm) |
|------|---------------------|---------------------|
| Petroleiro | 5.0 | 500 |
| Cargueiro | 5.0 | 500 |
| Porta-Contêineres | 4.5 | 450 |
| Rebocador | 6.0 | 600 |
| Barcaça | 6.0 | 600 |
| Padrão | 5.0 | 500 |

### 3.2 Zonas de Classificação

**Zona Verde (COMPLIANT):**
- Espessura: 0 - 80% do limite
- Rugosidade: 0 - 80% do limite
- Status: Conforme
- Ação: Manter monitoramento regular

**Zona Amarela (AT_RISK):**
- Espessura: 80% - 100% do limite
- Rugosidade: 80% - 100% do limite
- Status: Em risco
- Ação: Monitoramento mais frequente, ações preventivas

**Zona Laranja (NON_COMPLIANT):**
- Inspeção fora do prazo (> 90 dias)
- Status: Não conforme
- Ação: Inspeção imediata requerida

**Zona Vermelha (CRITICAL):**
- Espessura > limite máximo
- Rugosidade > limite máximo
- Status: Crítico
- Ação: Ação imediata obrigatória, limpeza urgente

### 3.3 Cálculo de Score

O score de conformidade varia de 0 a 1, onde:
- 1.0 = Totalmente conforme
- 0.8 - 0.99 = Em risco
- 0.5 - 0.79 = Não conforme
- < 0.5 = Crítico

**Fórmula:**
```
score_espessura = max(0, 1 - (espessura_atual / limite_máximo))
score_rugosidade = max(0, 1 - (rugosidade_atual / limite_máximo))
score_final = (score_espessura × 0.6) + (score_rugosidade × 0.4)
```

## 4. Verificação de Conformidade

### 4.1 Verificação Automática

O sistema realiza verificação automática quando:
- Nova medição de bioincrustação é registrada
- Dados operacionais são atualizados
- Período desde última inspeção excede 90 dias
- Solicitação manual via API

### 4.2 Processo de Verificação

```python
def verify_compliance(vessel_id, fouling_data):
    # 1. Obtém limites para tipo de embarcação
    limits = get_limits(vessel_id)
    
    # 2. Verifica violações
    violations = []
    if fouling_data.thickness > limits.max_thickness:
        violations.append("Espessura excede limite")
    if fouling_data.roughness > limits.max_roughness:
        violations.append("Rugosidade excede limite")
    
    # 3. Verifica frequência de inspeção
    last_inspection = get_last_inspection(vessel_id)
    if days_since(last_inspection) > 90:
        violations.append("Inspeção fora do prazo")
    
    # 4. Classifica status
    if any("excede limite" in v for v in violations):
        status = ComplianceStatus.CRITICAL
    elif violations:
        status = ComplianceStatus.NON_COMPLIANT
    elif in_warning_zone(fouling_data, limits):
        status = ComplianceStatus.AT_RISK
    else:
        status = ComplianceStatus.COMPLIANT
    
    # 5. Calcula score
    score = calculate_compliance_score(fouling_data, limits)
    
    # 6. Gera recomendações
    recommendations = generate_recommendations(status, violations)
    
    # 7. Persiste resultado
    save_compliance_check(vessel_id, status, score, violations, recommendations)
    
    return ComplianceCheck(status, score, violations, recommendations)
```

## 5. Predição de Riscos

### 5.1 Predição de Risco NORMAM 401

O sistema utiliza modelos de IA para prever:
- Probabilidade de exceder limites em 15 dias
- Probabilidade de exceder limites em 30 dias
- Fatores de risco identificados
- Momento ótimo para intervenção

### 5.2 Fatores de Risco

Fatores considerados na predição:
- Espessura atual de bioincrustação
- Rugosidade atual
- Taxa de crescimento histórica
- Condições ambientais (temperatura, salinidade)
- Tempo desde última limpeza
- Tipo de tinta anti-incrustante
- Região de operação
- Tempo em portos

### 5.3 Alertas Preventivos

O sistema gera alertas quando:
- Risco de não conformidade em 15 dias > 50%
- Risco de não conformidade em 30 dias > 70%
- Tendência de crescimento acelerado detectada
- Múltiplos fatores de risco presentes

## 6. Recomendações de Ações Corretivas

### 6.1 Tipos de Recomendações

**Limpeza Imediata:**
- Quando status é CRITICAL
- Quando excede limites
- Prioridade: URGENTE

**Limpeza Programada:**
- Quando em zona de risco
- Quando risco previsto em 15-30 dias
- Prioridade: ALTA

**Inspeção Adicional:**
- Quando próximo dos limites
- Quando múltiplos fatores de risco
- Prioridade: MÉDIA

**Monitoramento Intensificado:**
- Quando em zona de alerta
- Quando condições ambientais favoráveis ao crescimento
- Prioridade: BAIXA

### 6.2 Análise de Custo-Benefício

As recomendações incluem análise de:
- Custo da intervenção
- Benefício esperado (redução de consumo, conformidade)
- Impacto operacional (tempo de parada)
- ROI da ação recomendada

## 7. Relatórios e Documentação

### 7.1 Relatórios por Embarcação

Cada verificação gera relatório contendo:
- Status de conformidade atual
- Medições de espessura e rugosidade
- Comparação com limites
- Histórico de verificações
- Violações identificadas
- Recomendações de ações

### 7.2 Relatórios Consolidados

Relatórios consolidados da frota incluem:
- Taxa de conformidade geral
- Distribuição de status
- Embarcações em risco
- Tendências de conformidade
- Resumo de violações
- Recomendações gerais

### 7.3 Exportação

Relatórios podem ser exportados em:
- CSV (para análise em planilhas)
- Excel (formatação completa)
- PDF (para documentação oficial)

## 8. Integração com Inspeções

### 8.1 Otimização de Inspeções

O sistema otimiza o agendamento de inspeções:
- Prioriza embarcações em risco
- Agrupa inspeções por região
- Minimiza impacto operacional
- Garante conformidade com frequência mínima

### 8.2 Registro de Inspeções

Cada inspeção é registrada com:
- Data e hora
- Inspetor responsável
- Medições realizadas
- Métodos utilizados
- Resultados
- Ações tomadas

## 9. Alertas e Notificações

### 9.1 Tipos de Alertas

**Crítico:**
- Excede limites
- Requer ação imediata
- Notificação imediata

**Alto Risco:**
- Próximo dos limites
- Risco previsto em 15 dias
- Notificação diária

**Médio Risco:**
- Em zona de alerta
- Risco previsto em 30 dias
- Notificação semanal

**Informativo:**
- Mudanças de status
- Atualizações de conformidade
- Notificação mensal

### 9.2 Canais de Notificação

- Dashboard da aplicação
- Email (configurável)
- API webhooks (para integração)
- Relatórios agendados

## 10. Auditoria e Rastreabilidade

### 10.1 Histórico Completo

O sistema mantém histórico de:
- Todas as verificações realizadas
- Mudanças de status
- Ações corretivas tomadas
- Resultados de inspeções
- Alterações em limites ou configurações

### 10.2 Logs de Auditoria

Logs de auditoria registram:
- Quem realizou verificação
- Quando foi realizada
- Dados utilizados
- Resultados obtidos
- Ações recomendadas

## 11. Conformidade com Outras Regulamentações

### 11.1 Padrões Internacionais

O sistema está preparado para:
- IMO Guidelines (International Maritime Organization)
- ISO 19030 (medição de performance)
- Padrões de classificação (DNV, ABS, etc.)

### 11.2 Expansibilidade

Arquitetura permite adicionar:
- Novas regulamentações
- Requisitos específicos por região
- Padrões de clientes
- Requisitos de certificação

## 12. Melhorias Contínuas

### 12.1 Aprendizado de Máquina

O sistema aprende com:
- Histórico de verificações
- Resultados de ações corretivas
- Padrões de não conformidade
- Eficácia de recomendações

### 12.2 Otimização

Melhorias contínuas em:
- Precisão de predições
- Relevância de recomendações
- Eficiência de alertas
- Usabilidade de relatórios

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


