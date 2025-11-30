# Modelos de Inteligência Artificial - HullZero

## 1. Visão Geral

O sistema HullZero utiliza múltiplos modelos de inteligência artificial para predição, otimização e análise de bioincrustação marinha. Os modelos combinam técnicas de machine learning, física aplicada e análise de séries temporais para fornecer predições precisas e explicáveis.

## 2. Arquitetura de Modelos

### 2.1 Modelo Híbrido

O sistema utiliza uma abordagem híbrida que combina:
- **Modelo Físico (30%):** Baseado em equações físicas e químicas conhecidas
- **Machine Learning (70%):** Modelos treinados com dados históricos

**Vantagens:**
- Maior precisão que modelos puramente físicos
- Melhor generalização que modelos puramente ML
- Explicabilidade através do componente físico

### 2.2 Ensemble de Modelos

Para predições avançadas, o sistema utiliza ensemble de múltiplos algoritmos:

- **XGBoost:** Gradient boosting otimizado
- **Random Forest:** Ensemble de árvores de decisão
- **Gradient Boosting:** Boosting sequencial
- **Extra Trees:** Árvores extremamente aleatórias
- **Voting Regressor:** Combinação ponderada dos modelos acima

**Pesos do Ensemble:**
Os pesos são calculados dinamicamente baseados na performance de cada modelo em validação cruzada.

## 3. Modelos Implementados

### 3.1 Predição de Bioincrustação

**Arquivo:** `src/models/fouling_prediction.py`

**Modelo Híbrido:**
```python
class HybridFoulingModel:
    def predict(self, features: VesselFeatures) -> FoulingPrediction:
        # Predição física
        physical_thickness = self.physical_model.predict_growth(...)
        
        # Predição ML
        ml_thickness = self.ml_model.predict(features)
        
        # Combinação híbrida
        hybrid_thickness = (
            0.3 * physical_thickness + 
            0.7 * ml_thickness
        )
        
        return FoulingPrediction(...)
```

**Features Utilizadas:**
- Tempo desde última limpeza (dias)
- Temperatura da água (°C)
- Salinidade (PSU)
- Tempo em porto (horas)
- Velocidade média (nós)
- Região de rota
- Tipo de tinta
- Tipo de embarcação
- Área do casco (m²)

**Saída:**
- Espessura estimada (mm)
- Rugosidade estimada (μm)
- Severidade (light/moderate/severe)
- Score de confiança (0-1)
- Impacto previsto no combustível (%)
- Impacto previsto de CO₂ (kg)

### 3.2 Predição Avançada de Bioincrustação

**Arquivo:** `src/models/advanced_fouling_prediction.py`

**Modelo Ensemble:**
```python
class AdvancedMLModel:
    def __init__(self):
        self.models = {
            'xgb': XGBRegressor(...),
            'rf': RandomForestRegressor(...),
            'gbr': GradientBoostingRegressor(...),
            'etr': ExtraTreesRegressor(...)
        }
        self.weights = {}  # Calculados dinamicamente
        
    def predict(self, features: AdvancedVesselFeatures) -> float:
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(features)
        
        # Combinação ponderada
        final_prediction = sum(
            predictions[name] * self.weights[name]
            for name in self.models.keys()
        )
        
        return final_prediction
```

**Features Adicionais:**
- Histórico de bioincrustação
- Fatores sazonais
- Presença de espécies invasoras
- Eficácia de tintas anti-incrustantes
- Dados ambientais históricos

**Melhorias:**
- Maior precisão (R² > 0.85)
- Melhor generalização
- Tratamento de dados faltantes
- Feature engineering avançado

### 3.3 Predição de Impacto no Combustível

**Arquivo:** `src/models/fuel_impact.py`

**Abordagem:**
- Modelo de consumo ideal (física)
- Modelo de consumo real (ML)
- Cálculo de diferença (impacto)

**Fórmula Física:**
```
Consumo Ideal = f(velocidade, potência, área_casco_limpo)
Consumo Real = f(velocidade, potência, área_casco_com_bioincrustação)
Impacto = Consumo Real - Consumo Ideal
```

**Modelo ML:**
- Random Forest para consumo real
- Features: velocidade, potência, espessura, rugosidade, condições ambientais

**Saída:**
- Consumo adicional (kg/h)
- Consumo adicional (%)
- Custo adicional (R$)
- Impacto de CO₂ (kg)

### 3.4 Predição de Risco NORMAM 401

**Arquivo:** `src/models/normam401_risk.py`

**Abordagem:**
- Classificação binária (risco / sem risco)
- Predição de probabilidade
- Identificação de fatores de risco

**Modelo:**
- Gradient Boosting Classifier
- Features: espessura atual, rugosidade, taxa de crescimento, tempo até inspeção, histórico

**Saída:**
- Probabilidade de não conformidade (0-1)
- Nível de risco (low/medium/high/critical)
- Fatores de risco identificados
- Horizonte temporal (15/30 dias)

### 3.5 Otimização de Inspeções

**Arquivo:** `src/models/inspection_optimizer.py`

**Abordagem:**
- Otimização combinatória
- Algoritmo de agendamento
- Minimização de custos e riscos

**Algoritmo:**
1. Classifica embarcações por prioridade (risco)
2. Agrupa por região geográfica
3. Otimiza rota de inspeção
4. Minimiza impacto operacional

**Saída:**
- Cronograma de inspeções
- Priorização de embarcações
- Estimativa de custos
- Impacto operacional

### 3.6 Detecção de Anomalias

**Arquivo:** `src/models/anomaly_detector.py`

**Abordagem:**
- Isolation Forest
- Detecção de outliers estatísticos
- Análise de padrões anômalos

**Tipos de Anomalias Detectadas:**
- Crescimento acelerado de bioincrustação
- Valores fora do esperado
- Padrões incomuns de consumo
- Inconsistências em dados

**Saída:**
- Flag de anomalia (sim/não)
- Tipo de anomalia
- Severidade
- Explicação

### 3.7 Recomendação de Ações Corretivas

**Arquivo:** `src/models/corrective_actions.py`

**Abordagem:**
- Sistema de regras baseado em status de conformidade
- Análise de custo-benefício
- Priorização de ações

**Tipos de Ações:**
- Limpeza imediata
- Limpeza programada
- Inspeção adicional
- Monitoramento intensificado
- Pintura preventiva

**Saída:**
- Tipo de ação recomendada
- Prioridade (urgent/high/medium/low)
- Custo estimado
- Benefício esperado
- ROI da ação

### 3.8 Explicabilidade

**Arquivo:** `src/models/explainability.py`

**Técnicas:**
- SHAP values (quando disponível)
- Feature importance
- Explicações em linguagem natural

**Implementação:**
```python
class ModelExplainer:
    def explain_prediction(self, model, features, prediction) -> PredictionExplanation:
        # Calcula contribuições de features
        contributions = self.calculate_shap_values(model, features)
        
        # Gera explicação em linguagem natural
        explanation = self.generate_natural_language_explanation(
            contributions, prediction
        )
        
        return PredictionExplanation(
            contributions=contributions,
            explanation=explanation,
            confidence=prediction.confidence
        )
```

**Saída:**
- Contribuição de cada feature
- Explicação em linguagem natural
- Score de confiança
- Gráficos de contribuição

## 4. Análise de Espécies Invasoras

**Arquivo:** `src/services/invasive_species_service.py`

**Abordagem:**
- Sistema de regras baseado em pesquisas científicas
- Análise de fatores de risco
- Classificação de risco por espécie

**Fatores Considerados:**
- Região de operação
- Temperatura da água
- Salinidade
- Histórico de espécies na região
- Tipo de embarcação
- Tempo em portos

**Saída:**
- Risco por espécie (low/medium/high/critical)
- Probabilidade de presença
- Recomendações de controle
- Métodos biológicos disponíveis

## 5. Treinamento e Validação

### 5.1 Dados de Treinamento

**Fontes:**
- Dados históricos da frota Transpetro
- Dados sintéticos gerados (quando necessário)
- Pesquisas científicas publicadas
- Benchmarks da indústria

### 5.2 Validação

**Métricas:**
- R² (coeficiente de determinação)
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- Precisão/Recall (classificação)

**Validação Cruzada:**
- K-fold cross-validation
- Time series split (para dados temporais)

### 5.3 Performance Esperada

**Predição de Bioincrustação:**
- R² > 0.80
- MAE < 0.5 mm

**Predição de Impacto no Combustível:**
- R² > 0.75
- MAE < 2%

**Predição de Risco NORMAM 401:**
- Precisão > 85%
- Recall > 80%

## 6. Feature Engineering

### 6.1 Transformações

- Normalização (StandardScaler, RobustScaler)
- Encoding de variáveis categóricas
- Criação de features derivadas
- Tratamento de valores faltantes

### 6.2 Features Derivadas

- Taxa de crescimento (derivada temporal)
- Razões entre features (ex: temperatura/salinidade)
- Features sazonais (mês, estação)
- Features de histórico (média móvel, tendência)

## 7. Otimização de Hiperparâmetros

### 7.1 Grid Search

Para modelos individuais:
- Grid search em espaço de hiperparâmetros
- Validação cruzada para seleção

### 7.2 Ensemble Weights

Para ensemble:
- Pesos calculados baseados em performance de validação
- Otimização iterativa

## 8. Atualização de Modelos

### 8.1 Retreinamento

**Frequência:**
- Mensal (com novos dados)
- Quando performance degrada
- Quando novos dados significativos disponíveis

**Processo:**
1. Coleta de novos dados
2. Validação de qualidade
3. Retreinamento
4. Validação de performance
5. Deploy (se melhor)

### 8.2 Versionamento

- Modelos versionados
- Histórico de performance
- Rollback se necessário

## 9. Limitações e Considerações

### 9.1 Limitações Atuais

- Dependência de dados históricos
- Modelos treinados com dados sintéticos (fase inicial)
- Necessidade de validação com dados reais

### 9.2 Melhorias Futuras

- Deep Learning para padrões complexos
- Transfer Learning de modelos pré-treinados
- Reinforcement Learning para otimização contínua
- Modelos específicos por tipo de embarcação

## 10. Uso dos Modelos

### 10.1 Via API

```python
POST /api/vessels/{vessel_id}/fouling/predict
{
    "time_since_cleaning_days": 45,
    "water_temperature_c": 25.0,
    "salinity_psu": 35.0,
    ...
}

Response:
{
    "estimated_thickness_mm": 3.2,
    "estimated_roughness_um": 320.0,
    "confidence_score": 0.85,
    ...
}
```

### 10.2 Via Serviços Python

```python
from src.models.fouling_prediction import predict_fouling

prediction = predict_fouling(features)
print(f"Espessura prevista: {prediction.estimated_thickness_mm} mm")
```

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025


