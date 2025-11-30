# Sistema de Acesso e Controle - HullZero

## Resumo Executivo

O sistema HullZero implementa controle de acesso baseado em papéis (RBAC) alinhado com a hierarquia e responsabilidades do setor naval brasileiro, garantindo segurança, conformidade regulatória e rastreabilidade completa.

## Características Principais

### Autenticação
- Sistema JWT (JSON Web Tokens) com access e refresh tokens
- Tokens de acesso expiram em 30 minutos
- Tokens de refresh expiram em 7 dias
- Hash de senhas com bcrypt
- Suporte a OAuth2 Password Flow

### Autorização
- 15 papéis definidos baseados em hierarquia naval
- 24 permissões granulares
- Atribuição de embarcações a usuários específicos
- Verificação de permissões em tempo real
- Segregação de funções

### Auditoria
- Logs completos de todas as ações
- Rastreabilidade de mudanças
- Histórico de acessos
- Informações de IP e user agent

## Papéis Implementados

### Nível Executivo
- **Administrador Sistema:** Acesso total, gestão de usuários e configurações
- **Diretor Operações:** Visão estratégica completa
- **Gerente Frota:** Gestão operacional da frota

### Nível Técnico/Regulatório
- **Oficial Segurança:** Conformidade NORMAM 401, aprovações
- **Inspetor NORMAM:** Inspeções certificadas, relatórios regulatórios
- **Engenheiro Naval:** Análise técnica, validação de métodos

### Nível Operacional
- **Capitão Embarcação:** Comando completo da embarcação atribuída
- **Imediato:** Assistência ao capitão
- **Oficial Máquinas:** Operação de sistemas de propulsão
- **Técnico Manutenção:** Execução de manutenções e limpezas

### Nível Consultivo
- **Auditor:** Auditoria e verificação de conformidade
- **Analista Dados:** Análise de dados e geração de insights
- **Consultor:** Acesso limitado para consultoria

### Nível Básico
- **Operador:** Operação básica e registro de dados
- **Visualizador:** Apenas visualização de dados públicos

## Matriz de Permissões

Cada papel possui um conjunto específico de permissões que determina:
- Quais funcionalidades podem acessar
- Quais operações podem realizar
- Quais dados podem visualizar
- Quais ações podem aprovar

A matriz completa está documentada em `docs/regulatorio/PAPEIS_E_PERMISSOES.md`.

## Conformidade Regulatória

### NORMAM 401
- Inspeções podem ser registradas apenas por Inspetor NORMAM ou superior
- Aprovações de conformidade requerem Oficial de Segurança ou superior
- Rastreabilidade completa de todas as verificações
- Documentação automática de inspeções

### Segregação de Funções
- Inspetor não pode aprovar suas próprias inspeções
- Auditor não pode ser Administrador
- Validações automáticas de conflitos

## Segurança

### Implementado
- Hash de senhas com bcrypt
- Tokens JWT assinados
- Validação de tokens em cada requisição
- Verificação de permissões granular
- Logs de auditoria imutáveis

### Recomendações para Produção
- Secret key forte e aleatória
- HTTPS obrigatório
- Rate limiting
- Bloqueio de conta após tentativas falhadas
- Validação de força de senha
- MFA (Multi-Factor Authentication) - planejado

## Benefícios

### Segurança
- Controle granular de acesso
- Rastreabilidade completa
- Prevenção de acesso não autorizado
- Conformidade com regulamentações

### Operacional
- Hierarquia clara de responsabilidades
- Atribuição de embarcações específicas
- Aprovações controladas
- Auditoria facilitada

### Regulatório
- Conformidade com NORMAM 401
- Documentação automática
- Rastreabilidade de inspeções
- Validação de certificações

## Implementação

O sistema está totalmente implementado e pronto para uso:

1. **Modelos de Dados:** Criados e normalizados
2. **Serviços de Autenticação:** JWT completo
3. **Endpoints de API:** Login, refresh, gestão de usuários
4. **Dependências FastAPI:** Proteção de endpoints
5. **Inicialização:** Scripts automatizados
6. **Documentação:** Completa e detalhada

## Próximos Passos

1. Executar migração de banco de dados (003_create_auth_tables.sql)
2. Inicializar papéis e permissões (init_auth_data.py)
3. Criar usuários conforme necessidade
4. Atribuir papéis aos usuários
5. Configurar atribuições de embarcações
6. Integrar autenticação no frontend

---

**Versão:** 1.0  
**Data:** Janeiro 2025
