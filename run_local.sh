#!/bin/bash
# Script para rodar a aplicação HullZero localmente
# sem necessidade de Docker.

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================================"
echo "  HullZero - Inicialização Local"
echo "============================================================"

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado. Criando...${NC}"
    python3 -m venv venv
fi

# Ativa o ambiente virtual
echo -e "${GREEN}✅ Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Verifica se as dependências estão instaladas
echo -e "${GREEN}✅ Verificando dependências...${NC}"
if ! python3 -c "import fastapi, uvicorn, pydantic, numpy, pandas" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Algumas dependências estão faltando. Instalando...${NC}"
    pip install -r requirements.txt
fi

# Verifica se já existe um processo rodando na porta 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Já existe um processo rodando na porta 8000${NC}"
    read -p "Deseja encerrar o processo existente e iniciar um novo? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${YELLOW}🛑 Encerrando processo existente...${NC}"
        pkill -f "uvicorn.*main:app" || true
        sleep 2
    else
        echo -e "${GREEN}✅ Mantendo processo existente${NC}"
        echo -e "${GREEN}📍 API disponível em: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 Documentação em: http://localhost:8000/docs${NC}"
        exit 0
    fi
fi

# Inicia o backend
echo ""
echo -e "${GREEN}🚀 Iniciando HullZero API...${NC}"
echo -e "${GREEN}📍 API disponível em: http://localhost:8000${NC}"
echo -e "${GREEN}📚 Documentação em: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🔍 Health check: http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}⚠️  Nota: Banco de dados e Redis não são obrigatórios para testes básicos${NC}"
echo -e "${YELLOW}   Os modelos funcionam sem banco de dados para demonstração.${NC}"
echo ""

# Executa o backend em background e salva o log
python3 -m uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    > backend.log 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}📝 Logs salvos em: backend.log${NC}"

# Aguarda alguns segundos para verificar se iniciou corretamente
sleep 3

# Verifica se o backend está respondendo
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend está respondendo corretamente!${NC}"
    echo ""
    echo "============================================================"
    echo -e "${GREEN}  ✅ Backend ativo e funcionando!${NC}"
    echo "============================================================"
    echo ""
    echo "Para ver os logs em tempo real:"
    echo "  tail -f backend.log"
    echo ""
    echo "Para encerrar o backend:"
    echo "  pkill -f 'uvicorn.*main:app'"
    echo ""
else
    echo -e "${RED}❌ Backend não está respondendo. Verifique os logs:${NC}"
    echo "  tail -20 backend.log"
    exit 1
fi


