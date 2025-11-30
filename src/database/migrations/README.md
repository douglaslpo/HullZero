# Guia de Migração de Banco de Dados - HullZero

## 📋 Visão Geral

Este diretório contém os scripts SQL de migração para normalizar o banco de dados do HullZero, aplicando a 3ª Forma Normal (3NF+) e melhorando a integridade, performance e escalabilidade.

## 📁 Estrutura de Migrações

```
migrations/
├── 001_create_reference_tables.sql  # Tabelas de referência (lookup tables)
├── 002_create_new_entities.sql      # Novas entidades normalizadas
└── README.md                         # Este arquivo
```

## 🚀 Como Executar Migrações

### Opção 1: Usando o Script Python (Recomendado)

```bash
# 1. Verificar status atual das migrações
python -m src.database.migrate check

# 2. Simular execução (dry-run) - não faz alterações
python -m src.database.migrate dry-run

# 3. Executar migrações
python -m src.database.migrate run
```

### Opção 2: Executar SQL Manualmente

```bash
# PostgreSQL/Psql
psql -U hullzero -d hullzero -f 001_create_reference_tables.sql
psql -U hullzero -d hullzero -f 002_create_new_entities.sql

# SQLite
sqlite3 hullzero.db < 001_create_reference_tables.sql
sqlite3 hullzero.db < 002_create_new_entities.sql
```

## 📊 O que cada migração faz

### 001_create_reference_tables.sql

Cria **9 tabelas de referência** (lookup tables) e **3 tabelas de relacionamento N:N**:

#### Tabelas de Referência:
- `vessel_types` - Tipos de embarcação padronizados
- `vessel_classes` - Classes de embarcação (Suezmax, Aframax, etc.)
- `paint_types` - Tipos de tinta com metadados
- `ports` - Portos com dados geográficos
- `routes` - Rotas entre portos
- `contractors` - Contratantes/fornecedores
- `cargo_types` - Tipos de carga
- `fuel_types` - Tipos de combustível
- `invasive_species` - Espécies invasoras catalogadas

#### Tabelas de Relacionamento:
- `vessel_routes` - Relacionamento N:N entre vessels e routes
- `vessel_cargo_types` - Relacionamento N:N entre vessels e cargo_types
- `vessel_fuel_alternatives` - Relacionamento N:N entre vessels e fuel_types

**✅ Sem breaking changes** - Estas tabelas são aditivas e não afetam o código existente.

### 002_create_new_entities.sql

Cria **11 novas entidades normalizadas**:

#### Novas Entidades:
- `paint_applications` - Histórico de aplicações de tinta
- `sensor_calibrations` - Calibrações de sensores
- `inspections` - Inspeções separadas de manutenção
- `compliance_checks` - Verificações de conformidade persistidas
- `compliance_violations` - Violações de conformidade
- `compliance_warnings` - Avisos de conformidade
- `compliance_recommendations` - Recomendações de conformidade
- `risk_factors` - Fatores de risco NORMAM 401
- `risk_recommendations` - Recomendações de risco
- `invasive_species_risks` - Riscos de espécies invasoras persistidos
- `invasive_species_recommendations` - Recomendações de espécies invasoras

**✅ Compatível com código existente** - Estas entidades são novas e não quebram funcionalidades existentes.

## ⚠️ Importante

### Antes de Executar

1. **Backup do Banco de Dados**
   ```bash
   # PostgreSQL
   pg_dump -U hullzero hullzero > backup_$(date +%Y%m%d).sql
   
   # SQLite
   cp hullzero.db hullzero.db.backup
   ```

2. **Verificar Ambiente**
   - Certifique-se de estar no ambiente correto (dev/staging/prod)
   - Verifique se há conexões ativas ao banco
   - Teste primeiro em ambiente de desenvolvimento

3. **Revisar Scripts**
   - Leia os scripts SQL antes de executar
   - Verifique se há dados que precisam ser migrados

### Ordem de Execução

As migrações **devem ser executadas em ordem numérica**:
1. `001_create_reference_tables.sql` (primeiro)
2. `002_create_new_entities.sql` (segundo)

### Rollback

Se precisar reverter as migrações:

```sql
-- Reverter 002
DROP TABLE IF EXISTS invasive_species_recommendations CASCADE;
DROP TABLE IF EXISTS invasive_species_risks CASCADE;
-- ... (repetir para todas as tabelas criadas em 002)

-- Reverter 001
DROP TABLE IF EXISTS vessel_fuel_alternatives CASCADE;
DROP TABLE IF EXISTS vessel_cargo_types CASCADE;
DROP TABLE IF EXISTS vessel_routes CASCADE;
-- ... (repetir para todas as tabelas criadas em 001)
```

**⚠️ ATENÇÃO**: Rollback pode causar perda de dados. Sempre faça backup antes!

## 🔍 Verificação Pós-Migração

Após executar as migrações, verifique:

```bash
# Verificar status
python -m src.database.migrate check

# Verificar tabelas criadas (PostgreSQL)
psql -U hullzero -d hullzero -c "\dt"

# Verificar constraints (PostgreSQL)
psql -U hullzero -d hullzero -c "\d+ vessels"
```

## 📈 Próximos Passos

Após executar as migrações:

1. **Atualizar Modelos SQLAlchemy**
   - Importar modelos de `models_normalized.py`
   - Atualizar `__init__.py` do módulo database

2. **Atualizar Repositórios**
   - Criar repositórios para novas entidades
   - Atualizar repositórios existentes

3. **Migrar Dados Existentes**
   - Migrar dados de JSON para tabelas relacionadas
   - Popular tabelas de referência com dados reais

4. **Atualizar APIs**
   - Atualizar endpoints para usar novo modelo
   - Manter compatibilidade com código legado (views)

## 🐛 Troubleshooting

### Erro: "relation already exists"
- A tabela já foi criada. Isso é normal se você executar a migração novamente.
- O script ignora este erro automaticamente.

### Erro: "foreign key constraint fails"
- Verifique se as tabelas de referência foram criadas primeiro.
- Execute as migrações em ordem numérica.

### Erro: "permission denied"
- Verifique permissões do usuário do banco de dados.
- Certifique-se de que o usuário tem permissões CREATE, ALTER, etc.

## 📚 Documentação Relacionada

- **Análise Completa**: `docs/DATABASE_MODEL_ANALYSIS.md`
- **Resumo Executivo**: `docs/DATABASE_NORMALIZATION_SUMMARY.md`
- **Modelos SQLAlchemy**: `src/database/models_normalized.py`
- **Script de Migração**: `src/database/migrate.py`

---

**Última Atualização**: 2025-01-XX  
**Versão**: 1.0

