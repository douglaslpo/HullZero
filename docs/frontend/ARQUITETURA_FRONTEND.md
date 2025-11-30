# Arquitetura Frontend - HullZero

## 1. Visão Geral

O frontend do HullZero é uma aplicação web moderna construída com React 18 e TypeScript, utilizando Vite como build tool e Chakra UI como biblioteca de componentes. A aplicação segue uma arquitetura baseada em componentes reutilizáveis, gerenciamento de estado com React Query e roteamento com React Router DOM.

## 2. Stack Tecnológico

### 2.1 Core

- **React 18.2.0**: Biblioteca principal para construção de interfaces
- **TypeScript 5.2.2**: Tipagem estática para maior segurança de código
- **Vite 5.0.8**: Build tool e dev server de alta performance

### 2.2 UI e Estilização

- **Chakra UI 2.8.2**: Biblioteca de componentes acessíveis e customizáveis
- **Emotion**: Sistema de estilização CSS-in-JS usado pelo Chakra UI
- **Framer Motion 10.16.16**: Animações e transições

### 2.3 Gerenciamento de Estado e Dados

- **React Query (TanStack Query) 5.12.2**: Gerenciamento de estado do servidor, cache e sincronização
- **Axios 1.6.2**: Cliente HTTP para comunicação com a API

### 2.4 Roteamento e Formulários

- **React Router DOM 6.20.0**: Roteamento declarativo
- **React Hook Form 7.48.2**: Gerenciamento de formulários performático

### 2.5 Visualização de Dados

- **Recharts 2.10.3**: Biblioteca de gráficos baseada em D3.js
- **date-fns 2.30.0**: Manipulação e formatação de datas

## 3. Estrutura de Diretórios

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # Configuração do cliente Axios
│   │   └── services.ts        # Serviços de API centralizados
│   ├── components/
│   │   ├── AdvancedPredictionCard.tsx
│   │   ├── ComplianceReport.tsx
│   │   ├── ContributionChart.tsx
│   │   ├── ExplanationModal.tsx
│   │   ├── KPICard.tsx
│   │   ├── TrendsChart.tsx
│   │   └── VesselCard.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── FleetManagement.tsx
│   │   ├── VesselDetails.tsx
│   │   ├── Compliance.tsx
│   │   ├── OperationalData.tsx
│   │   ├── Maintenance.tsx
│   │   ├── InvasiveSpecies.tsx
│   │   └── Recommendations.tsx
│   ├── App.tsx                # Componente raiz e roteamento
│   ├── main.tsx              # Ponto de entrada da aplicação
│   └── theme.ts              # Configuração do tema Chakra UI
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## 4. Arquitetura de Componentes

### 4.1 Padrão de Componentes

A aplicação segue o padrão de componentes funcionais com hooks:

```typescript
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, Heading } from '@chakra-ui/react'

function ComponentName() {
  const [state, setState] = useState()
  const { data, isLoading } = useQuery({
    queryKey: ['key'],
    queryFn: fetchFunction
  })
  
  return (
    <Box>
      {/* JSX */}
    </Box>
  )
}
```

### 4.2 Componentes Reutilizáveis

**KPICard**: Exibe indicadores-chave de performance com formatação automática
**TrendsChart**: Gráfico de tendências com múltiplas métricas selecionáveis
**VesselCard**: Card de embarcação com informações resumidas
**ComplianceReport**: Componente para geração de relatórios de conformidade
**ExplanationModal**: Modal para exibição de explicações de modelos de IA

### 4.3 Páginas Principais

**Dashboard**: Visão geral com KPIs e gráficos de tendências
**FleetManagement**: Gestão completa da frota com filtros e visualizações
**VesselDetails**: Detalhes completos de uma embarcação com múltiplas abas
**Compliance**: Análise de conformidade NORMAM 401
**OperationalData**: Visualização de dados operacionais em tempo real
**Maintenance**: Histórico e gestão de eventos de manutenção
**InvasiveSpecies**: Análise de risco de espécies invasoras
**Recommendations**: Recomendações de ações corretivas

## 5. Gerenciamento de Estado

### 5.1 React Query

React Query é usado para:
- Cache de dados do servidor
- Sincronização automática
- Gerenciamento de estados de loading e error
- Refetch automático e manual

**Configuração:**
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
    },
  },
})
```

### 5.2 Estado Local

Estado local é gerenciado com `useState` para:
- Filtros e seleções do usuário
- Estados de UI (modais, abas, etc.)
- Formulários temporários

### 5.3 Estado Global

Não há necessidade de estado global (Redux/Zustand) pois:
- React Query gerencia estado do servidor
- Estado local é suficiente para UI
- Comunicação entre componentes via props e contexto quando necessário

## 6. Comunicação com API

### 6.1 Cliente HTTP

O cliente Axios é configurado em `src/api/client.ts`:

```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### 6.2 Serviços Centralizados

Todos os serviços de API estão centralizados em `src/api/services.ts`:

- `dashboardService`: KPIs e tendências
- `vesselService`: CRUD de embarcações
- `foulingService`: Predições de bioincrustação
- `complianceService`: Verificações de conformidade
- `operationalDataService`: Dados operacionais
- `maintenanceService`: Eventos de manutenção
- `invasiveSpeciesService`: Análise de espécies invasoras
- `fleetManagementService`: Gestão de frota

### 6.3 Tratamento de Erros

Erros são tratados em múltiplos níveis:

1. **Interceptores Axios**: Tratamento global de erros HTTP
2. **React Query**: Retry automático e estados de error
3. **Componentes**: Exibição de mensagens de erro ao usuário

## 7. Roteamento

### 7.1 Estrutura de Rotas

```typescript
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/vessel/:id" element={<VesselDetails />} />
  <Route path="/fleet" element={<FleetManagement />} />
  <Route path="/compliance" element={<Compliance />} />
  <Route path="/operational-data" element={<OperationalData />} />
  <Route path="/maintenance" element={<Maintenance />} />
  <Route path="/invasive-species" element={<InvasiveSpecies />} />
  <Route path="/recommendations" element={<Recommendations />} />
</Routes>
```

### 7.2 Navegação

Navegação é feita via:
- Componente `Link` do React Router
- Hook `useNavigate` para navegação programática
- Hook `useParams` para parâmetros de rota

## 8. Visualização de Dados

### 8.1 Gráficos com Recharts

Recharts é usado para todos os gráficos:
- LineChart: Tendências temporais
- BarChart: Comparações categóricas
- PieChart: Distribuições
- AreaChart: Áreas acumuladas
- ScatterChart: Correlações
- ComposedChart: Múltiplos tipos combinados

### 8.2 Formatação de Dados

Dados são formatados antes da visualização:
- Números: `toLocaleString('pt-BR')`
- Moeda: `toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })`
- Datas: `date-fns` para formatação e manipulação

## 9. Acessibilidade

### 9.1 Chakra UI

Chakra UI fornece componentes acessíveis por padrão:
- Suporte a ARIA attributes
- Navegação por teclado
- Contraste de cores adequado
- Foco visível

### 9.2 Boas Práticas

- Uso de labels descritivos
- Mensagens de erro claras
- Estados de loading visíveis
- Feedback visual para ações

## 10. Performance

### 10.1 Otimizações

- **Code Splitting**: Rotas carregadas sob demanda
- **Lazy Loading**: Componentes pesados carregados quando necessário
- **Memoização**: `useMemo` e `useCallback` para cálculos custosos
- **React Query Cache**: Reduz requisições desnecessárias

### 10.2 Build e Deploy

Vite otimiza o build:
- Tree shaking automático
- Minificação de código
- Code splitting por rota
- Assets otimizados

## 11. Desenvolvimento

### 11.1 Scripts Disponíveis

```bash
npm run dev      # Servidor de desenvolvimento
npm run build    # Build de produção
npm run preview  # Preview do build
npm run lint     # Linter
```

### 11.2 Configuração de Desenvolvimento

- Hot Module Replacement (HMR) ativo
- Source maps para debugging
- TypeScript strict mode
- ESLint para qualidade de código

## 12. Testes

### 12.1 Estratégia de Testes

- Testes unitários de componentes (planejado)
- Testes de integração de serviços (planejado)
- Testes E2E com Playwright (planejado)

## 13. Manutenção e Extensibilidade

### 13.1 Adicionar Nova Página

1. Criar componente em `src/pages/`
2. Adicionar rota em `App.tsx`
3. Adicionar link no header (se necessário)
4. Criar serviços em `services.ts` (se necessário)

### 13.2 Adicionar Novo Componente

1. Criar componente em `src/components/`
2. Exportar do componente
3. Importar onde necessário
4. Documentar props e uso

### 13.3 Adicionar Novo Serviço de API

1. Adicionar função em `src/api/services.ts`
2. Definir interfaces TypeScript
3. Usar `apiClient` para requisições
4. Integrar com React Query nas páginas

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


