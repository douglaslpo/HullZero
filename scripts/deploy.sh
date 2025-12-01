#!/bin/bash
set -e

# Cores para logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Deploy Completo do HullZero...${NC}"

# 1. Instalar Dependências do Sistema
echo -e "${YELLOW}📦 Instalando dependências do sistema...${NC}"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx unzip

# 2. Configurar Backend
echo -e "${YELLOW}🐍 Configurando Backend (Python)...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
# Instalar uvicorn explicitamente se não estiver no requirements
pip install uvicorn fastapi

# 3. Configurar Frontend
echo -e "${YELLOW}⚛️  Configurando Frontend (React)...${NC}"
cd frontend
# Definir URL da API para Produção
export VITE_API_URL="https://hullzero.siog.com.br"
npm install
npm run build
cd ..

# 4. Configurar Aplicativo Mobile
echo -e "${YELLOW}📱 Configurando Aplicativo Mobile (Expo)...${NC}"
cd aplicativo
npm install
cd ..

# 5. Configurar Nginx e SSL
echo -e "${YELLOW}🌐 Configurando Servidor Web (Nginx + SSL)...${NC}"
chmod +x setup_nginx.sh
./setup_nginx.sh

# 6. Gerenciar Processos com PM2
echo -e "${YELLOW}⚙️  Configurando Processos (PM2)...${NC}"
sudo npm install -g pm2

# Parar processos antigos se existirem
pm2 delete hullzero-api 2>/dev/null || true
pm2 delete hullzero-web 2>/dev/null || true # Frontend agora é pelo Nginx

# Iniciar Backend
pm2 start "venv/bin/python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000" --name hullzero-api

# Salvar e Configurar Startup
pm2 save
pm2 startup | tail -n 1 | bash || true

echo -e "${GREEN}✅ Deploy Concluído com Sucesso!${NC}"
echo -e "🌍 Web: https://hullzero.siog.com.br"
echo -e "📱 Mobile: Entre na pasta 'aplicativo' e rode 'npx expo start' para gerar o QR Code."
