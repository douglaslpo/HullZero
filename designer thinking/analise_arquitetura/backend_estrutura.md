# Análise de Arquitetura - Backend

## 🏗️ Estrutura do Backend

### Organização de Diretórios

```
src/
├── api/                    # Endpoints da API
│   ├── main.py            # Aplicação FastAPI principal
│   ├── auth_endpoints.py  # Endpoints de autenticação
│   ├── db_endpoints.py    # Endpoints com banco de dados
│   └── compliance_endpoints.py  # Endpoints de conformidade
├── auth/                   # Sistema de autenticação
│   ├── auth_service.py    # Serviço de autenticação
│   ├── models.py         # Modelos de usuário, papel, permissão
│   ├── dependencies.py   # Dependências FastAPI
│   └── init_auth_data.py # Inicialização de dados
├── database/              # Camada de dados
│   ├── database.py        # Configuração do banco
│   ├── models.py         # Modelos SQLAlchemy
│   ├── repositories.py   # Repositórios (Repository Pattern)
│   └── migrations/       # Migrações SQL
├── models/                # Modelos de IA/ML
│   ├── fouling_prediction.py
│   ├── fuel_impact.py
│   ├── normam401_risk.py
│   ├── advanced_fouling_prediction.py
│   └── ...
├── services/              # Serviços de negócio
│   ├── compliance_service.py
│   ├── recommendation_service.py
│   ├── economy_service.py
│   └── ...
└── data/                  # Dados e geração de dados
    └── transpetro_fleet_data.py
```

## 🔌 Endpoints da API

### Autenticação (`/api/auth/*`)
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Informações do usuário atual
- `POST /api/auth/users` - Criar usuário
- `GET /api/auth/users` - Listar usuários
- `PUT /api/auth/users/{id}` - Atualizar usuário
- `POST /api/auth/users/{id}/roles` - Atribuir papel
- `POST /api/auth/change-password` - Alterar senha

### Dados do Banco (`/api/db/*`)
- `GET /api/db/vessels` - Listar embarcações
- `GET /api/db/vessels/{id}` - Detalhes da embarcação
- `GET /api/db/vessels/{id}/fouling` - Dados de bioincrustação
- `GET /api/db/vessels/{id}/fouling/latest` - Última medição
- `GET /api/db/vessels/{id}/operational-data/latest` - Dados operacionais
- `GET /api/db/vessels/{id}/maintenance/latest` - Última manutenção

### Conformidade (`/api/compliance/*`)
- `GET /api/compliance/vessels/{id}/checks` - Verificações de conformidade
- `GET /api/compliance/vessels/{id}/checks/latest` - Última verificação
- `GET /api/compliance/vessels/{id}/inspections` - Inspeções
- `GET /api/compliance/status/summary` - Resumo de status

### Previsões e Análises (`/api/vessels/*`)
- `POST /api/vessels/{id}/fouling/predict` - Prever bioincrustação
- `POST /api/vessels/{id}/fouling/predict/advanced` - Previsão avançada
- `POST /api/vessels/{id}/fuel-impact` - Impacto no combustível
- `POST /api/vessels/{id}/normam401-risk` - Risco NORMAM 401

## 🔐 Sistema de Autenticação

### Componentes
- **JWT**: Tokens de acesso e refresh
- **OAuth2**: Password flow
- **RBAC**: Role-Based Access Control
- **15 Papéis**: Hierarquia naval
- **24 Permissões**: Controle granular

### Fluxo
```
1. Cliente → POST /api/auth/login (username, password)
2. Servidor → Valida credenciais
3. Servidor → Gera JWT (access + refresh)
4. Cliente → Armazena tokens
5. Cliente → Envia access token em requisições
6. Servidor → Valida token e verifica permissões
```

## 💾 Camada de Dados

### Repository Pattern
- Abstração de acesso a dados
- Facilita testes e manutenção
- Exemplo: `VesselRepository`

### Modelos SQLAlchemy
- Normalização 3NF+
- Relacionamentos bem definidos
- Migrações estruturadas

## 🤖 Modelos de IA/ML

### Tipos de Modelos
1. **Previsão de Bioincrustação**
   - Modelo físico + ML
   - Ensemble (XGBoost, RandomForest, etc.)

2. **Impacto no Combustível**
   - Regressão
   - Análise de correlação

3. **Risco NORMAM 401**
   - Classificação
   - Análise de conformidade

4. **Otimização de Inspeções**
   - Otimização
   - Análise de custo-benefício

5. **Detecção de Anomalias**
   - Anomaly detection
   - Padrões não usuais

6. **Ações Corretivas**
   - Recomendações
   - Priorização

7. **Explicabilidade**
   - SHAP values
   - Interpretação de modelos

## 🔧 Serviços de Negócio

### Compliance Service
- Verificação de conformidade
- Cálculo de riscos
- Geração de relatórios

### Recommendation Service
- Recomendações de limpeza
- Priorização de ações
- Análise de custo-benefício

### Economy Service
- Cálculo de economia
- Análise de ROI
- Projeções financeiras

### CO2 Service
- Cálculo de emissões
- Redução de CO2
- Impacto ambiental

### Cleaning Methods Service
- Recomendação de métodos
- Comparação de técnicas
- Análise de eficácia

### Invasive Species Service
- Identificação de espécies
- Avaliação de risco
- Recomendações de ação

## 📊 Padrões e Boas Práticas

### 1. Validação de Dados
- Pydantic models
- Validação automática
- Mensagens de erro claras

### 2. Tratamento de Erros
- HTTPException
- Códigos de status apropriados
- Mensagens informativas

### 3. Logging
- Logs estruturados
- Níveis apropriados
- Contexto rico

### 4. Documentação
- OpenAPI/Swagger
- Descrições detalhadas
- Exemplos de uso

## 🔍 Pontos Fortes

1. ✅ Estrutura modular e organizada
2. ✅ Separação clara de responsabilidades
3. ✅ Autenticação robusta
4. ✅ Modelos de IA bem estruturados
5. ✅ API RESTful bem definida

## ⚠️ Oportunidades de Melhoria

1. ⚠️ Cache pode ser implementado
2. ⚠️ Testes podem ser expandidos
3. ⚠️ Observabilidade pode ser melhorada
4. ⚠️ Tratamento de erros pode ser padronizado
5. ⚠️ Documentação pode ser mais completa

