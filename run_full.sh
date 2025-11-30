#!/bin/bash
# Script para rodar Backend e Frontend do HullZero

echo "🚀 Iniciando HullZero - Backend e Frontend"
echo "=========================================="

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se backend está rodando
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend já está rodando em http://localhost:8000${NC}"
else
    echo -e "${YELLOW}📦 Iniciando Backend...${NC}"
    cd "$(dirname "$0")"
    python3 run_local.py > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend iniciado com sucesso!${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend pode estar iniciando ainda...${NC}"
    fi
fi

# Iniciar Frontend
echo -e "${BLUE}📦 Iniciando Frontend...${NC}"
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "Instalando dependências do frontend..."
    npm install
fi

echo -e "${GREEN}✅ Frontend iniciando em http://localhost:3000${NC}"
echo ""
echo "=========================================="
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "Pressione Ctrl+C para parar ambos os serviços"

npm run dev

