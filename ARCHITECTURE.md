# Arquitetura do Sistema HullZero

Este documento apresenta a visão geral da arquitetura da aplicação HullZero, detalhando o fluxo de dados e a interação entre os componentes.

## Fluxograma da Aplicação

```mermaid
graph TD
    %% Estilos
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef api fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef service fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef external fill:#eceff1,stroke:#455a64,stroke-width:2px,stroke-dasharray: 5 5,color:#000

    %% Atores
    User((Usuário))

    %% Frontend
    subgraph Frontend [Frontend (React + Vite + Chakra UI)]
        direction TB
        App[App Container]
        
        subgraph Pages [Páginas]
            Dashboard[Dashboard Geral]
            Fleet[Gestão da Frota]
            VesselDetails[Detalhes da Embarcação]
            Maintenance[Manutenção & Histórico]
            InvasiveSpecies[Espécies Invasoras]
        end
        
        subgraph State [Gerenciamento de Estado]
            ReactQuery[TanStack Query]
            AuthContext[Contexto de Autenticação]
        end
        
        App --> AuthContext
        AuthContext --> Pages
        Pages <--> ReactQuery
    end

    %% API
    subgraph Backend [Backend (FastAPI)]
        direction TB
        APIGateway[API Gateway / Router]
        
        subgraph Endpoints [Endpoints]
            AuthAPI[/api/auth]
            VesselAPI[/api/vessels]
            MaintAPI[/api/maintenance]
            DashAPI[/api/dashboard]
            CompAPI[/api/compliance]
        end
        
        subgraph Services [Serviços de Negócio]
            PredService[Serviço de Predição (Híbrido)]
            FuelService[Análise de Combustível]
            RiskService[Risco NORMAM-401]
            BioService[Espécies Invasoras]
            OptService[Otimização de Manutenção]
        end
        
        APIGateway --> Endpoints
        Endpoints --> Services
    end

    %% Dados
    subgraph DataLayer [Camada de Dados]
        ORM[SQLAlchemy ORM]
        DB[(Banco de Dados\nSQLite/PostgreSQL)]
        FileStore[Armazenamento de Arquivos\n(Uploads)]
    end

    %% Fluxo Principal
    User <--> App
    ReactQuery <-->|HTTP/JSON| APIGateway
    
    %% Conexões de Serviços
    VesselAPI --> ORM
    MaintAPI --> ORM
    MaintAPI --> FileStore
    DashAPI --> ORM
    
    %% Lógica de Negócio
    PredService -->|Lê| ORM
    FuelService -->|Lê| ORM
    RiskService -->|Lê| ORM
    BioService -->|Lê| ORM
    
    ORM <--> DB

    %% Detalhes Específicos
    Maintenance -->|Upload Fotos| MaintAPI
    VesselDetails -->|Solicita Predição| PredService
    InvasiveSpecies -->|Analisa Risco| BioService

    %% Classes
    class App,Dashboard,Fleet,VesselDetails,Maintenance,InvasiveSpecies frontend
    class APIGateway,AuthAPI,VesselAPI,MaintAPI,DashAPI,CompAPI api
    class PredService,FuelService,RiskService,BioService,OptService service
    class ORM,DB,FileStore data
```

## Descrição dos Componentes

### 1. Frontend (Client-Side)
- **Tecnologia**: React, Vite, TypeScript.
- **UI Framework**: Chakra UI para componentes visuais responsivos e acessíveis.
- **Gerenciamento de Estado**: TanStack Query (React Query) para cache, sincronização e atualização de dados do servidor.
- **Funcionalidades**:
    - Visualização de KPIs da frota em tempo real.
    - Detalhamento técnico de cada embarcação.
    - Registro e monitoramento de manutenções com suporte a upload de imagens.
    - Análise avançada de riscos de bioincrustação e espécies invasoras.

### 2. Backend (Server-Side)
- **Tecnologia**: Python, FastAPI.
- **Arquitetura**: RESTful API com separação clara de responsabilidades (Rotas, Controladores, Serviços, Modelos).
- **Serviços Principais**:
    - **Predição de Bioincrustação**: Modelo híbrido combinando física naval e Machine Learning para estimar o crescimento de incrustações.
    - **Análise Econômica**: Cálculo do impacto financeiro (combustível extra) e ambiental (emissões de CO₂).
    - **Compliance**: Verificação automatizada contra normas como a NORMAM-401.

### 3. Camada de Dados
- **Banco de Dados**: SQLite para desenvolvimento ágil, preparado para migração para PostgreSQL/TimescaleDB em produção.
- **ORM**: SQLAlchemy para abstração do banco de dados e manipulação segura de dados.
- **Armazenamento**: Sistema de arquivos local para persistência de evidências (fotos de manutenção), com estrutura para migração para Object Storage (S3).
