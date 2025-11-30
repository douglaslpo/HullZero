# Análise de Dados Reais - HullZero

## 📊 Estrutura de Dados Identificada

### 1. Dados AIS (Automatic Identification System)
**Localização**: `dados/Dados AIS frota TP/*.csv`

**Estrutura**:
- `NOME`: Nome da embarcação
- `DATAHORA`: Timestamp da posição
- `RUMO`: Direção (heading) em graus
- `VELOCIDADE`: Velocidade em nós
- `LATITUDE`: Latitude
- `LONGITUDE`: Longitude

**Quantidade**: 21 arquivos CSV (um por embarcação)

**Uso**:
- Importar para `operational_data`
- Usar para calcular métricas operacionais
- Usar para previsões de IA

---

### 2. Dados de Consumo
**Localização**: `dados/ResultadoQueryConsumo.csv`

**Estrutura**:
- `SESSION_ID`: ID da sessão
- `CONSUMED_QUANTITY`: Quantidade consumida
- `DESCRIPTION`: Descrição do combustível

**Quantidade**: 87.737 registros

**Uso**:
- Importar para `operational_data.fuel_consumption_kg_h`
- Usar para calcular impacto de bioincrustação
- Usar para treinar modelos de IA

---

### 3. Dados de Eventos
**Localização**: `dados/ResultadoQueryEventos.csv`

**Estrutura**:
- `sessionId`: ID da sessão
- `shipName`: Nome da embarcação
- `class`: Classe da embarcação
- `eventName`: Nome do evento (NAVEGACAO, etc.)
- `startGMTDate`: Data de início
- `endGMTDate`: Data de fim
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

**Quantidade**: 50.904 registros

**Uso**:
- Importar para `operational_data` (navegação)
- Importar para `maintenance_events` (eventos de manutenção)
- Usar para análise operacional

---

### 4. Dados de Navios
**Localização**: `dados/Dados navios Hackathon.xlsx`

**Estrutura**: (a ser analisada com pandas/openpyxl)

**Uso**:
- Atualizar dados de embarcações
- Complementar informações da frota

---

## 🔄 Mapeamento de Dados

### Dados AIS → `operational_data`
```python
{
    "vessel_id": vessel_id,
    "timestamp": DATAHORA,
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "speed_knots": VELOCIDADE,
    "heading": RUMO,
}
```

### Dados de Consumo → `operational_data`
```python
{
    "vessel_id": vessel_id (mapeado de SESSION_ID),
    "timestamp": timestamp (extraído de SESSION_ID ou data),
    "fuel_consumption_kg_h": CONSUMED_QUANTITY,
}
```

### Dados de Eventos → `operational_data` + `maintenance_events`
```python
# Para operational_data:
{
    "vessel_id": vessel_id (mapeado de shipName),
    "timestamp": startGMTDate,
    "latitude": decLatitude,
    "longitude": decLongitude,
    "speed_knots": speed,
    "depth_m": (aftDraft + fwdDraft + midDraft) / 3,
}

# Para maintenance_events (se eventName for limpeza/manutenção):
{
    "vessel_id": vessel_id,
    "event_type": "cleaning" ou "inspection",
    "start_date": startGMTDate,
    "end_date": endGMTDate,
    "duration_hours": duration,
}
```

---

## 🤖 Integração com Modelos de IA

### Features Extraídas dos Dados Reais

#### Para `VesselFeatures` (fouling_prediction.py):
```python
{
    "vessel_id": vessel_id,
    "time_since_cleaning_days": calculado de maintenance_events,
    "water_temperature_c": de operational_data (ou padrão 25.0),
    "salinity_psu": de operational_data (ou padrão 35.0),
    "time_in_port_hours": calculado de speed_knots < 1.0,
    "average_speed_knots": média de operational_data,
    "route_region": de vessel.operating_routes,
    "paint_type": de vessel.paint_type,
    "vessel_type": de vessel.vessel_type,
    "hull_area_m2": de vessel.hull_area_m2,
}
```

#### Para `AdvancedVesselFeatures` (advanced_fouling_prediction.py):
```python
{
    # Todas as features básicas acima +
    "paint_age_days": calculado de vessel.paint_application_date,
    "port_water_quality_index": de operational_data.port_water_quality_index,
    "seasonal_factor": calculado de timestamp,
    "chlorophyll_a_concentration": de operational_data,
    "dissolved_oxygen": de operational_data,
    "ph_level": de operational_data,
    "turbidity": de operational_data,
    "current_velocity": de operational_data,
    "depth_m": de operational_data,
}
```

#### Para `ConsumptionFeatures` (fuel_impact.py):
```python
{
    "speed_knots": de operational_data,
    "engine_power_kw": de operational_data,
    "rpm": de operational_data,
    "water_temperature_c": de operational_data,
    "wind_speed_knots": de operational_data,
    "wave_height_m": de operational_data,
    "current_speed_knots": de operational_data,
    "vessel_load_percent": calculado de displacement,
    "fouling_thickness_mm": de fouling_data (ou predição),
    "fouling_roughness_um": de fouling_data (ou predição),
    "hull_area_m2": de vessel,
    "vessel_type": de vessel,
}
```

---

## 📈 Fluxo de Dados

### 1. Importação
```
CSV/Excel → import_real_data.py → Banco de Dados
```

### 2. Carregamento para Modelos
```
Banco de Dados → data_loader.py → Features → Modelos de IA
```

### 3. Predição
```
Features → Modelos de IA → Predições → Banco de Dados (fouling_data)
```

### 4. Apresentação
```
Banco de Dados → API Endpoints → Frontend
```

---

## 🔧 Mudanças Necessárias

### Backend

1. **Atualizar `db_endpoints.py`**:
   - Usar `data_loader.get_vessel_features_from_db()` para buscar features reais
   - Gerar predições baseadas em dados reais
   - Salvar predições em `fouling_data`

2. **Atualizar modelos de IA**:
   - Aceitar dados do banco via `data_loader`
   - Treinar com dados históricos reais (se disponíveis)
   - Usar features reais em vez de valores padrão

3. **Criar endpoint de importação**:
   - Endpoint para executar importação de dados
   - Endpoint para verificar status da importação

### Frontend

1. **Atualizar serviços**:
   - Garantir que endpoints usem dados reais
   - Tratar casos onde dados não estão disponíveis

2. **Atualizar visualizações**:
   - Mostrar dados reais quando disponíveis
   - Fallback para dados sintéticos apenas se necessário

---

## ✅ Checklist de Implementação

- [x] Analisar estrutura de dados
- [x] Criar script de importação
- [x] Criar data_loader para modelos de IA
- [ ] Atualizar endpoints para usar dados reais
- [ ] Atualizar modelos para consumir dados reais
- [ ] Testar importação completa
- [ ] Validar predições com dados reais
- [ ] Atualizar frontend para mostrar dados reais

---

## 📝 Notas Importantes

1. **Mapeamento de Nomes**: Os nomes nos CSVs podem não corresponder exatamente aos IDs no banco. O script de importação faz mapeamento flexível.

2. **Dados Faltantes**: Nem todos os campos estarão disponíveis em todos os registros. Usar valores padrão quando necessário.

3. **Performance**: Com 87k+ registros de consumo e 50k+ de eventos, a importação pode demorar. Considerar processamento em lote.

4. **Validação**: Validar dados antes de importar (datas, coordenadas, valores numéricos).

5. **Incremental**: Considerar importação incremental para atualizações futuras.

