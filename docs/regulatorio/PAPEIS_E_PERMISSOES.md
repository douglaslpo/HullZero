# Papéis e Permissões - Sistema HullZero

## 1. Visão Geral

O sistema HullZero implementa controle de acesso baseado em papéis (RBAC - Role-Based Access Control) alinhado com a hierarquia e responsabilidades do setor naval brasileiro, considerando as regulamentações da NORMAM 401 e práticas da indústria marítima.

## 2. Hierarquia de Papéis

### 2.1 Nível Executivo

**ADMINISTRADOR_SISTEMA**
- **Descrição:** Acesso total ao sistema, configurações globais e gestão de usuários
- **Responsabilidades:**
  - Gerenciar configurações globais da aplicação
  - Criar, modificar e excluir usuários e papéis
  - Visualizar e gerenciar logs de auditoria
  - Configurar parâmetros do sistema
  - Gerenciar integrações externas
- **Uso Típico:** Equipe de TI, administradores de sistema

**DIRETOR_OPERACOES**
- **Descrição:** Visão estratégica completa da frota e operações
- **Responsabilidades:**
  - Acesso a todos os dados e relatórios executivos
  - Aprovação de decisões estratégicas
  - Visualização de KPIs e métricas consolidadas
  - Acesso a análises de ROI e economia
- **Uso Típico:** Diretores, vice-presidentes de operações

**GERENTE_FROTA**
- **Descrição:** Gestão operacional completa da frota
- **Responsabilidades:**
  - Visualizar e gerenciar todas as embarcações
  - Aprovar manutenções e limpezas
  - Gerar relatórios operacionais
  - Acompanhar conformidade da frota
  - Alocar recursos e planejar operações
- **Uso Típico:** Gerentes de frota, superintendentes

### 2.2 Nível Técnico e Regulatório

**OFICIAL_SEGURANCA**
- **Descrição:** Garantir conformidade com normas de segurança e regulamentações
- **Responsabilidades:**
  - Verificar conformidade NORMAM 401
  - Aprovar inspeções e verificações
  - Gerar relatórios regulatórios
  - Registrar e acompanhar não conformidades
  - Validar certificações e documentos
- **Uso Típico:** Oficiais de segurança, auditores de conformidade
- **Requisitos Regulatórios:** Certificação conforme NORMAM 401

**INSPETOR_NORMAM**
- **Descrição:** Realizar inspeções e verificações de conformidade
- **Responsabilidades:**
  - Registrar inspeções de bioincrustação
  - Medir espessura e rugosidade
  - Gerar relatórios de inspeção
  - Validar medições realizadas
  - Acompanhar histórico de inspeções
- **Uso Típico:** Inspetores certificados, técnicos de inspeção
- **Requisitos Regulatórios:** Certificação para inspeção NORMAM 401

**ENGENHEIRO_NAVAL**
- **Descrição:** Análise técnica e engenharia de embarcações
- **Responsabilidades:**
  - Acessar dados técnicos detalhados
  - Analisar predições e modelos de IA
  - Validar recomendações técnicas
  - Aprovar métodos de limpeza e manutenção
  - Acessar dados de performance e eficiência
- **Uso Típico:** Engenheiros navais, analistas técnicos

### 2.3 Nível Operacional

**CAPITAO_EMBARCAÇÃO**
- **Descrição:** Comando de embarcação específica
- **Responsabilidades:**
  - Acesso completo aos dados da sua embarcação
  - Visualizar predições e recomendações
  - Registrar dados operacionais
  - Solicitar manutenções e limpezas
  - Acompanhar conformidade da embarcação
  - Gerar relatórios da embarcação
- **Uso Típico:** Capitães de embarcações
- **Escopo:** Acesso limitado à embarcação atribuída

**IMEDIATO**
- **Descrição:** Assistência ao capitão, comando em sua ausência
- **Responsabilidades:**
  - Acesso aos dados da embarcação
  - Registrar dados operacionais
  - Visualizar alertas e recomendações
  - Solicitar manutenções (com aprovação)
- **Uso Típico:** Imediatos, primeiros oficiais
- **Escopo:** Acesso limitado à embarcação atribuída

**OFICIAL_MAQUINAS**
- **Descrição:** Operação e manutenção de sistemas de propulsão
- **Responsabilidades:**
  - Acessar dados operacionais (máquinas)
  - Registrar dados de consumo e performance
  - Visualizar alertas de manutenção
  - Solicitar manutenções de máquinas
- **Uso Típico:** Oficiais de máquinas, engenheiros de bordo
- **Escopo:** Acesso limitado à embarcação atribuída

**TECNICO_MANUTENCAO**
- **Descrição:** Execução de manutenções e limpezas
- **Responsabilidades:**
  - Registrar eventos de manutenção
  - Registrar resultados de limpezas
  - Visualizar histórico de manutenção
  - Acessar especificações técnicas
  - Registrar custos e durações
- **Uso Típico:** Técnicos de manutenção, equipes de limpeza
- **Escopo:** Acesso a múltiplas embarcações (conforme atribuição)

### 2.4 Nível Consultivo e Auditoria

**AUDITOR**
- **Descrição:** Auditoria e verificação de conformidade
- **Responsabilidades:**
  - Acesso de leitura a todos os dados
  - Gerar relatórios de auditoria
  - Visualizar logs de atividades
  - Verificar conformidade com políticas
  - Acompanhar histórico de mudanças
- **Uso Típico:** Auditores internos, consultores
- **Permissões:** Apenas leitura

**ANALISTA_DADOS**
- **Descrição:** Análise de dados e geração de insights
- **Responsabilidades:**
  - Acesso a dados históricos e estatísticos
  - Gerar relatórios e análises
  - Visualizar predições e modelos
  - Exportar dados para análise externa
- **Uso Típico:** Analistas de dados, pesquisadores
- **Permissões:** Leitura e exportação

**CONSULTOR**
- **Descrição:** Acesso limitado para consultoria
- **Responsabilidades:**
  - Visualizar dados específicos (conforme contrato)
  - Gerar relatórios consultivos
  - Acessar análises e recomendações
- **Uso Típico:** Consultores externos
- **Permissões:** Leitura limitada

### 2.5 Nível Básico

**OPERADOR**
- **Descrição:** Operação básica e registro de dados
- **Responsabilidades:**
  - Registrar dados operacionais básicos
  - Visualizar informações da embarcação
  - Receber alertas e notificações
  - Acessar documentação básica
- **Uso Típico:** Operadores de bordo, tripulação
- **Permissões:** Leitura e registro limitado

**VISUALIZADOR**
- **Descrição:** Apenas visualização de dados públicos
- **Responsabilidades:**
  - Visualizar dashboards públicos
  - Acessar relatórios consolidados
  - Visualizar estatísticas gerais
- **Uso Típico:** Stakeholders, visitantes autorizados
- **Permissões:** Apenas leitura de dados públicos

## 3. Matriz de Permissões

### 3.1 Funcionalidades por Papel

| Funcionalidade | Admin | Dir Ops | Ger Frota | Of Seg | Insp | Eng Naval | Capitão | Técnico | Auditor | Operador |
|----------------|-------|---------|-----------|--------|------|-----------|---------|---------|---------|----------|
| **Dashboard** |
| Visualizar KPIs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Visualizar Tendências | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Gestão de Frota** |
| Listar embarcações | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Visualizar detalhes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Criar embarcação | ✓ | ✓ | ✓ | - | - | - | - | - | - | - |
| Editar embarcação | ✓ | ✓ | ✓ | - | - | - | - | - | - | - |
| Excluir embarcação | ✓ | - | - | - | - | - | - | - | - | - |
| **Predições** |
| Predição básica | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Predição avançada | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | - |
| Explicabilidade | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | - |
| **Conformidade NORMAM 401** |
| Verificar conformidade | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Aprovar verificação | ✓ | ✓ | ✓ | ✓ | - | - | - | - | - | - |
| Registrar inspeção | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓* | - | - | - |
| Gerar relatório regulatório | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | - | ✓ | - |
| **Manutenção** |
| Visualizar histórico | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Registrar evento | ✓ | ✓ | ✓ | - | - | - | ✓* | ✓ | - | - |
| Aprovar manutenção | ✓ | ✓ | ✓ | ✓ | - | ✓ | - | - | - | - |
| **Dados Operacionais** |
| Visualizar dados | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Registrar dados | ✓ | ✓ | ✓ | - | - | - | ✓* | ✓ | - | ✓ |
| **Espécies Invasoras** |
| Visualizar análise | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Registrar detecção | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓* | - | - | - |
| **Recomendações** |
| Visualizar recomendações | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ |
| Aprovar ação | ✓ | ✓ | ✓ | ✓ | - | ✓ | - | - | - | - |
| **Administração** |
| Gerenciar usuários | ✓ | - | - | - | - | - | - | - | - | - |
| Gerenciar papéis | ✓ | - | - | - | - | - | - | - | - | - |
| Visualizar logs | ✓ | ✓ | ✓ | ✓ | - | - | - | - | ✓ | - |
| Configurar sistema | ✓ | - | - | - | - | - | - | - | - | - |

* Acesso limitado à embarcação atribuída

### 3.2 Níveis de Acesso por Dados

**Dados Públicos:**
- KPIs gerais do dashboard
- Estatísticas consolidadas
- Informações públicas de embarcações

**Dados Internos:**
- Detalhes operacionais
- Histórico de manutenção
- Dados de conformidade
- Predições e análises

**Dados Confidenciais:**
- Dados financeiros detalhados
- Informações estratégicas
- Logs de auditoria
- Configurações do sistema

**Dados Regulatórios:**
- Relatórios NORMAM 401
- Certificações
- Inspeções oficiais
- Documentação regulatória

## 4. Regras de Negócio

### 4.1 Atribuição de Embarcações

- **Capitão, Imediato, Oficial de Máquinas:** Acesso limitado à embarcação atribuída
- **Técnico de Manutenção:** Acesso a múltiplas embarcações conforme atribuição
- **Outros papéis:** Acesso conforme permissões gerais

### 4.2 Aprovações e Validações

- **Manutenções:** Requer aprovação de Gerente de Frota ou Oficial de Segurança
- **Inspeções NORMAM 401:** Requer validação de Inspetor NORMAM ou Oficial de Segurança
- **Alterações em embarcações:** Requer aprovação de Gerente de Frota ou superior
- **Ações corretivas críticas:** Requer aprovação de Oficial de Segurança

### 4.3 Auditoria e Rastreabilidade

- Todas as ações são registradas com:
  - Usuário responsável
  - Data e hora
  - Tipo de ação
  - Dados alterados (antes/depois)
  - IP de origem

### 4.4 Conformidade Regulatória

- **Inspeções NORMAM 401:** Apenas usuários com papel de Inspetor NORMAM ou superior podem registrar
- **Aprovação de conformidade:** Requer Oficial de Segurança ou superior
- **Relatórios regulatórios:** Podem ser gerados por Inspetor NORMAM, Oficial de Segurança ou superior

## 5. Implementação Técnica

### 5.1 Estrutura de Papéis

```python
class UserRole(str, Enum):
    ADMINISTRADOR_SISTEMA = "administrador_sistema"
    DIRETOR_OPERACOES = "diretor_operacoes"
    GERENTE_FROTA = "gerente_frota"
    OFICIAL_SEGURANCA = "oficial_seguranca"
    INSPETOR_NORMAM = "inspetor_normam"
    ENGENHEIRO_NAVAL = "engenheiro_naval"
    CAPITAO_EMBARCAÇÃO = "capitao_embarcacao"
    IMEDIATO = "imediato"
    OFICIAL_MAQUINAS = "oficial_maquinas"
    TECNICO_MANUTENCAO = "tecnico_manutencao"
    AUDITOR = "auditor"
    ANALISTA_DADOS = "analista_dados"
    CONSULTOR = "consultor"
    OPERADOR = "operador"
    VISUALIZADOR = "visualizador"
```

### 5.2 Permissões

```python
class Permission(str, Enum):
    # Gestão
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_VESSELS = "manage_vessels"
    MANAGE_SYSTEM = "manage_system"
    
    # Visualização
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_VESSELS = "view_vessels"
    VIEW_COMPLIANCE = "view_compliance"
    VIEW_MAINTENANCE = "view_maintenance"
    VIEW_OPERATIONAL_DATA = "view_operational_data"
    
    # Operações
    CREATE_VESSEL = "create_vessel"
    EDIT_VESSEL = "edit_vessel"
    DELETE_VESSEL = "delete_vessel"
    REGISTER_MAINTENANCE = "register_maintenance"
    REGISTER_OPERATIONAL_DATA = "register_operational_data"
    REGISTER_INSPECTION = "register_inspection"
    
    # Aprovações
    APPROVE_MAINTENANCE = "approve_maintenance"
    APPROVE_COMPLIANCE = "approve_compliance"
    APPROVE_ACTION = "approve_action"
    
    # Relatórios
    GENERATE_REPORTS = "generate_reports"
    EXPORT_DATA = "export_data"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # Predições
    VIEW_PREDICTIONS = "view_predictions"
    VIEW_ADVANCED_PREDICTIONS = "view_advanced_predictions"
    VIEW_EXPLANATIONS = "view_explanations"
```

### 5.3 Mapeamento Papel-Permissão

Cada papel possui um conjunto específico de permissões, definido em configuração do sistema.

## 6. Segurança e Conformidade

### 6.1 Princípio do Menor Privilégio

Usuários recebem apenas as permissões mínimas necessárias para suas funções.

### 6.2 Segregação de Funções

Funções conflitantes não podem ser atribuídas ao mesmo usuário:
- Auditor não pode ser Administrador
- Inspetor não pode aprovar suas próprias inspeções

### 6.3 Revisão Periódica

- Revisão de papéis e permissões a cada 6 meses
- Auditoria de acessos trimestral
- Remoção de acessos de usuários inativos

### 6.4 Conformidade Regulatória

- Papéis alinhados com NORMAM 401
- Rastreabilidade completa de ações
- Documentação de aprovações
- Logs de auditoria imutáveis

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025

