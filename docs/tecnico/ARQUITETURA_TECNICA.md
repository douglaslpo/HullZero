# Arquitetura Técnica - HullZero

## 1. Visão Geral da Arquitetura

O HullZero é uma aplicação full-stack construída com arquitetura de microserviços, separando claramente as responsabilidades entre frontend, backend, banco de dados e modelos de IA. A arquitetura foi projetada para ser escalável, manutenível e extensível.

## 2. Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  React 18 + TypeScript + Chakra UI + React Query            │
│  Porta: 5173                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      Backend API                             │
│  FastAPI + Python 3.11+ + Pydantic                         │
│  Porta: 8000                                                 │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       │                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼─────────┐
│  Database   │  │  AI/ML Models   │  │   Services    │
│  SQLAlchemy │  │  XGBoost, RF,   │  │  Business     │
│  SQLite/    │  │  Prophet, etc.  │  │  Logic        │
│  PostgreSQL │  │                 │  │               │
└─────────────┘  └─────────────────┘  └───────────────┘
```

## 3. Camadas da Aplicação

### 3.1 Camada de Apresentação (Frontend)

**Tecnologias:**
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.8
- Chakra UI 2.8.2
- React Query 5.12.2
- React Router DOM 6.20.0

**Responsabilidades:**
- Interface do usuário
- Visualização de dados
- Interação com usuário
- Comunicação com API via HTTP

**Estrutura:**
```
frontend/
├── src/
│   ├── api/              # Serviços de API
│   ├── components/       # Componentes reutilizáveis
│   ├── pages/            # Páginas da aplicação
│   └── App.tsx           # Componente raiz
```

### 3.2 Camada de API (Backend)

**Tecnologias:**
- FastAPI 0.104+
- Python 3.11+
- Pydantic 2.0+
- Uvicorn (ASGI server)

**Responsabilidades:**
- Exposição de endpoints REST
- Validação de dados de entrada
- Orquestração de serviços
- Tratamento de erros

**Estrutura:**
```
src/
├── api/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── db_endpoints.py      # Endpoints com banco de dados
│   └── compliance_endpoints.py  # Endpoints de conformidade
```

### 3.3 Camada de Serviços

**Responsabilidades:**
- Lógica de negócio
- Orquestração de modelos de IA
- Cálculos e transformações
- Integração com sistemas externos

**Estrutura:**
```
src/
├── services/
│   ├── compliance_service.py
│   ├── recommendation_service.py
│   ├── cleaning_methods_service.py
│   ├── invasive_species_service.py
│   ├── economy_service.py
│   └── co2_service.py
```

### 3.4 Camada de Modelos de IA

**Tecnologias:**
- scikit-learn
- XGBoost
- Prophet (time series)
- NumPy, Pandas

**Responsabilidades:**
- Predição de bioincrustação
- Predição de impacto no combustível
- Predição de risco NORMAM 401
- Otimização de inspeções
- Detecção de anomalias
- Explicabilidade (SHAP)

**Estrutura:**
```
src/
├── models/
│   ├── fouling_prediction.py
│   ├── advanced_fouling_prediction.py
│   ├── fuel_impact.py
│   ├── normam401_risk.py
│   ├── inspection_optimizer.py
│   ├── anomaly_detector.py
│   ├── corrective_actions.py
│   └── explainability.py
```

### 3.5 Camada de Dados

**Tecnologias:**
- SQLAlchemy 2.0+
- SQLite (desenvolvimento)
- PostgreSQL + TimescaleDB (produção)

**Responsabilidades:**
- Persistência de dados
- Modelagem de dados
- Migrações de schema
- Queries e relatórios

**Estrutura:**
```
src/
├── database/
│   ├── models.py              # Modelos originais
│   ├── models_normalized.py   # Modelos normalizados
│   ├── repositories.py        # Repositórios originais
│   ├── repositories_normalized.py  # Repositórios normalizados
│   ├── migrations/            # Scripts de migração SQL
│   ├── init_data.py          # Dados iniciais
│   └── init_reference_data.py  # Dados de referência
```

## 4. Padrões Arquiteturais

### 4.1 Repository Pattern

O sistema utiliza o padrão Repository para abstrair o acesso a dados:

```python
class VesselRepository:
    def get_by_id(self, vessel_id: str) -> Optional[Vessel]:
        # Implementação
        
    def get_all(self) -> List[Vessel]:
        # Implementação
        
    def create(self, vessel_data: dict) -> Vessel:
        # Implementação
```

**Benefícios:**
- Separação de responsabilidades
- Facilita testes unitários
- Permite troca de implementação de banco de dados

### 4.2 Service Layer Pattern

A lógica de negócio é encapsulada em serviços:

```python
class NORMAM401ComplianceService:
    def check_compliance(self, vessel_id, fouling_data) -> ComplianceCheck:
        # Lógica de verificação de conformidade
```

**Benefícios:**
- Reutilização de lógica
- Facilita manutenção
- Testabilidade

### 4.3 Dependency Injection

FastAPI utiliza injeção de dependências para gerenciar recursos:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/vessels/{vessel_id}")
def get_vessel(vessel_id: str, db: Session = Depends(get_db)):
    # Uso do banco de dados
```

## 5. Comunicação entre Componentes

### 5.1 Frontend ↔ Backend

**Protocolo:** HTTP/REST
**Formato:** JSON
**Autenticação:** Não implementada (planejada)

**Fluxo:**
```
Frontend (React Query)
    ↓
Axios Client
    ↓
HTTP Request
    ↓
FastAPI Endpoint
    ↓
Service Layer
    ↓
Repository/Model
    ↓
Response (JSON)
```

### 5.2 Backend ↔ Database

**ORM:** SQLAlchemy
**Conexão:** Connection pooling
**Transações:** Gerenciadas por contexto

**Fluxo:**
```
FastAPI Endpoint
    ↓
Dependency Injection (get_db)
    ↓
Repository
    ↓
SQLAlchemy Session
    ↓
Database
```

### 5.3 Backend ↔ AI Models

**Integração:** Import direto de módulos Python
**Serialização:** NumPy arrays, Pandas DataFrames
**Cache:** Em memória (planejado: Redis)

**Fluxo:**
```
Service Layer
    ↓
Model Import
    ↓
Feature Preparation
    ↓
Model Prediction
    ↓
Result Processing
```

## 6. Banco de Dados

### 6.1 Modelo de Dados

O sistema utiliza modelo normalizado (3NF+) com:

**Tabelas de Referência:**
- vessel_types
- vessel_classes
- paint_types
- ports
- routes
- contractors
- cargo_types
- fuel_types
- invasive_species

**Tabelas Principais:**
- vessels
- fouling_measurements
- operational_data
- maintenance_events
- compliance_checks
- inspections
- paint_applications

**Tabelas de Relacionamento (N:N):**
- vessel_operating_routes
- vessel_cargo_types
- vessel_fuel_alternatives

### 6.2 Migrações

Sistema de migrações SQL para evolução do schema:

```
src/database/migrations/
├── 001_create_reference_tables.sql
└── 002_create_new_entities.sql
```

**Ferramenta:** `src/database/migrate.py`

### 6.3 Estratégia de Dados

- **Desenvolvimento:** SQLite (arquivo local)
- **Produção:** PostgreSQL + TimescaleDB (séries temporais)
- **Cache:** Em memória (planejado: Redis)

## 7. Modelos de IA

### 7.1 Arquitetura de Modelos

**Modelo Híbrido:**
- Combinação de modelo físico e machine learning
- Peso: 30% físico, 70% ML

**Ensemble de ML:**
- XGBoost
- Random Forest
- Gradient Boosting
- Extra Trees
- Voting Regressor (combinação)

### 7.2 Pipeline de Predição

```
Input Features
    ↓
Feature Engineering
    ↓
Scaling/Normalization
    ↓
Model Ensemble
    ↓
Post-processing
    ↓
Prediction Result
```

### 7.3 Explicabilidade

**Técnicas:**
- SHAP values (quando disponível)
- Feature importance
- Explicações em linguagem natural

## 8. Segurança

### 8.1 Implementado

- Validação de entrada (Pydantic)
- CORS configurado
- Tratamento de erros padronizado

### 8.2 Planejado

- Autenticação JWT
- Autorização baseada em roles
- Rate limiting
- HTTPS obrigatório
- Validação de dados sensíveis

## 9. Performance

### 9.1 Otimizações Implementadas

**Frontend:**
- Code splitting por rota
- React Query cache
- Lazy loading de componentes

**Backend:**
- Connection pooling (SQLAlchemy)
- Cache de modelos (em memória)
- Queries otimizadas

**Database:**
- Índices em campos frequentes
- Normalização para reduzir redundância

### 9.2 Planejado

- Redis para cache distribuído
- CDN para assets estáticos
- Load balancing
- Database replication

## 10. Escalabilidade

### 10.1 Horizontal Scaling

**Frontend:**
- Stateless (pode escalar horizontalmente)
- CDN para assets

**Backend:**
- Stateless (pode escalar horizontalmente)
- Load balancer necessário

**Database:**
- Read replicas
- Sharding (se necessário)

### 10.2 Vertical Scaling

- Aumento de recursos de servidor
- Otimização de queries
- Cache mais agressivo

## 11. Monitoramento e Logging

### 11.1 Implementado

- Logs básicos (print statements)
- Health check endpoint (`/health`)

### 11.2 Planejado

- Structured logging (JSON)
- Log aggregation (ELK stack)
- APM (Application Performance Monitoring)
- Métricas (Prometheus)
- Alertas (Grafana)

## 12. Deploy e DevOps

### 12.1 Desenvolvimento Local

- Scripts de inicialização (`init_complete.py`)
- Docker Compose (planejado)
- Hot reload (Vite + Uvicorn)

### 12.2 Produção (Planejado)

- Containerização (Docker)
- Orquestração (Kubernetes)
- CI/CD (GitHub Actions)
- Infrastructure as Code (Terraform)

## 13. Testes

### 13.1 Estratégia

**Unit Tests:**
- Modelos de IA
- Serviços
- Repositórios

**Integration Tests:**
- Endpoints da API
- Fluxos completos

**E2E Tests:**
- Fluxos críticos do usuário

### 13.2 Ferramentas

- pytest (backend)
- Jest/React Testing Library (frontend - planejado)
- Playwright (E2E - planejado)

## 14. Documentação

### 14.1 API Documentation

- Swagger/OpenAPI automático (`/docs`)
- ReDoc (`/redoc`)

### 14.2 Código

- Docstrings em Python
- JSDoc em TypeScript (planejado)
- README.md principal

### 14.3 Técnica

- Documentação em `docs/`
- Diagramas de arquitetura
- Guias de desenvolvimento

## 15. Manutenibilidade

### 15.1 Princípios Aplicados

- SOLID principles
- DRY (Don't Repeat Yourself)
- Separation of Concerns
- Single Responsibility

### 15.2 Code Quality

- Type hints (Python)
- TypeScript strict mode
- Linting (ESLint, flake8)
- Formatação (Black, Prettier - planejado)

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


