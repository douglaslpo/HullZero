# Modelo de Banco de Dados - HullZero

## 1. Visão Geral

O banco de dados do HullZero foi projetado seguindo princípios de normalização (3NF+) para garantir integridade, reduzir redundância e facilitar manutenção. O modelo suporta tanto SQLite (desenvolvimento) quanto PostgreSQL/TimescaleDB (produção).

## 2. Estratégia de Normalização

### 2.1 Forma Normal Aplicada

O banco de dados está normalizado até a **Terceira Forma Normal (3NF)** e além, incluindo:
- Eliminação de dependências transitivas
- Separação de entidades relacionadas
- Tabelas de referência (lookup tables)
- Relacionamentos muitos-para-muitos explícitos

### 2.2 Benefícios da Normalização

- **Integridade:** Redução de inconsistências
- **Manutenibilidade:** Mudanças centralizadas
- **Performance:** Queries mais eficientes
- **Escalabilidade:** Estrutura preparada para crescimento

## 3. Estrutura do Modelo

### 3.1 Tabelas de Referência (Lookup Tables)

Tabelas que armazenam dados padronizados e reutilizáveis:

**vessel_types**
- Tipos de embarcação (tanker, cargo, container, etc.)
- Categoria e descrição

**vessel_classes**
- Classes de embarcação (Suezmax, Aframax, Panamax, etc.)
- Dimensões típicas

**paint_types**
- Tipos de tinta anti-incrustante
- Fabricante, categoria, vida útil típica
- Classificação ambiental

**ports**
- Portos com dados geográficos
- Código do porto, coordenadas, timezone
- Índice de qualidade da água

**routes**
- Rotas entre portos
- Distância, duração típica
- Condições ambientais médias
- Nível de risco

**contractors**
- Contratantes/fornecedores
- Especialização, certificações
- Status (ativo/inativo)

**cargo_types**
- Tipos de carga
- Categoria (líquido, sólido, gás, container)

**fuel_types**
- Tipos de combustível
- Fator de emissão CO₂
- Densidade energética

**invasive_species**
- Espécies invasoras catalogadas
- Nome científico e comum
- Regiões nativas e invasoras
- Taxa de crescimento, dificuldade de remoção

### 3.2 Tabelas Principais

**vessels**
- Informações principais das embarcações
- Dimensões, características técnicas
- Status operacional
- Relacionamentos com tipos, classes, portos

**fouling_measurements**
- Medições de bioincrustação
- Espessura, rugosidade
- Data, local, método de medição
- Relacionamento com embarcação

**operational_data**
- Dados operacionais em tempo real
- Velocidade, potência, consumo
- Condições ambientais
- Timestamp para séries temporais

**maintenance_events**
- Eventos de manutenção
- Tipo (limpeza, pintura, inspeção, reparo)
- Datas, custos, duração
- Método de limpeza utilizado
- Resultados (antes/depois)

**compliance_checks**
- Verificações de conformidade NORMAM 401
- Status, score, violações
- Recomendações
- Histórico completo

**inspections**
- Inspeções realizadas
- Inspetor, data, resultados
- Relacionamento com compliance_checks

**paint_applications**
- Aplicações de tinta
- Tipo de tinta, data, porto
- Contratante, método
- Próxima aplicação prevista

**invasive_species_risks**
- Avaliações de risco de espécies invasoras
- Espécie, embarcação, nível de risco
- Fatores de risco identificados
- Recomendações

### 3.3 Tabelas de Relacionamento (N:N)

**vessel_operating_routes**
- Relacionamento muitos-para-muitos entre vessels e routes
- Frequência de uso, última utilização

**vessel_cargo_types**
- Tipos de carga transportados por cada embarcação
- Percentual de uso

**vessel_fuel_alternatives**
- Combustíveis alternativos disponíveis para embarcação
- Status de implementação

## 4. Relacionamentos

### 4.1 Relacionamentos 1:N

- vessel → fouling_measurements
- vessel → operational_data
- vessel → maintenance_events
- vessel → compliance_checks
- vessel → inspections
- vessel → paint_applications
- vessel → invasive_species_risks
- vessel_type → vessels
- vessel_class → vessels
- port → routes (origin)
- port → routes (destination)
- contractor → maintenance_events
- contractor → paint_applications

### 4.2 Relacionamentos N:N

- vessels ↔ routes (via vessel_operating_routes)
- vessels ↔ cargo_types (via vessel_cargo_types)
- vessels ↔ fuel_types (via vessel_fuel_alternatives)

## 5. Índices e Performance

### 5.1 Índices Implementados

**Índices Primários:**
- Todas as chaves primárias (automático)

**Índices Únicos:**
- imo_number (vessels)
- call_sign (vessels)
- port_code (ports)
- scientific_name (invasive_species)

**Índices de Performance:**
- vessel_id em tabelas relacionadas
- timestamp em séries temporais
- status em vessels
- vessel_type em vessels
- check_date em compliance_checks

### 5.2 Otimizações

**Para Séries Temporais:**
- TimescaleDB (PostgreSQL) para hypertables
- Particionamento por data
- Compressão de dados antigos

**Para Queries Frequentes:**
- Índices compostos em queries comuns
- Materialized views (planejado)

## 6. Constraints e Validações

### 6.1 Constraints de Integridade

**Foreign Keys:**
- Todas as referências têm foreign keys
- ON DELETE CASCADE onde apropriado
- ON DELETE RESTRICT para dados críticos

**Check Constraints:**
- Valores positivos para dimensões
- Ranges válidos para porcentagens (0-100)
- Datas válidas (end_date >= start_date)

**Unique Constraints:**
- IMO number único
- Port code único
- Scientific name único

### 6.2 Validações de Negócio

**Nível de Aplicação:**
- Validação de limites NORMAM 401
- Validação de ranges de valores
- Validação de formatos (IMO, call sign)

**Nível de Banco:**
- NOT NULL em campos obrigatórios
- DEFAULT values onde apropriado
- ENUM types para valores fixos

## 7. Migrações

### 7.1 Estrutura de Migrações

```
src/database/migrations/
├── 001_create_reference_tables.sql
└── 002_create_new_entities.sql
```

### 7.2 Ferramenta de Migração

**Script:** `src/database/migrate.py`

**Comandos:**
```bash
# Verificar status
python -m src.database.migrate check

# Dry-run (simular)
python -m src.database.migrate dry-run

# Executar migrações
python -m src.database.migrate run
```

### 7.3 Versionamento

- Migrações numeradas sequencialmente
- Histórico de execução
- Rollback (planejado)

## 8. Dados Iniciais

### 8.1 Dados de Referência

**Script:** `src/database/init_reference_data.py`

Popula tabelas de referência com:
- Tipos de embarcação padrão
- Classes de embarcação
- Tipos de tinta conhecidos
- Portos principais
- Rotas comuns
- Espécies invasoras catalogadas

### 8.2 Dados de Desenvolvimento

**Script:** `src/database/init_data.py`

Gera dados sintéticos para:
- Embarcações de exemplo
- Medições históricas
- Eventos de manutenção
- Dados operacionais

## 9. Repositórios

### 9.1 Padrão Repository

Cada entidade tem um repositório correspondente:

```python
class VesselRepository:
    def get_by_id(self, vessel_id: str) -> Optional[Vessel]
    def get_all(self) -> List[Vessel]
    def create(self, vessel_data: dict) -> Vessel
    def update(self, vessel_id: str, updates: dict) -> Vessel
    def delete(self, vessel_id: str) -> bool
```

### 9.2 Repositórios Disponíveis

- VesselRepository
- FoulingMeasurementRepository
- OperationalDataRepository
- MaintenanceEventRepository
- ComplianceCheckRepository
- InspectionRepository
- PaintApplicationRepository
- InvasiveSpeciesRiskRepository

## 10. Modelos SQLAlchemy

### 10.1 Modelos Base

**Arquivo:** `src/database/models.py`
- Modelos originais
- Compatibilidade retroativa

### 10.2 Modelos Normalizados

**Arquivo:** `src/database/models_normalized.py`
- Modelos normalizados (3NF+)
- Novas entidades
- Relacionamentos explícitos

### 10.3 Uso

```python
from src.database import get_db, Vessel, VesselType

def get_vessel_with_type(vessel_id: str):
    db = next(get_db())
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    vessel_type = db.query(VesselType).filter(
        VesselType.id == vessel.vessel_type_id
    ).first()
    return vessel, vessel_type
```

## 11. Backup e Recuperação

### 11.1 Estratégia de Backup

**Desenvolvimento (SQLite):**
- Backup manual do arquivo .db
- Versionamento no Git (não recomendado para produção)

**Produção (PostgreSQL):**
- Backup diário automático
- Retenção de 30 dias
- Backup incremental

### 11.2 Recuperação

- Restauração de backup completo
- Point-in-time recovery (PostgreSQL)
- Validação de integridade

## 12. Segurança

### 12.1 Acesso

- Credenciais seguras
- Conexões criptografadas (TLS)
- Roles e permissões (PostgreSQL)

### 12.2 Dados Sensíveis

- Criptografia de dados sensíveis (planejado)
- Mascaramento em logs
- Auditoria de acessos (planejado)

## 13. Monitoramento

### 13.1 Métricas

- Tamanho do banco de dados
- Número de registros por tabela
- Performance de queries
- Uso de índices

### 13.2 Alertas

- Espaço em disco
- Queries lentas
- Erros de conexão
- Deadlocks

## 14. Escalabilidade

### 14.1 Estratégias

**Vertical:**
- Aumento de recursos (CPU, RAM, disco)

**Horizontal:**
- Read replicas
- Sharding (se necessário)
- TimescaleDB para séries temporais

### 14.2 Otimizações Futuras

- Particionamento de tabelas grandes
- Arquivo de dados antigos
- Compressão
- Cache de queries frequentes

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


