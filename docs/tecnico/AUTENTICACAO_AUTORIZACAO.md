# Sistema de Autenticação e Autorização - HullZero

## 1. Visão Geral

O sistema HullZero implementa autenticação baseada em JWT (JSON Web Tokens) e autorização baseada em papéis (RBAC - Role-Based Access Control), alinhado com a hierarquia e responsabilidades do setor naval brasileiro.

## 2. Arquitetura

### 2.1 Componentes

**Autenticação:**
- JWT para tokens de acesso e refresh
- OAuth2 Password Flow
- Hash de senhas com bcrypt
- Refresh tokens para renovação

**Autorização:**
- Sistema de papéis (15 papéis definidos)
- Sistema de permissões (24 permissões)
- Relacionamento N:N entre usuários e papéis
- Relacionamento N:N entre papéis e permissões
- Atribuição de embarcações a usuários

**Auditoria:**
- Logs de todas as ações
- Rastreabilidade completa
- Histórico de mudanças

### 2.2 Fluxo de Autenticação

```
1. Cliente envia credenciais (username/password)
   ↓
2. Servidor valida credenciais
   ↓
3. Servidor gera access token (30 min) e refresh token (7 dias)
   ↓
4. Cliente armazena tokens
   ↓
5. Cliente envia access token em requisições (Header: Authorization: Bearer <token>)
   ↓
6. Servidor valida token e verifica permissões
   ↓
7. Se token expirar, cliente usa refresh token para obter novo access token
```

## 3. Modelos de Dados

### 3.1 User (Usuário)

```python
class User:
    id: str (UUID)
    username: str (único)
    email: str (único)
    full_name: str
    hashed_password: str
    is_active: bool
    is_verified: bool
    employee_id: str (matrícula)
    department: str
    position: str
    phone: str
    certifications: str (JSON)
    certification_expiry: datetime
    created_at: datetime
    updated_at: datetime
    last_login: datetime
```

### 3.2 Role (Papel)

```python
class Role:
    id: str (enum value)
    name: str
    description: str
    level: int (1-5, hierarquia)
    created_at: datetime
    updated_at: datetime
```

### 3.3 Permission (Permissão)

```python
class Permission:
    id: str (enum value)
    name: str
    description: str
    category: str (management, view, operation, approval, report)
    created_at: datetime
```

### 3.4 AuditLog (Log de Auditoria)

```python
class AuditLog:
    id: str (UUID)
    user_id: str
    action: str (create, update, delete, view, etc.)
    resource_type: str (vessel, maintenance, compliance, etc.)
    resource_id: str
    details: str (JSON)
    changes: str (JSON, antes/depois)
    ip_address: str
    user_agent: str
    timestamp: datetime
```

## 4. Papéis Implementados

### 4.1 Nível Executivo

- **ADMINISTRADOR_SISTEMA:** Acesso total
- **DIRETOR_OPERACOES:** Visão estratégica
- **GERENTE_FROTA:** Gestão operacional

### 4.2 Nível Técnico/Regulatório

- **OFICIAL_SEGURANCA:** Conformidade NORMAM 401
- **INSPETOR_NORMAM:** Inspeções certificadas
- **ENGENHEIRO_NAVAL:** Análise técnica

### 4.3 Nível Operacional

- **CAPITAO_EMBARCAÇÃO:** Comando de embarcação
- **IMEDIATO:** Assistência ao capitão
- **OFICIAL_MAQUINAS:** Operação de máquinas
- **TECNICO_MANUTENCAO:** Execução de manutenções

### 4.4 Nível Consultivo

- **AUDITOR:** Auditoria e verificação
- **ANALISTA_DADOS:** Análise de dados
- **CONSULTOR:** Consultoria externa

### 4.5 Nível Básico

- **OPERADOR:** Operação básica
- **VISUALIZADOR:** Apenas visualização

## 5. Permissões

### 5.1 Gestão

- `MANAGE_USERS`: Gerenciar usuários
- `MANAGE_ROLES`: Gerenciar papéis
- `MANAGE_VESSELS`: Gerenciar embarcações
- `MANAGE_SYSTEM`: Gerenciar sistema

### 5.2 Visualização

- `VIEW_DASHBOARD`: Visualizar dashboard
- `VIEW_VESSELS`: Visualizar embarcações
- `VIEW_COMPLIANCE`: Visualizar conformidade
- `VIEW_MAINTENANCE`: Visualizar manutenção
- `VIEW_OPERATIONAL_DATA`: Visualizar dados operacionais

### 5.3 Operações

- `CREATE_VESSEL`: Criar embarcação
- `EDIT_VESSEL`: Editar embarcação
- `DELETE_VESSEL`: Excluir embarcação
- `REGISTER_MAINTENANCE`: Registrar manutenção
- `REGISTER_OPERATIONAL_DATA`: Registrar dados operacionais
- `REGISTER_INSPECTION`: Registrar inspeção

### 5.4 Aprovações

- `APPROVE_MAINTENANCE`: Aprovar manutenção
- `APPROVE_COMPLIANCE`: Aprovar conformidade
- `APPROVE_ACTION`: Aprovar ação corretiva

### 5.5 Relatórios

- `GENERATE_REPORTS`: Gerar relatórios
- `EXPORT_DATA`: Exportar dados
- `VIEW_AUDIT_LOGS`: Visualizar logs de auditoria

### 5.6 Predições

- `VIEW_PREDICTIONS`: Visualizar predições básicas
- `VIEW_ADVANCED_PREDICTIONS`: Visualizar predições avançadas
- `VIEW_EXPLANATIONS`: Visualizar explicações de IA

## 6. Endpoints de Autenticação

### 6.1 Login

**POST** `/api/auth/login`

Body (form-data):
```
username: string
password: string
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 6.2 Refresh Token

**POST** `/api/auth/refresh`

Body:
```json
{
  "refresh_token": "eyJ..."
}
```

Response: Mesmo formato do login

### 6.3 Informações do Usuário

**GET** `/api/auth/me`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@hullzero.com",
  "full_name": "Administrador",
  "is_active": true,
  "is_verified": true,
  "roles": ["administrador_sistema"]
}
```

### 6.4 Gestão de Usuários

**POST** `/api/auth/users` - Criar usuário (requer MANAGE_USERS)
**GET** `/api/auth/users` - Listar usuários (requer MANAGE_USERS)
**PUT** `/api/auth/users/{user_id}` - Atualizar usuário (requer MANAGE_USERS)
**POST** `/api/auth/users/{user_id}/roles` - Atribuir papel (requer MANAGE_USERS)

### 6.5 Alterar Senha

**POST** `/api/auth/change-password`

Body:
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha"
}
```

## 7. Uso em Endpoints

### 7.1 Proteger Endpoint com Autenticação

```python
from src.auth import get_current_active_user, User

@app.get("/api/vessels")
async def list_vessels(
    current_user: User = Depends(get_current_active_user)
):
    # Endpoint protegido - requer autenticação
    return {"vessels": [...]}
```

### 7.2 Verificar Permissão

```python
from src.auth import require_permission, PermissionEnum

@app.post("/api/vessels")
async def create_vessel(
    current_user: User = Depends(require_permission(PermissionEnum.CREATE_VESSEL))
):
    # Endpoint protegido - requer permissão específica
    return {"vessel": {...}}
```

### 7.3 Verificar Papel

```python
from src.auth import require_role, UserRoleEnum

@app.post("/api/compliance/approve")
async def approve_compliance(
    current_user: User = Depends(require_role(UserRoleEnum.OFICIAL_SEGURANCA))
):
    # Endpoint protegido - requer papel específico
    return {"status": "approved"}
```

### 7.4 Verificar Acesso à Embarcação

```python
from src.auth import can_access_vessel

@app.get("/api/vessels/{vessel_id}")
async def get_vessel(
    vessel_id: str,
    current_user: User = Depends(can_access_vessel(vessel_id))
):
    # Endpoint protegido - verifica acesso à embarcação
    return {"vessel": {...}}
```

## 8. Inicialização

### 8.1 Criar Tabelas

Execute a migração:
```bash
python -m src.database.migrate run
```

Ou use o script Python:
```python
from src.database import init_db
init_db()
```

### 8.2 Inicializar Papéis e Permissões

```bash
python src/auth/init_auth_data.py
```

Este script:
1. Cria todas as permissões
2. Cria todos os papéis
3. Atribui permissões aos papéis
4. Cria usuário administrador inicial (admin/admin123)

### 8.3 Criar Usuário Administrador

O script `init_auth_data.py` cria automaticamente:
- Username: `admin`
- Password: `admin123`
- Papel: `ADMINISTRADOR_SISTEMA`

**IMPORTANTE:** Altere a senha após o primeiro login!

## 9. Segurança

### 9.1 Senhas

- Hash com bcrypt (cost factor 12)
- Senhas nunca armazenadas em texto plano
- Validação de força de senha (planejado)

### 9.2 Tokens

- Access tokens expiram em 30 minutos
- Refresh tokens expiram em 7 dias
- Tokens assinados com HS256
- Secret key deve ser alterada em produção

### 9.3 Validações

- Usuário deve estar ativo
- Token deve ser válido e não expirado
- Permissões verificadas a cada requisição
- Acesso à embarcação verificado quando aplicável

### 9.4 Auditoria

- Todas as ações são registradas
- Logs incluem usuário, ação, recurso, IP, timestamp
- Logs são imutáveis (apenas inserção)

## 10. Configuração

### 10.1 Variáveis de Ambiente

```bash
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 10.2 Produção

**Recomendações:**
- Usar secret key forte e aleatória
- Habilitar HTTPS obrigatório
- Configurar CORS adequadamente
- Implementar rate limiting
- Monitorar tentativas de login falhadas
- Implementar bloqueio de conta após tentativas

## 11. Integração com Frontend

### 11.1 Login

```typescript
const response = await axios.post('/api/auth/login', 
  new URLSearchParams({
    username: 'admin',
    password: 'admin123'
  })
);

const { access_token, refresh_token } = response.data;
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### 11.2 Requisições Autenticadas

```typescript
axios.defaults.headers.common['Authorization'] = 
  `Bearer ${localStorage.getItem('access_token')}`;
```

### 11.3 Refresh Token

```typescript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await axios.post('/api/auth/refresh', {
    refresh_token: refreshToken
  });
  
  localStorage.setItem('access_token', response.data.access_token);
  return response.data.access_token;
}
```

### 11.4 Interceptor para Renovação Automática

```typescript
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        const newToken = await refreshAccessToken();
        error.config.headers['Authorization'] = `Bearer ${newToken}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Redirecionar para login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

## 12. Exemplos de Uso

### 12.1 Endpoint Público

```python
@app.get("/health")
async def health_check():
    # Não requer autenticação
    return {"status": "healthy"}
```

### 12.2 Endpoint Protegido

```python
@app.get("/api/dashboard/kpis")
async def get_kpis(
    current_user: User = Depends(get_current_active_user)
):
    # Requer autenticação
    return {"kpis": {...}}
```

### 12.3 Endpoint com Permissão

```python
@app.post("/api/vessels")
async def create_vessel(
    vessel_data: VesselCreate,
    current_user: User = Depends(require_permission(PermissionEnum.CREATE_VESSEL))
):
    # Requer permissão específica
    return {"vessel": create_vessel_in_db(vessel_data)}
```

### 12.4 Endpoint com Múltiplos Papéis

```python
@app.post("/api/compliance/approve")
async def approve_compliance(
    current_user: User = Depends(require_any_role([
        UserRoleEnum.OFICIAL_SEGURANCA,
        UserRoleEnum.GERENTE_FROTA
    ]))
):
    # Requer um dos papéis especificados
    return {"status": "approved"}
```

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025

