# Mindmap - Mapeamento Mental da Aplicação HullZero

## 🗺️ Estrutura do Mindmap

```
                    HULLZERO
                        |
        ┌───────────────┼───────────────┐
        |               |               |
    FRONTEND        BACKEND         DADOS
        |               |               |
    ┌───┴───┐       ┌───┴───┐       ┌───┴───┐
    |       |       |       |       |       |
  React   UI     FastAPI  Services  DB    Models
```

## 📊 Mapa Mental Completo

### 🎨 FRONTEND
```
Frontend
├── Tecnologias
│   ├── React 18
│   ├── TypeScript
│   ├── Vite
│   └── Chakra UI
├── Estrutura
│   ├── Pages
│   │   ├── Dashboard
│   │   ├── Fleet Management
│   │   ├── Vessel Details
│   │   ├── Compliance
│   │   └── Recommendations
│   ├── Components
│   │   ├── KPICard
│   │   ├── TrendsChart
│   │   ├── VesselCard
│   │   └── ComplianceReport
│   └── API Services
│       ├── Auth Service
│       ├── Client
│       └── Services
└── Funcionalidades
    ├── Autenticação
    ├── Visualização de Dados
    ├── Gráficos e Dashboards
    └── Gestão de Frota
```

### ⚙️ BACKEND
```
Backend
├── API Layer
│   ├── Endpoints
│   │   ├── /api/auth/*
│   │   ├── /api/db/*
│   │   ├── /api/compliance/*
│   │   └── /api/vessels/*
│   └── Middleware
│       ├── CORS
│       ├── Authentication
│       └── Error Handling
├── Services
│   ├── Compliance Service
│   ├── Recommendation Service
│   ├── Economy Service
│   ├── CO2 Service
│   ├── Cleaning Methods Service
│   └── Invasive Species Service
├── Models (IA/ML)
│   ├── Fouling Prediction
│   ├── Fuel Impact
│   ├── NORMAM 401 Risk
│   ├── Inspection Optimizer
│   ├── Anomaly Detector
│   ├── Corrective Actions
│   └── Explainability
└── Auth System
    ├── JWT
    ├── RBAC
    ├── Roles (15)
    └── Permissions (24)
```

### 💾 DADOS
```
Dados
├── Banco de Dados
│   ├── SQLite (dev)
│   ├── PostgreSQL (prod)
│   └── SQLAlchemy ORM
├── Modelos
│   ├── Vessels
│   ├── Fouling Data
│   ├── Operational Data
│   ├── Maintenance
│   ├── Inspections
│   └── Users
├── Repositories
│   ├── VesselRepository
│   ├── FoulingRepository
│   └── ...
└── Migrations
    ├── Reference Tables
    ├── New Entities
    └── Auth Tables
```

### 🔗 INTEGRAÇÕES
```
Integrações
├── Internas
│   ├── Frontend ↔ Backend
│   ├── Backend ↔ Database
│   └── Services ↔ Models
├── Externas (Futuras)
│   ├── APIs de Dados Meteorológicos
│   ├── Sistemas de Navegação
│   └── Plataformas de Manutenção
└── Comunicação
    ├── HTTP/REST
    ├── JWT Tokens
    └── JSON
```

### 🎯 FUNCIONALIDADES PRINCIPAIS
```
Funcionalidades
├── Monitoramento
│   ├── Status da Frota
│   ├── Bioincrustação em Tempo Real
│   └── Alertas e Notificações
├── Previsões
│   ├── Bioincrustação Futura
│   ├── Impacto no Combustível
│   └── Risco NORMAM 401
├── Conformidade
│   ├── Verificação Automática
│   ├── Relatórios Regulatórios
│   └── Histórico de Inspeções
├── Recomendações
│   ├── Limpeza Otimizada
│   ├── Métodos de Limpeza
│   └── Priorização de Ações
└── Análises
    ├── Economia Acumulada
    ├── Redução de CO2
    └── Impacto Operacional
```

### 👥 USUÁRIOS
```
Usuários
├── Perfis
│   ├── Administrador
│   ├── Capitão
│   ├── Técnico de Manutenção
│   ├── Gerente de Frota
│   └── Analista de Conformidade
├── Papéis (15)
│   ├── Almirante
│   ├── Capitão de Mar e Guerra
│   ├── Capitão de Fragata
│   └── ...
└── Permissões (24)
    ├── MANAGE_USERS
    ├── VIEW_FLEET
    ├── MANAGE_VESSELS
    └── ...
```

### 🔒 SEGURANÇA
```
Segurança
├── Autenticação
│   ├── JWT Tokens
│   ├── Refresh Tokens
│   └── Password Hashing (bcrypt)
├── Autorização
│   ├── RBAC
│   ├── Permissions
│   └── Vessel Assignment
└── Proteções
    ├── CORS
    ├── Input Validation
    └── Rate Limiting (futuro)
```

## 🎨 Visualização Gráfica

### Relações Principais
```
Frontend ←→ Backend ←→ Database
    ↓         ↓          ↓
  UI/UX    Business   Persistence
           Logic
             ↓
        AI/ML Models
             ↓
        Services
```

### Fluxo de Dados
```
User Action
    ↓
Frontend Component
    ↓
API Service
    ↓
Backend Endpoint
    ↓
Service Layer
    ↓
Model/Repository
    ↓
Database
    ↓
Response
    ↓
Frontend Update
```

## 💡 Insights do Mindmap

### Pontos Fortes Identificados
1. ✅ Arquitetura bem estruturada
2. ✅ Separação clara de responsabilidades
3. ✅ Múltiplos modelos de IA
4. ✅ Sistema de autenticação robusto
5. ✅ Funcionalidades abrangentes

### Oportunidades Identificadas
1. ⚠️ Cache distribuído
2. ⚠️ Message queue para processamento assíncrono
3. ⚠️ CDN para assets estáticos
4. ⚠️ Integrações externas
5. ⚠️ Testes E2E automatizados

## 🔄 Atualização do Mindmap

Este mindmap deve ser atualizado regularmente conforme:
- Novas funcionalidades são adicionadas
- Arquitetura evolui
- Novas integrações são implementadas
- Mudanças estruturais ocorrem

