# Referência da API - HullZero

## 1. Visão Geral

A API do HullZero é uma API REST construída com FastAPI, fornecendo endpoints para acesso a todos os recursos do sistema. A API segue padrões RESTful e utiliza JSON para serialização de dados.

## 2. Base URL

**Desenvolvimento:** `http://localhost:8000`  
**Produção:** `https://api.hullzero.com` (planejado)

## 3. Autenticação

Atualmente não implementada. Planejado:
- JWT (JSON Web Tokens)
- OAuth2
- API Keys

## 4. Formato de Resposta

### 4.1 Sucesso

```json
{
  "data": { ... },
  "status": "success"
}
```

### 4.2 Erro

```json
{
  "detail": "Mensagem de erro",
  "status": "error",
  "code": "ERROR_CODE"
}
```

## 5. Endpoints Principais

### 5.1 Health Check

**GET** `/health`

Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 5.2 Dashboard

**GET** `/api/dashboard/kpis`

Retorna KPIs principais do dashboard.

**Resposta:**
```json
{
  "monitored_vessels": 28,
  "economy_brl": 2800000,
  "co2_reduction_tonnes": 1750,
  "compliance_rate_percent": 95.5
}
```

**GET** `/api/dashboard/trends`

Retorna dados de tendências para gráficos.

**Query Parameters:**
- `months` (int, opcional): Número de meses (padrão: 6)

**Resposta:**
```json
{
  "trends": [
    {
      "month": "2024-07",
      "economy_brl": 450000,
      "co2_tonnes": 280,
      "compliance_rate_percent": 92.5,
      ...
    }
  ]
}
```

### 5.3 Embarcações

**GET** `/api/vessels`

Lista todas as embarcações.

**Query Parameters:**
- `type` (string, opcional): Filtrar por tipo
- `class` (string, opcional): Filtrar por classe
- `status` (string, opcional): Filtrar por status

**Resposta:**
```json
{
  "vessels": [
    {
      "id": "TP_SUEZMAX_MILTON_SANTOS",
      "name": "Milton Santos",
      "type": "tanker",
      "class": "Suezmax",
      "status": "active",
      ...
    }
  ]
}
```

**GET** `/api/vessels/{vessel_id}`

Retorna detalhes de uma embarcação específica.

**Resposta:**
```json
{
  "id": "TP_SUEZMAX_MILTON_SANTOS",
  "name": "Milton Santos",
  "imo_number": "1234567",
  "type": "tanker",
  "class": "Suezmax",
  "dimensions": {
    "length_m": 274.0,
    "width_m": 48.0,
    "hull_area_m2": 15000.0
  },
  ...
}
```

**POST** `/api/vessels`

Cria uma nova embarcação.

**Body:**
```json
{
  "name": "Nova Embarcação",
  "imo_number": "7654321",
  "type": "tanker",
  "class": "Aframax",
  ...
}
```

**PUT** `/api/vessels/{vessel_id}`

Atualiza uma embarcação existente.

**DELETE** `/api/vessels/{vessel_id}`

Remove uma embarcação.

### 5.4 Predição de Bioincrustação

**POST** `/api/vessels/{vessel_id}/fouling/predict`

Prediz bioincrustação para uma embarcação.

**Body:**
```json
{
  "time_since_cleaning_days": 45,
  "water_temperature_c": 25.0,
  "salinity_psu": 35.0,
  "time_in_port_hours": 120.0,
  "average_speed_knots": 14.5,
  "route_region": "Brazil_Coast",
  "paint_type": "AFS",
  "vessel_type": "tanker",
  "hull_area_m2": 15000.0
}
```

**Resposta:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "estimated_thickness_mm": 3.2,
  "estimated_roughness_um": 320.0,
  "fouling_severity": "moderate",
  "confidence_score": 0.85,
  "predicted_fuel_impact_percent": 8.5,
  "predicted_co2_impact_kg": 1250.0
}
```

**POST** `/api/vessels/{vessel_id}/fouling/predict/advanced`

Predição avançada com ensemble de modelos.

**Body:**
```json
{
  "time_since_cleaning_days": 45,
  "water_temperature_c": 25.0,
  "salinity_psu": 35.0,
  ...
}
```

**Resposta:**
```json
{
  "predicted_thickness_mm": 3.15,
  "predicted_roughness_um": 315.0,
  "confidence_score": 0.88,
  "model_breakdown": {
    "xgb": 3.20,
    "rf": 3.10,
    "gbr": 3.18,
    "etr": 3.12
  },
  ...
}
```

**POST** `/api/vessels/{vessel_id}/fouling/predict/explain`

Explica uma predição (explicabilidade).

**Body:**
```json
{
  "time_since_cleaning_days": 45,
  ...
}
```

**Resposta:**
```json
{
  "prediction": {
    "estimated_thickness_mm": 3.2,
    ...
  },
  "explanation": {
    "contributions": [
      {
        "feature_name": "time_since_cleaning_days",
        "contribution": 0.8,
        "percentage": 35.2,
        "description": "Tempo desde última limpeza contribui positivamente"
      },
      ...
    ],
    "natural_language": "A predição indica espessura de 3.2mm principalmente devido ao tempo desde última limpeza (45 dias) e temperatura da água (25°C)..."
  }
}
```

**GET** `/api/vessels/{vessel_id}/fouling/latest`

Retorna a última medição de bioincrustação.

**GET** `/api/vessels/{vessel_id}/fouling`

Retorna histórico de medições.

**Query Parameters:**
- `days` (int, opcional): Número de dias (padrão: 90)

### 5.5 Impacto no Combustível

**POST** `/api/vessels/{vessel_id}/fuel/impact`

Calcula impacto da bioincrustação no consumo de combustível.

**Body:**
```json
{
  "current_speed_knots": 14.5,
  "engine_power_kw": 15000,
  "fouling_thickness_mm": 3.2,
  "roughness_um": 320.0,
  "hull_area_m2": 15000.0,
  "fuel_price_brl_per_kg": 3.50
}
```

**Resposta:**
```json
{
  "additional_consumption_kg_h": 125.5,
  "additional_consumption_percent": 8.5,
  "additional_cost_brl_h": 439.25,
  "co2_impact_kg": 395.33
}
```

### 5.6 Conformidade NORMAM 401

**POST** `/api/vessels/{vessel_id}/compliance/check`

Verifica conformidade com NORMAM 401.

**Body:**
```json
{
  "fouling_thickness_mm": 3.2,
  "roughness_um": 320.0,
  "vessel_type": "tanker"
}
```

**Resposta:**
```json
{
  "vessel_id": "TP_SUEZMAX_MILTON_SANTOS",
  "check_date": "2025-01-15T10:30:00Z",
  "status": "compliant",
  "fouling_thickness_mm": 3.2,
  "roughness_um": 320.0,
  "max_allowed_thickness_mm": 5.0,
  "max_allowed_roughness_um": 500.0,
  "violations": [],
  "warnings": [],
  "compliance_score": 0.92,
  "next_inspection_due": "2025-04-15T10:30:00Z",
  "recommendations": [
    "Manter monitoramento regular",
    "Próxima inspeção em 90 dias"
  ]
}
```

**GET** `/api/compliance/vessels/{vessel_id}/checks`

Histórico de verificações de conformidade.

**GET** `/api/compliance/vessels/{vessel_id}/checks/latest`

Última verificação de conformidade.

**GET** `/api/compliance/vessels/{vessel_id}/inspections`

Histórico de inspeções.

**GET** `/api/compliance/status/summary`

Resumo de conformidade da frota.

### 5.7 Recomendações

**POST** `/api/vessels/{vessel_id}/recommendations`

Gera recomendações de ações.

**Body:**
```json
{
  "current_fouling_mm": 3.2,
  "predicted_fouling_30d_mm": 4.5
}
```

**Resposta:**
```json
{
  "recommendations": [
    {
      "type": "scheduled_cleaning",
      "priority": "high",
      "description": "Limpeza programada recomendada em 20 dias",
      "estimated_cost_brl": 150000,
      "estimated_benefit_brl": 250000,
      "roi_percent": 66.7
    }
  ]
}
```

### 5.8 Dados Operacionais

**GET** `/api/vessels/{vessel_id}/operational-data/latest`

Últimos dados operacionais.

**GET** `/api/vessels/{vessel_id}/operational-data`

Histórico de dados operacionais.

**Query Parameters:**
- `days` (int, opcional): Número de dias (padrão: 30)

**POST** `/api/vessels/{vessel_id}/operational-data`

Registra novos dados operacionais.

### 5.9 Manutenção

**GET** `/api/vessels/{vessel_id}/maintenance/latest`

Último evento de manutenção.

**GET** `/api/vessels/{vessel_id}/maintenance`

Histórico de eventos de manutenção.

**Query Parameters:**
- `start_date` (string, opcional): Data inicial (ISO 8601)
- `end_date` (string, opcional): Data final (ISO 8601)
- `event_type` (string, opcional): Tipo de evento

**POST** `/api/vessels/{vessel_id}/maintenance`

Registra novo evento de manutenção.

### 5.10 Espécies Invasoras

**POST** `/api/invasive-species/assess`

Avalia risco de espécies invasoras.

**Body:**
```json
{
  "vessel_id": "TP_SUEZMAX_MILTON_SANTOS",
  "region": "Brazil_Coast",
  "water_temperature_c": 25.0,
  "salinity_psu": 35.0,
  "time_in_port_days": 5.0
}
```

**Resposta:**
```json
{
  "risks": [
    {
      "species": "CORAL_SOL",
      "scientific_name": "Tubastraea_coccinea",
      "risk_level": "high",
      "probability": 0.75,
      "factors": [
        "Região com histórico de coral sol",
        "Temperatura favorável",
        "Tempo prolongado em porto"
      ],
      "recommendations": [
        "Inspeção visual imediata",
        "Limpeza preventiva recomendada"
      ]
    }
  ]
}
```

**GET** `/api/invasive-species/info/{species}`

Informações sobre uma espécie específica.

**GET** `/api/invasive-species/list`

Lista todas as espécies catalogadas.

### 5.11 Gestão de Frota

**GET** `/api/fleet/summary`

Resumo da frota.

**GET** `/api/fleet/detailed-status`

Status detalhado de todas as embarcações.

**Query Parameters:**
- `filter_by_class` (string, opcional): Filtrar por classe

## 6. Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `404 Not Found`: Recurso não encontrado
- `405 Method Not Allowed`: Método HTTP não permitido
- `500 Internal Server Error`: Erro interno do servidor

## 7. Rate Limiting

Atualmente não implementado. Planejado:
- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário

## 8. Versionamento

A API está na versão 1.0. Versionamento futuro:
- `/api/v1/...` (versão atual implícita)
- `/api/v2/...` (futuras versões)

## 9. Documentação Interativa

A API inclui documentação interativa gerada automaticamente:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

## 10. Exemplos de Uso

### 10.1 Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Predição de bioincrustação
data = {
    "time_since_cleaning_days": 45,
    "water_temperature_c": 25.0,
    "salinity_psu": 35.0,
    ...
}
response = requests.post(
    "http://localhost:8000/api/vessels/TP_SUEZMAX_MILTON_SANTOS/fouling/predict",
    json=data
)
prediction = response.json()
print(f"Espessura prevista: {prediction['estimated_thickness_mm']} mm")
```

### 10.2 JavaScript/TypeScript

```typescript
// Usando fetch
const response = await fetch('http://localhost:8000/api/dashboard/kpis');
const kpis = await response.json();
console.log(`Economia: R$ ${kpis.economy_brl.toLocaleString('pt-BR')}`);

// Usando axios
import axios from 'axios';

const prediction = await axios.post(
  'http://localhost:8000/api/vessels/TP_SUEZMAX_MILTON_SANTOS/fouling/predict',
  {
    time_since_cleaning_days: 45,
    water_temperature_c: 25.0,
    ...
  }
);
console.log(prediction.data);
```

### 10.3 cURL

```bash
# Health check
curl http://localhost:8000/health

# Predição
curl -X POST http://localhost:8000/api/vessels/TP_SUEZMAX_MILTON_SANTOS/fouling/predict \
  -H "Content-Type: application/json" \
  -d '{
    "time_since_cleaning_days": 45,
    "water_temperature_c": 25.0,
    "salinity_psu": 35.0,
    ...
  }'
```

## 11. Tratamento de Erros

### 11.1 Erros de Validação

```json
{
  "detail": [
    {
      "loc": ["body", "time_since_cleaning_days"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

### 11.2 Erros de Negócio

```json
{
  "detail": "Embarcação não encontrada",
  "status": "error",
  "code": "VESSEL_NOT_FOUND"
}
```

## 12. Webhooks

Atualmente não implementado. Planejado:
- Notificações de eventos importantes
- Alertas de conformidade
- Atualizações de predições

---

**Versão da API:** 1.0  
**Última Atualização:** Janeiro 2025


