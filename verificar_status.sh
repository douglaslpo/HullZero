#!/bin/bash
# Script para verificar status

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Verificando status..."

# Verificar Backend (Porta 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "⚙️  Backend (8000): ${GREEN}ONLINE${NC}"
else
    echo -e "⚙️  Backend (8000): ${RED}OFFLINE${NC}"
fi

# Verificar Frontend (Porta 5173)
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "📱 Frontend (5173): ${GREEN}ONLINE${NC}"
else
    echo -e "📱 Frontend (5173): ${RED}OFFLINE${NC}"
fi
