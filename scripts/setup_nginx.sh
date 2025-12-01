#!/bin/bash
set -e

DOMAIN="hullzero.siog.com.br"

echo "🚀 Configurando Servidor de Produção (Nginx + SSL)..."

# 1. Instalar Nginx e Certbot
echo "📦 Instalando Nginx e Certbot..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Criar Configuração do Nginx
echo "⚙️  Criando configuração do Nginx..."

# Definir o diretório do frontend
# Tenta detectar automaticamente, senão usa o padrão do usuário
if [ -d "$PWD/frontend/dist" ]; then
    FRONTEND_PATH="$PWD/frontend/dist"
elif [ -d "$HOME/hackathon-transpetro/frontend/dist" ]; then
    FRONTEND_PATH="$HOME/hackathon-transpetro/frontend/dist"
else
    echo "⚠️  Não foi possível encontrar a pasta frontend/dist automaticamente."
    echo "Assumindo: /home/$USER/hackathon-transpetro/frontend/dist"
    FRONTEND_PATH="/home/$USER/hackathon-transpetro/frontend/dist"
fi

echo "📂 Servindo Frontend de: $FRONTEND_PATH"

# Criar arquivo de configuração diretamente (sem depender de arquivo externo)
cat <<EOF | sudo tee /etc/nginx/sites-available/$DOMAIN
server {
    server_name $DOMAIN;

    # Frontend - Arquivos Estáticos
    location / {
        root $FRONTEND_PATH;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    # Backend - API Proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend - Docs Proxy (Swagger/Redoc)
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }
}
EOF

# Remover default se existir e criar link simbólico
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
echo "✅ Nginx configurado e reiniciado."

# 3. Configurar SSL com Let's Encrypt
echo "🔒 Configurando SSL (HTTPS)..."
echo "⚠️  Certifique-se de que o domínio $DOMAIN já aponta para este servidor no Cloudflare!"

# Tentar obter certificado
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m douglaslpolinto@gmail.com --redirect

echo "✅ SSL Configurado com Sucesso!"
echo "🌐 Acesse: https://$DOMAIN"
