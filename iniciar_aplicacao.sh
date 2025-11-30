#!/bin/bash
# Script para iniciar a aplicação HullZero (Backend + Frontend)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================================"
echo "  🚀 HullZero - Iniciando Aplicação Completa"
echo "============================================================"

# 1. Backend
echo -e "\n${GREEN}📦 Configurando Backend...${NC}"

if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt > /dev/null 2>&1

echo "Inicializando banco de dados..."
python3 init_complete.py --skip-tests

echo "Iniciando API..."
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"

# 2. Frontend
echo -e "\n${GREEN}🎨 Configurando Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Instalando dependências do frontend..."
    npm install > /dev/null 2>&1
fi

echo "Iniciando Frontend..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

cd ..

# 3. Resumo
echo -e "\n============================================================"
echo -e "  ✨ Aplicação HullZero rodando!"
echo "============================================================"
echo -e "📱 Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "⚙️  Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "📚 Docs API: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "Para parar a aplicação, execute: ./parar_aplicacao.sh"
echo "Logs em: backend.log e frontend.log"
