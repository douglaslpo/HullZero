# Documentação de Componentes - Frontend HullZero

## 1. Componentes de Interface

### 1.1 KPICard

Componente reutilizável para exibição de indicadores-chave de performance.

**Localização:** `src/components/KPICard.tsx`

**Props:**
```typescript
interface KPICardProps {
  label: string              // Rótulo do KPI
  value: string | number     // Valor a ser exibido
  helpText?: string          // Texto de ajuda opcional
  isLoading?: boolean        // Estado de carregamento
  colorScheme?: string       // Esquema de cores (Chakra UI)
  trend?: 'up' | 'down'      // Tendência (opcional)
}
```

**Uso:**
```typescript
<KPICard
  label="Economia Acumulada"
  value={2800000}
  helpText="Últimos 6 meses"
  colorScheme="green"
  isLoading={false}
/>
```

**Funcionalidades:**
- Formatação automática de números (milhares, milhões)
- Formatação de moeda para valores numéricos
- Formatação de porcentagem para valores < 1
- Indicador de tendência (seta para cima/baixo)
- Estado de loading com skeleton

### 1.2 TrendsChart

Componente para visualização de tendências temporais com múltiplas métricas.

**Localização:** `src/components/TrendsChart.tsx`

**Props:**
```typescript
interface TrendsChartProps {
  data: TrendDataPoint[]     // Array de pontos de dados
  isLoading?: boolean        // Estado de carregamento
}
```

**Interface TrendDataPoint:**
```typescript
interface TrendDataPoint {
  month: string
  economy_brl: number
  co2_tonnes: number
  compliance_rate_percent: number
  avg_fouling_mm: number
  avg_roughness_um: number
  monitored_vessels: number
  maintenance_events: number
}
```

**Funcionalidades:**
- Seleção de métricas via checkboxes
- Múltiplos eixos Y para diferentes escalas
- Tooltips informativos
- Responsivo e acessível
- Destaque visual quando apenas uma métrica está selecionada

### 1.3 VesselCard

Card para exibição resumida de informações de embarcação.

**Localização:** `src/components/VesselCard.tsx`

**Props:**
```typescript
interface VesselCardProps {
  vessel: Vessel
  onClick?: () => void
  showDetails?: boolean
}
```

**Funcionalidades:**
- Exibição de informações principais
- Badge de status
- Link para detalhes
- Responsivo

### 1.4 ComplianceReport

Componente para geração e exibição de relatórios de conformidade.

**Localização:** `src/components/ComplianceReport.tsx`

**Props:**
```typescript
interface ComplianceReportProps {
  fleetStatus: FleetDetailedStatus
  kpis?: KPIsResponse
  onClose?: () => void
}
```

**Funcionalidades:**
- Geração de relatório completo
- Formatação para impressão/PDF
- Seções: Resumo Executivo, Métricas, Status Detalhado, Alertas, Recomendações
- Estilização otimizada para impressão

### 1.5 ExplanationModal

Modal para exibição de explicações de modelos de IA.

**Localização:** `src/components/ExplanationModal.tsx`

**Props:**
```typescript
interface ExplanationModalProps {
  isOpen: boolean
  onClose: () => void
  explanation: PredictionExplanation
  type: 'fouling' | 'compliance'
}
```

**Funcionalidades:**
- Exibição de contribuições de features (SHAP values)
- Gráfico de contribuições
- Explicação em linguagem natural
- Score de confiança

### 1.6 ContributionChart

Gráfico de barras horizontal para exibir contribuições de features.

**Localização:** `src/components/ContributionChart.tsx`

**Props:**
```typescript
interface ContributionChartProps {
  contributions: FeatureContribution[]
  baseValue: number
  predictionValue: number
}
```

**Funcionalidades:**
- Barras coloridas (verde para positivo, vermelho para negativo)
- Tooltips com descrições
- Ordenação por magnitude
- Formatação de valores

### 1.7 AdvancedPredictionCard

Card para exibição de predições avançadas de bioincrustação.

**Localização:** `src/components/AdvancedPredictionCard.tsx`

**Props:**
```typescript
interface AdvancedPredictionCardProps {
  prediction: AdvancedFoulingPrediction
  isLoading?: boolean
}
```

**Funcionalidades:**
- Exibição de múltiplas métricas
- Comparação com predição básica
- Indicadores de confiança
- Breakdown de fatores contribuintes

## 2. Páginas

### 2.1 Dashboard

**Localização:** `src/pages/Dashboard.tsx`

**Funcionalidades:**
- Exibição de KPIs principais
- Gráfico de tendências interativo
- Status resumido da frota
- Links para páginas detalhadas

**Dados Exibidos:**
- Economia acumulada (R$)
- Redução de CO₂ (toneladas)
- Taxa de conformidade (%)
- Número de embarcações monitoradas

### 2.2 FleetManagement

**Localização:** `src/pages/FleetManagement.tsx`

**Funcionalidades:**
- Resumo da frota (KPIs)
- Cards detalhados por embarcação
- Filtros (nome, tipo, FR level)
- Alertas de manutenção crítica
- Links para detalhes de cada embarcação

**Informações por Embarcação:**
- Nível FR (Fouling Risk)
- Perda de performance (%)
- Última limpeza
- Última pintura
- Calibração de sensores
- Riscos 15/30 dias
- Alertas contextuais

### 2.3 VesselDetails

**Localização:** `src/pages/VesselDetails.tsx`

**Estrutura:**
- Aba "Visão Geral": Informações básicas e status atual
- Aba "Histórico": Gráficos de histórico de bioincrustação
- Aba "Predição Avançada": Predições com múltiplos modelos
- Aba "Conformidade NORMAM 401": Verificação de conformidade
- Aba "Manutenção": Histórico de manutenção
- Aba "Recomendações": Ações corretivas recomendadas

**Funcionalidades:**
- Carregamento de dados via React Query
- Fallback para dados mock quando necessário
- Explicabilidade de predições
- Exportação de dados

### 2.4 Compliance

**Localização:** `src/pages/Compliance.tsx`

**Funcionalidades:**
- KPIs de conformidade
- Tabela detalhada por embarcação
- Gráficos de distribuição
- Tendências de conformidade
- Documentação NORMAM 401
- Exportação (CSV, Excel, PDF)
- Modal de ações corretivas

**Seções:**
- Resumo de Conformidade
- Status Detalhado
- Tendências
- Documentação Regulatória
- Análise de Riscos

### 2.5 OperationalData

**Localização:** `src/pages/OperationalData.tsx`

**Funcionalidades:**
- Visualização de dados em tempo real
- 5 gráficos interativos:
  - Velocidade ao longo do tempo (Area Chart)
  - Consumo de combustível (Line Chart)
  - Potência do motor (Bar Chart)
  - Condições ambientais (Composed Chart)
  - Velocidade vs. Consumo (Scatter Chart)
- Estatísticas (média, min, max)
- Tabela de dados históricos
- Formulário para registro de novos dados
- Exportação CSV

### 2.6 Maintenance

**Localização:** `src/pages/Maintenance.tsx`

**Estrutura:**
- Aba "Visão Geral": Estatísticas e KPIs
- Aba "Gráficos": Visualizações interativas
- Aba "Histórico Detalhado": Tabela completa

**Gráficos:**
- Custo ao longo do tempo
- Distribuição por tipo
- Eficiência de limpeza
- Bioincrustação antes vs. depois

**Funcionalidades:**
- Filtros por tipo e data
- Estatísticas agregadas
- Visualizações interativas

### 2.7 InvasiveSpecies

**Localização:** `src/pages/InvasiveSpecies.tsx`

**Estrutura:**
- Aba "Visão Geral": Estatísticas e lista de riscos
- Aba "Análise Detalhada": Análise por espécie
- Aba "Métodos de Controle": Métodos biológicos e inovadores
- Aba "Dados Científicos": Dados reais e pesquisas

**Funcionalidades:**
- Seleção de embarcação
- Parâmetros de avaliação (região, temperatura, salinidade, etc.)
- Avaliação de risco por espécie
- Gráficos de risco e fatores sazonais
- Informações detalhadas sobre métodos de controle
- Dados científicos e impactos reais

### 2.8 Recommendations

**Localização:** `src/pages/Recommendations.tsx`

**Funcionalidades:**
- Lista de recomendações por embarcação
- Priorização (urgente, alta, média, baixa)
- Análise de custo-benefício
- Filtros e ordenação

## 3. Padrões de Desenvolvimento

### 3.1 Estrutura de Componente

```typescript
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, Heading } from '@chakra-ui/react'
import { service } from '../api/services'

function ComponentName() {
  const [state, setState] = useState()
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['key', dependencies],
    queryFn: () => service.method(),
    enabled: condition,
    refetchInterval: 60000,
  })
  
  if (isLoading) return <Spinner />
  if (error) return <Alert status="error">Erro ao carregar</Alert>
  
  return (
    <Box>
      {/* JSX */}
    </Box>
  )
}

export default ComponentName
```

### 3.2 Tratamento de Erros

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['key'],
  queryFn: async () => {
    try {
      return await service.method()
    } catch (error) {
      // Fallback ou tratamento
      return fallbackData
    }
  },
})
```

### 3.3 Formatação de Dados

```typescript
// Números
const formatted = value.toLocaleString('pt-BR')

// Moeda
const currency = value.toLocaleString('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

// Datas
import { format } from 'date-fns'
const date = format(new Date(dateString), 'dd/MM/yyyy')
```

## 4. Acessibilidade

### 4.1 Boas Práticas

- Uso de componentes semânticos do Chakra UI
- Labels descritivos em todos os inputs
- Mensagens de erro claras e acionáveis
- Contraste adequado de cores
- Navegação por teclado funcional

### 4.2 ARIA

Chakra UI adiciona automaticamente atributos ARIA quando necessário. Para casos especiais:

```typescript
<Box role="alert" aria-live="polite">
  Mensagem importante
</Box>
```

## 5. Performance

### 5.1 Otimizações Implementadas

- React Query cache reduz requisições
- Lazy loading de rotas
- Memoização de cálculos custosos
- Code splitting automático pelo Vite

### 5.2 Boas Práticas

- Evitar re-renders desnecessários
- Usar `useMemo` para cálculos pesados
- Usar `useCallback` para funções passadas como props
- Paginação de listas grandes

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


