# 📊 Análise: Dados Reais vs Banco de Dados - HullZero

## 🎯 Objetivo

Analisar se o banco de dados atual suporta os dados reais disponíveis, se faz sentido substituir dados sintéticos pelos reais, e se esses dados resolvem o problema de bioincrustação.

---

## 📋 1. Dados Disponíveis (do Notebook)

### 1.1 Dados AIS (20 arquivos CSV)
**Estrutura identificada:**
- `NOME`: Nome da embarcação (ex: "BRUNO LIMA")
- `DATAHORA`: Timestamp (YYYY-MM-DD HH:MM:SS)
- `RUMO`: Heading em graus (ex: 58.1)
- `VELOCIDADE`: Velocidade em nós (ex: 12.2)
- `LATITUDE`: Latitude (ex: -24.954948)
- `LONGITUDE`: Longitude (ex: -46.857981)

**Volume:** ~30MB total, milhares de registros por navio

### 1.2 Dados de Consumo (ResultadoQueryConsumo.csv)
**Estrutura identificada:**
- `SESSION_ID`: ID da sessão (ex: 39800000086)
- `CONSUMED_QUANTITY`: Quantidade consumida (ex: 47.0000)
- `DESCRIPTION`: Tipo de combustível (ex: "LSHFO 0.5")

**Volume:** 87.737+ registros (~2.3MB)

### 1.3 Dados de Eventos (ResultadoQueryEventos.csv)
**Estrutura identificada:**
- `sessionId`: ID da sessão
- `shipName`: Nome da embarcação
- `class`: Classe da embarcação
- `eventName`: Tipo de evento (ex: "NAVEGACAO")
- `startGMTDate`, `endGMTDate`: Datas de início/fim
- `duration`: Duração
- `distance`: Distância
- `aftDraft`, `fwdDraft`, `midDraft`: Calados
- `TRIM`: Trim
- `displacement`: Deslocamento
- `beaufortScale`: Escala Beaufort
- `seaCondition`: Condição do mar
- `speed`, `speedGps`: Velocidades
- `Porto`: Porto
- `decLatitude`, `decLongitude`: Coordenadas

**Volume:** 50.904+ registros (~8.2MB)

### 1.4 Dados de Navios (Dados navios Hackathon.xlsx)
**Estrutura:** A ser analisada (Excel com múltiplas abas)

---

## 🗄️ 2. Schema do Banco de Dados Atual

### 2.1 Tabela `vessels` (Embarcações)
**Campos relevantes:**
- ✅ `id`, `name`, `imo_number`, `call_sign`
- ✅ `vessel_type`, `vessel_class`, `fleet_category`
- ✅ `length_m`, `width_m`, `draft_m`, `hull_area_m2`
- ✅ `displacement_tonnes`, `dwt`
- ✅ `max_speed_knots`, `typical_speed_knots`
- ✅ `engine_power_kw`, `fuel_type`
- ✅ `home_port`, `status`

**Compatibilidade:** ✅ **COMPATÍVEL** - Suporta dados de navios

### 2.2 Tabela `operational_data` (Dados Operacionais)
**Campos relevantes:**
- ✅ `vessel_id`, `timestamp`
- ✅ `latitude`, `longitude` → **Mapeia AIS**
- ✅ `speed_knots` → **Mapeia AIS VELOCIDADE**
- ✅ `heading` → **Mapeia AIS RUMO**
- ✅ `fuel_consumption_kg_h` → **Mapeia CONSUMED_QUANTITY**
- ✅ `engine_power_kw`, `rpm`
- ✅ `water_temperature_c`, `salinity_psu`
- ✅ `wind_speed_knots`, `wave_height_m`
- ✅ `cargo_load_percent`

**Compatibilidade:** ✅ **COMPATÍVEL** - Suporta dados AIS e consumo

**Campos adicionais no banco (não nos dados reais):**
- `current_velocity`, `depth_m`
- `port_water_quality_index`, `chlorophyll_a_concentration`
- `dissolved_oxygen`, `ph_level`, `turbidity`

**Análise:** Banco tem campos extras que podem ser preenchidos com valores padrão ou estimados.

### 2.3 Tabela `maintenance_events` (Eventos de Manutenção)
**Campos relevantes:**
- ✅ `vessel_id`, `start_date`, `end_date`
- ✅ `event_type` → **Pode mapear eventName**
- ✅ `location` → **Pode mapear Porto**
- ✅ `description`
- ✅ `fouling_thickness_before_mm`, `fouling_thickness_after_mm`
- ✅ `roughness_before_um`, `roughness_after_um`
- ✅ `cost_brl`, `cost_usd`

**Compatibilidade:** ⚠️ **PARCIALMENTE COMPATÍVEL**

**Problemas identificados:**
- Dados de eventos têm `eventName` como "NAVEGACAO", mas não especificam se é manutenção
- Não há dados diretos de `fouling_thickness` ou `roughness` nos eventos
- Dados de eventos parecem ser operacionais, não de manutenção

### 2.4 Tabela `fouling_data` (Dados de Bioincrustação)
**Campos:**
- ✅ `vessel_id`, `timestamp`
- ✅ `estimated_thickness_mm`
- ✅ `estimated_roughness_um`
- ✅ `fouling_severity`
- ✅ `predicted_fuel_impact_percent`
- ✅ `predicted_co2_impact_kg`

**Compatibilidade:** ❌ **NÃO COMPATÍVEL DIRETAMENTE**

**Problema crítico:**
- **Os dados reais NÃO contêm medições diretas de bioincrustação!**
- Não há `thickness_mm` ou `roughness_um` nos dados AIS, consumo ou eventos
- Esses dados precisam ser **PREDITOS** pelos modelos de IA

---

## 🔍 3. Análise de Compatibilidade Detalhada

### 3.1 Mapeamento de Dados AIS → `operational_data`

| Dado AIS | Campo Banco | Status |
|----------|-------------|--------|
| `NOME` | `vessel_id` (via lookup) | ✅ Mapeável |
| `DATAHORA` | `timestamp` | ✅ Compatível |
| `LATITUDE` | `latitude` | ✅ Compatível |
| `LONGITUDE` | `longitude` | ✅ Compatível |
| `VELOCIDADE` | `speed_knots` | ✅ Compatível |
| `RUMO` | `heading` | ✅ Compatível |

**Conclusão:** ✅ **100% compatível**

### 3.2 Mapeamento de Consumo → `operational_data`

| Dado Consumo | Campo Banco | Status |
|--------------|-------------|--------|
| `SESSION_ID` | Não mapeável diretamente | ⚠️ Precisa lookup |
| `CONSUMED_QUANTITY` | `fuel_consumption_kg_h` | ✅ Compatível |
| `DESCRIPTION` | `fuel_type` (via parse) | ⚠️ Precisa parse |

**Problemas:**
- `SESSION_ID` não tem correspondência direta com `vessel_id` ou `timestamp`
- Precisa de tabela intermediária ou lógica de mapeamento

**Conclusão:** ⚠️ **70% compatível** - Requer mapeamento adicional

### 3.3 Mapeamento de Eventos → `operational_data` / `maintenance_events`

| Dado Evento | Campo Banco | Status |
|-------------|-------------|--------|
| `shipName` | `vessel_id` (via lookup) | ✅ Mapeável |
| `startGMTDate` | `start_date` / `timestamp` | ✅ Compatível |
| `endGMTDate` | `end_date` | ✅ Compatível |
| `duration` | `duration_hours` | ✅ Compatível |
| `speed`, `speedGps` | `speed_knots` | ✅ Compatível |
| `decLatitude`, `decLongitude` | `latitude`, `longitude` | ✅ Compatível |
| `Porto` | `location` | ✅ Compatível |
| `displacement` | `displacement_tonnes` (vessel) | ⚠️ Tabela diferente |
| `aftDraft`, `fwdDraft`, `midDraft` | Não existe no banco | ❌ Não mapeável |
| `TRIM` | Não existe no banco | ❌ Não mapeável |
| `beaufortScale` | Não existe no banco | ❌ Não mapeável |
| `seaCondition` | Não existe no banco | ❌ Não mapeável |

**Conclusão:** ⚠️ **60% compatível** - Muitos campos não mapeáveis

### 3.4 Dados de Bioincrustação

**Problema crítico identificado:**
- ❌ **Nenhum dos dados reais contém medições de bioincrustação!**
- ❌ Não há `thickness_mm`, `roughness_um` ou qualquer métrica de fouling
- ✅ **Isso é esperado** - bioincrustação precisa ser **PREDITA** pelos modelos

**Conclusão:** ✅ **Compatível via predição** - Os modelos devem gerar esses dados

---

## 💡 4. Análise: Faz Sentido Substituir Dados Sintéticos?

### 4.1 Vantagens dos Dados Reais

✅ **Dados operacionais reais:**
- Posições GPS reais (AIS)
- Velocidades reais
- Consumo real de combustível
- Eventos reais de navegação
- Nomes reais de embarcações da Transpetro

✅ **Volume significativo:**
- 87k+ registros de consumo
- 50k+ registros de eventos
- Milhares de pontos AIS por navio

✅ **Validação de modelos:**
- Modelos podem ser testados com dados reais
- Predições podem ser comparadas com consumo real

### 4.2 Desvantagens / Limitações

❌ **Dados incompletos:**
- Não há medições diretas de bioincrustação
- Faltam campos importantes (calados, trim, condições do mar)
- Não há dados de manutenção/limpeza

❌ **Mapeamento complexo:**
- `SESSION_ID` não mapeia diretamente
- Nomes de navios podem não corresponder aos IDs
- Dados de eventos misturam operação e manutenção

❌ **Dados sintéticos podem ser mais completos:**
- Dados sintéticos podem ter todos os campos necessários
- Dados sintéticos podem ter dados de bioincrustação simulados

### 4.3 Recomendação: **ABORDAGEM HÍBRIDA**

✅ **Usar dados reais para:**
1. **Dados operacionais** (`operational_data`)
   - Importar dados AIS (posição, velocidade, heading)
   - Importar dados de consumo quando possível mapear
   - Importar eventos operacionais (navegação)

2. **Validação de modelos**
   - Usar consumo real para validar predições de impacto
   - Comparar predições com dados reais

3. **Dados de embarcações**
   - Atualizar informações de navios com dados do Excel

❌ **Manter dados sintéticos para:**
1. **Dados de bioincrustação** (`fouling_data`)
   - Gerar via modelos de predição baseados em dados operacionais reais
   - Usar dados sintéticos apenas como fallback/treinamento

2. **Dados de manutenção** (`maintenance_events`)
   - Se não houver dados reais de manutenção, manter sintéticos
   - Ou gerar recomendações baseadas em predições

3. **Campos faltantes**
   - Preencher com valores estimados ou padrões

---

## 🎯 5. Análise: Resolvemos o Problema com Esses Dados?

### 5.1 O Problema: Monitoramento e Predição de Bioincrustação

**Requisitos:**
1. ✅ Monitorar embarcações em tempo real
2. ✅ Predizer bioincrustação futura
3. ✅ Calcular impacto em consumo de combustível
4. ✅ Avaliar conformidade NORMAM 401
5. ✅ Recomendar ações corretivas

### 5.2 Como os Dados Reais Ajudam

✅ **Dados AIS:**
- Permitem rastreamento real de embarcações
- Fornecem dados de velocidade e posição para modelos
- Permitem calcular tempo em porto, rotas, etc.

✅ **Dados de Consumo:**
- Permitem validar predições de impacto de bioincrustação
- Fornecem baseline real de consumo
- Permitem calcular economia real vs. predita

✅ **Dados de Eventos:**
- Fornecem contexto operacional
- Permitem identificar padrões de operação
- Podem indicar quando navios estão em porto (oportunidade de limpeza)

### 5.3 Limitações Identificadas

❌ **Falta de dados diretos de bioincrustação:**
- Não podemos validar predições com medições reais
- Dependemos 100% dos modelos de IA

❌ **Falta de dados de manutenção:**
- Não sabemos quando limpezas foram feitas
- Não podemos validar recomendações

❌ **Dados incompletos:**
- Faltam campos importantes (calados, trim, condições do mar)
- Alguns campos precisam ser estimados

### 5.4 Conclusão: **SIM, mas com ressalvas**

✅ **Os dados reais RESOLVEM parcialmente o problema:**
- Fornecem base operacional real
- Permitem predições mais realistas
- Permitem validação de impacto em consumo

⚠️ **Mas NÃO resolvem completamente:**
- Ainda dependemos de modelos para predição de bioincrustação
- Falta validação com medições reais
- Falta histórico de manutenção

**Recomendação:** Usar dados reais como base, mas complementar com:
1. Predições de modelos de IA para bioincrustação
2. Dados sintéticos ou estimados para campos faltantes
3. Recomendações baseadas em análise de padrões

---

## 📊 6. Plano de Ação Recomendado

### Fase 1: Importação de Dados Reais (Prioritário)
1. ✅ Importar dados AIS → `operational_data`
2. ✅ Importar dados de consumo (quando mapeável) → `operational_data`
3. ✅ Importar dados de eventos operacionais → `operational_data`
4. ✅ Atualizar informações de navios → `vessels`

### Fase 2: Geração de Dados de Bioincrustação
1. ✅ Executar modelos de predição baseados em dados operacionais reais
2. ✅ Gerar `fouling_data` com predições
3. ✅ Calcular impacto em consumo baseado em dados reais

### Fase 3: Validação e Ajuste
1. ✅ Comparar predições com consumo real
2. ✅ Ajustar modelos se necessário
3. ✅ Gerar recomendações baseadas em dados reais

### Fase 4: Complementação
1. ⚠️ Preencher campos faltantes com estimativas
2. ⚠️ Gerar dados de manutenção baseados em recomendações
3. ⚠️ Criar histórico sintético se necessário para treinamento

---

## ✅ 7. Resumo Executivo

### Compatibilidade do Banco de Dados
- ✅ **Dados AIS:** 100% compatível
- ⚠️ **Dados de Consumo:** 70% compatível (requer mapeamento)
- ⚠️ **Dados de Eventos:** 60% compatível (muitos campos não mapeáveis)
- ❌ **Dados de Bioincrustação:** Não existem nos dados reais (precisam ser preditos)

### Recomendação Final
✅ **SIM, usar dados reais**, mas com abordagem híbrida:
- Importar dados operacionais reais (AIS, consumo, eventos)
- Gerar dados de bioincrustação via modelos de IA
- Complementar com dados sintéticos/estimados quando necessário
- **NÃO apagar dados anteriores completamente** - manter como backup/treinamento

### Resolução do Problema
✅ **SIM, os dados reais ajudam a resolver o problema**, mas:
- Fornecem base operacional real
- Permitem validação de modelos
- Permitem predições mais realistas
- **Mas ainda dependemos de modelos de IA para bioincrustação**

---

## 🔧 8. Próximos Passos Técnicos

1. **Criar script de mapeamento** de nomes de navios para IDs
2. **Aprimorar script de importação** para lidar com campos faltantes
3. **Criar pipeline de predição** que usa dados operacionais reais
4. **Implementar validação** comparando predições com consumo real
5. **Documentar gaps** e criar estratégia de preenchimento

---

**Data da Análise:** 2025-01-XX  
**Analista:** Sistema HullZero  
**Status:** ✅ **APROVADO PARA IMPLEMENTAÇÃO COM RESERVAS**

