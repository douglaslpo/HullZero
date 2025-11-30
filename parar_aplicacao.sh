#!/bin/bash
# Script para parar a aplicação HullZero

echo "🛑 Parando HullZero..."

# Parar Backend
pkill -f "uvicorn src.api.main:app" && echo "✅ Backend parado." || echo "⚠️  Backend não estava rodando."

# Parar Frontend (Vite)
pkill -f "vite" && echo "✅ Frontend parado." || echo "⚠️  Frontend não estava rodando."

echo "✨ Tudo limpo."
