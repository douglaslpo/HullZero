# Documentação HullZero

Este diretório contém a documentação completa do sistema HullZero, organizada por categoria.

## Estrutura da Documentação

### Executivo

Documentos para gestão e tomada de decisão:

- **[PROPOSTA_EXECUTIVA.md](executivo/PROPOSTA_EXECUTIVA.md)**
  - Contexto e problema
  - Solução proposta
  - Benefícios esperados
  - Arquitetura da solução
  - Plano de implementação
  - Investimento e ROI
  - Riscos e mitigações

- **[RESUMO_EXECUTIVO.md](executivo/RESUMO_EXECUTIVO.md)**
  - Visão geral concisa
  - Problema e solução
  - Benefícios principais
  - Tecnologia
  - Investimento
  - Próximos passos

- **[ANALISE_ROI.md](executivo/ANALISE_ROI.md)**
  - Metodologia de análise
  - Investimento inicial
  - Custos operacionais
  - Benefícios e economias
  - Análise de ROI detalhada
  - Projeção de 5 anos
  - Análise de sensibilidade

### Frontend

Documentação técnica do frontend:

- **[ARQUITETURA_FRONTEND.md](frontend/ARQUITETURA_FRONTEND.md)**
  - Stack tecnológico
  - Estrutura de diretórios
  - Arquitetura de componentes
  - Gerenciamento de estado
  - Comunicação com API
  - Roteamento
  - Visualização de dados
  - Acessibilidade
  - Performance

- **[COMPONENTES.md](frontend/COMPONENTES.md)**
  - Componentes de interface
  - Páginas principais
  - Padrões de desenvolvimento
  - Tratamento de erros
  - Formatação de dados
  - Acessibilidade
  - Performance

### Regulatório

Documentação sobre conformidade e regulamentações:

- **[NORMAM_401.md](regulatorio/NORMAM_401.md)**
  - Contexto legal
  - Requisitos principais
  - Limites e classificações
  - Documentação e rastreabilidade
  - Penalizações
  - Implementação no HullZero
  - Métodos de controle aceitos
  - Boas práticas

- **[CONFORMIDADE.md](regulatorio/CONFORMIDADE.md)**
  - Visão geral do sistema
  - Arquitetura do sistema
  - Limites e classificações
  - Verificação de conformidade
  - Predição de riscos
  - Recomendações
  - Relatórios
  - Integração com inspeções
  - Alertas e notificações
  - Auditoria

- **[PAPEIS_E_PERMISSOES.md](regulatorio/PAPEIS_E_PERMISSOES.md)**
  - Hierarquia de papéis
  - Matriz de permissões
  - Regras de negócio
  - Atribuição de embarcações
  - Aprovações e validações
  - Conformidade regulatória
  - Implementação técnica

### Técnico

Documentação técnica detalhada:

- **[ARQUITETURA_TECNICA.md](tecnico/ARQUITETURA_TECNICA.md)**
  - Visão geral da arquitetura
  - Camadas da aplicação
  - Padrões arquiteturais
  - Comunicação entre componentes
  - Banco de dados
  - Modelos de IA
  - Segurança
  - Performance
  - Escalabilidade
  - Monitoramento
  - Deploy e DevOps
  - Testes

- **[MODELOS_IA.md](tecnico/MODELOS_IA.md)**
  - Visão geral
  - Arquitetura de modelos
  - Modelos implementados
  - Treinamento e validação
  - Feature engineering
  - Otimização de hiperparâmetros
  - Atualização de modelos
  - Limitações
  - Uso dos modelos

- **[BANCO_DADOS.md](tecnico/BANCO_DADOS.md)**
  - Visão geral
  - Estratégia de normalização
  - Estrutura do modelo
  - Relacionamentos
  - Índices e performance
  - Constraints e validações
  - Migrações
  - Dados iniciais
  - Repositórios
  - Modelos SQLAlchemy
  - Backup e recuperação
  - Segurança
  - Monitoramento
  - Escalabilidade

- **[API_REFERENCE.md](tecnico/API_REFERENCE.md)**
  - Visão geral
  - Base URL
  - Autenticação
  - Formato de resposta
  - Endpoints principais
  - Códigos de status HTTP
  - Rate limiting
  - Versionamento
  - Documentação interativa
  - Exemplos de uso
  - Tratamento de erros
  - Webhooks

- **[AUTENTICACAO_AUTORIZACAO.md](tecnico/AUTENTICACAO_AUTORIZACAO.md)**
  - Arquitetura do sistema
  - Modelos de dados
  - Papéis e permissões
  - Endpoints de autenticação
  - Uso em endpoints
  - Inicialização
  - Segurança
  - Configuração
  - Integração com frontend
  - Exemplos de uso

- **[GUIA_DEPLOY.md](tecnico/GUIA_DEPLOY.md)**
  - Deploy local
  - Deploy com Docker
  - Deploy em servidor Linux
  - Deploy em cloud (AWS, Azure, GCP)
  - Configuração de serviços
  - SSL e segurança
  - Backup e monitoramento
  - Troubleshooting

## Como Usar Esta Documentação

### Para Gestores e Executivos

Comece pelos documentos em `executivo/`:
1. Leia o **RESUMO_EXECUTIVO.md** para uma visão geral rápida
2. Consulte **PROPOSTA_EXECUTIVA.md** para detalhes completos
3. Revise **ANALISE_ROI.md** para análise financeira detalhada

### Para Desenvolvedores Frontend

Consulte os documentos em `frontend/`:
1. **ARQUITETURA_FRONTEND.md** para entender a estrutura geral
2. **COMPONENTES.md** para detalhes de componentes e páginas

### Para Desenvolvedores Backend

Consulte os documentos em `tecnico/`:
1. **ARQUITETURA_TECNICA.md** para arquitetura geral
2. **API_REFERENCE.md** para referência completa da API
3. **MODELOS_IA.md** para entender os modelos de IA
4. **BANCO_DADOS.md** para modelo de dados

### Para Equipe de Conformidade

Consulte os documentos em `regulatorio/`:
1. **NORMAM_401.md** para requisitos regulatórios
2. **CONFORMIDADE.md** para sistema de conformidade

## Convenções

- Todos os documentos estão em Markdown
- Código de exemplo está em blocos de código
- Diagramas estão em formato texto (ASCII art)
- Referências cruzadas usam links relativos

## Atualizações

Esta documentação é atualizada conforme o sistema evolui. A versão de cada documento está indicada no rodapé.

**Última Atualização Geral:** Janeiro 2025

---

**Versão:** 1.0


