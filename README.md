# 🚢 HullZero - Solução Integrada de Monitoramento e Previsão de Bioincrustação

## 📋 Visão Geral

O **HullZero** é uma solução tecnológica integrada desenvolvida para a Transpetro, focada em monitorar, prever e otimizar o gerenciamento de bioincrustação em cascos de embarcações, maximizando eficiência energética, reduzindo emissões de CO₂ e garantindo conformidade com a NORMAM 401.

## 🎯 Objetivos

- ✅ **Monitorar e prever** bioincrustação em cascos de embarcações
- ✅ **Isolar o impacto** da bioincrustação no consumo de combustível
- ✅ **Recomendar** o momento ótimo de limpeza/manutenção
- ✅ **Garantir conformidade** com a NORMAM 401
- ✅ **Maximizar redução** de emissões e eficiência operacional

## 🚀 Início Rápido

### Opção 1: Inicialização Automática Completa (Recomendado)

Este script automatiza todo o processo: ambiente virtual, dependências, banco de dados, migrações e testes.

#### Linux/Mac:
```bash
# Clone o repositório
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero

# Execute a inicialização completa
python3 init_complete.py --start-services
```

#### Windows:
```cmd
# Clone o repositório
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero

# Execute a inicialização completa
python init_complete.py --start-services
```

### Opção 2: Scripts de Inicialização Rápida

#### Linux/Mac:
```bash
# Clone o repositório
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero

# Execute o script de instalação
./iniciar_aplicacao.sh
```

#### Windows:
```cmd
# Clone o repositório
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero

# Execute o script (escolha um):
iniciar_aplicacao.bat        # CMD
.\iniciar_aplicacao.ps1      # PowerShell
```

### Acessos:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Documentação

- 📖 [Guia de Instalação Completo](./GUIA_INSTALACAO.md) - Instruções detalhadas
- ⚡ [Quick Start](./QUICK_START.md) - Guia rápido de uso
- 💡 [Como Usar](./COMO_USAR.md) - Exemplos práticos
- 📊 [Proposta Executiva](./docs/executivo/PROPOSTA_EXECUTIVA.md)
- 🏗️ [Arquitetura Técnica](./docs/tecnico/ARQUITETURA_TECNICA.md)
- 📈 [Análise de ROI](./docs/executivo/ANALISE_ROI.md)
- 🗺️ [Roadmap de Implementação](./docs/executivo/ROADMAP_IMPLEMENTACAO.md)

## 🛠️ Scripts Disponíveis

### Inicialização Automática Completa
- **`init_complete.py`** - Script Python que automatiza todo o processo:
  - ✅ Verifica versão do Python
  - ✅ Cria/ativa ambiente virtual
  - ✅ Instala dependências
  - ✅ Inicializa banco de dados (tabelas, migrações, dados de referência)
  - ✅ Executa testes de integridade
  - ✅ Opcionalmente inicia serviços (`--start-services`)
  
  **Uso:**
  ```bash
  # Apenas inicialização (sem iniciar serviços)
  python init_complete.py
  
  # Inicialização + iniciar serviços
  python init_complete.py --start-services
  
  # Pular banco de dados
  python init_complete.py --skip-db --start-services
  
  # Pular testes
  python init_complete.py --skip-tests --start-services
  ```

### Scripts de Inicialização Rápida

#### Linux/Mac:
- `./iniciar_aplicacao.sh` - Inicia Backend + Frontend (com inicialização automática do banco)
- `./verificar_status.sh` - Verifica status dos serviços
- `./parar_aplicacao.sh` - Para todos os serviços

#### Windows:
- `iniciar_aplicacao.bat` - Inicia Backend + Frontend (com inicialização automática do banco)
- `verificar_status.bat` - Verifica status dos serviços
- `parar_aplicacao.bat` - Para todos os serviços

## 🏗️ Estrutura do Projeto

```
hackathon-transpetro/
├── src/                    # Código fonte
│   ├── api/               # APIs REST (FastAPI)
│   ├── models/            # Modelos de IA/ML
│   └── services/          # Serviços de negócio
├── frontend/              # Frontend React + TypeScript
├── docs/                   # Documentação completa
│   ├── executivo/         # Propostas executivas
│   ├── tecnico/           # Arquitetura técnica
│   └── regulatorio/       # NORMAM 401
├── ENTREGA_HACKATHON/     # Documentação de entrega
├── requirements.txt        # Dependências Python
└── docker-compose.yml     # Configuração Docker
```

## 💻 Tecnologias

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **ML/AI**: TensorFlow, scikit-learn, Prophet, XGBoost
- **Frontend**: React 18+, TypeScript, Vite, Chakra UI
- **Dados**: PostgreSQL, TimescaleDB (opcional), Redis (opcional)
- **Infraestrutura**: Docker, Docker Compose

## 📦 Pré-requisitos

- **Python**: 3.11 ou superior
- **Node.js**: 18 ou superior
- **npm**: Incluído com Node.js
- **Git**: Para clonar o repositório

## 🔧 Instalação Manual

### 1. Backend:

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Frontend:

```bash
cd frontend
npm install
```

### 3. Executar:

```bash
# Backend (Terminal 1)
source venv/bin/activate
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (Terminal 2)
cd frontend
npm run dev
```

## 🧪 Testes

```bash
# Executar testes
pytest tests/

# Com cobertura
pytest --cov=src tests/
```

## 📝 API Endpoints Principais

- `GET /health` - Health check
- `POST /vessels/{id}/fouling/predict` - Predição de bioincrustação
- `POST /vessels/{id}/fuel/impact` - Impacto no combustível
- `POST /vessels/{id}/recommendations` - Recomendações de limpeza
- `POST /vessels/{id}/compliance/check` - Verificação NORMAM 401
- `GET /api/dashboard/kpis` - KPIs do dashboard
- `GET /api/vessels` - Lista de embarcações

Veja a documentação completa em: http://localhost:8000/docs

## 🐛 Troubleshooting

### Porta já em uso:
```bash
# Linux/Mac
lsof -i :8000
kill <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Dependências faltando:
```bash
# Reinstalar dependências
pip install -r requirements.txt
cd frontend && npm install
```

## 📄 Licença

Copyright © 2025 Transpetro - Todos os direitos reservados

## 🤝 Contribuindo

Este é um projeto desenvolvido para a hackathon Transpetro. Para contribuições, consulte a documentação em `docs/`.

---

**HullZero** - Solução Integrada para Monitoramento e Previsão de Bioincrustação

