# Guia de Deploy - HullZero

## 1. Visão Geral

Este guia apresenta diferentes opções de deploy da aplicação HullZero, desde ambientes locais até produção em cloud. A aplicação consiste em:
- **Backend:** API FastAPI (Python)
- **Frontend:** Aplicação React (TypeScript)
- **Banco de Dados:** SQLite (dev) ou PostgreSQL (produção)

## 2. Pré-requisitos

### 2.1 Para Deploy Local

- Python 3.11 ou superior
- Node.js 18 ou superior
- npm ou yarn
- Git

### 2.2 Para Deploy em Produção

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (opcional, para produção)
- Nginx (para servir frontend e reverse proxy)
- Certificado SSL (Let's Encrypt recomendado)

## 3. Opção 1: Deploy Local (Desenvolvimento)

### 3.1 Clonar Repositório

```bash
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero
```

### 3.2 Backend

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python init_complete.py

# Executar backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend estará disponível em: `http://localhost:8000`

### 3.3 Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev
```

Frontend estará disponível em: `http://localhost:5173`

## 4. Opção 2: Deploy com Docker

### 4.1 Criar Dockerfile para Backend

Crie `Dockerfile.backend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY init_complete.py .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Criar Dockerfile para Frontend

Crie `Dockerfile.frontend`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copiar package files
COPY frontend/package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código
COPY frontend/ .

# Build
RUN npm run build

# Stage de produção com Nginx
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4.3 Criar docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./hullzero.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Opcional: PostgreSQL para produção
  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=hullzero
      - POSTGRES_USER=hullzero
      - POSTGRES_PASSWORD=senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

### 4.4 Executar com Docker

```bash
# Build e start
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## 5. Opção 3: Deploy em Servidor Linux (Produção)

### 5.1 Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y nodejs npm
sudo apt install -y nginx
sudo apt install -y postgresql postgresql-contrib  # Opcional
```

### 5.2 Configurar Usuário

```bash
# Criar usuário para aplicação
sudo adduser --disabled-password --gecos "" hullzero
sudo su - hullzero
```

### 5.3 Clonar e Configurar Aplicação

```bash
# Clonar repositório
git clone https://github.com/douglaslpo/HullZero.git
cd HullZero

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python init_complete.py
```

### 5.4 Configurar Backend como Serviço Systemd

Crie `/etc/systemd/system/hullzero-backend.service`:

```ini
[Unit]
Description=HullZero Backend API
After=network.target

[Service]
Type=simple
User=hullzero
WorkingDirectory=/home/hullzero/HullZero
Environment="PATH=/home/hullzero/HullZero/venv/bin"
ExecStart=/home/hullzero/HullZero/venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hullzero-backend
sudo systemctl start hullzero-backend
sudo systemctl status hullzero-backend
```

### 5.5 Build do Frontend

```bash
cd /home/hullzero/HullZero/frontend

# Instalar dependências
npm install

# Build de produção
npm run build
```

### 5.6 Configurar Nginx

Crie `/etc/nginx/sites-available/hullzero`:

```nginx
# Backend API
upstream hullzero_backend {
    server 127.0.0.1:8000;
}

# Frontend
server {
    listen 80;
    server_name seu-dominio.com;

    # Frontend
    location / {
        root /home/hullzero/HullZero/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://hullzero_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://hullzero_backend;
    }
}
```

Ativar configuração:

```bash
sudo ln -s /etc/nginx/sites-available/hullzero /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5.7 Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática (já configurado)
sudo certbot renew --dry-run
```

## 6. Opção 4: Deploy em Cloud (AWS, Azure, GCP)

### 6.1 AWS (Elastic Beanstalk / EC2)

**Opção A: Elastic Beanstalk**

1. Instalar EB CLI:
```bash
pip install awsebcli
```

2. Inicializar:
```bash
eb init -p python-3.11 hullzero
eb create hullzero-env
eb deploy
```

**Opção B: EC2**

Seguir instruções da seção 5 (Deploy em Servidor Linux).

### 6.2 Azure (App Service)

1. Instalar Azure CLI
2. Criar App Service:
```bash
az webapp create --resource-group hullzero-rg --plan hullzero-plan --name hullzero-app
```

3. Deploy:
```bash
az webapp deployment source config-zip --resource-group hullzero-rg --name hullzero-app --src deploy.zip
```

### 6.3 Google Cloud Platform (App Engine / Cloud Run)

**Cloud Run (Recomendado):**

1. Criar `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/hullzero-backend', '-f', 'Dockerfile.backend', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/hullzero-backend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'hullzero-backend', '--image', 'gcr.io/$PROJECT_ID/hullzero-backend', '--region', 'us-central1']
```

2. Deploy:
```bash
gcloud builds submit --config cloudbuild.yaml
```

## 7. Variáveis de Ambiente

Crie arquivo `.env` para produção:

```bash
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/hullzero
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=False
ALLOWED_ORIGINS=https://seu-dominio.com

# Frontend (no build)
VITE_API_URL=https://api.seu-dominio.com
```

## 8. Banco de Dados em Produção

### 8.1 PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE hullzero;
CREATE USER hullzero_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE hullzero TO hullzero_user;
\q
```

### 8.2 Configurar Aplicação

Atualizar `src/database/__init__.py`:

```python
DATABASE_URL = "postgresql://hullzero_user:senha_segura@localhost:5432/hullzero"
```

## 9. Monitoramento e Logs

### 9.1 Logs do Backend

```bash
# Ver logs do serviço
sudo journalctl -u hullzero-backend -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 9.2 Monitoramento Básico

Instalar ferramentas de monitoramento:

```bash
# htop para monitoramento de recursos
sudo apt install -y htop

# netdata para monitoramento completo (opcional)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

## 10. Backup

### 10.1 Backup do Banco de Dados

Criar script `/home/hullzero/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/hullzero/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
pg_dump -U hullzero_user hullzero > $BACKUP_DIR/hullzero_$DATE.sql

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "hullzero_*.sql" -mtime +7 -delete
```

Agendar no cron:

```bash
crontab -e
# Adicionar linha:
0 2 * * * /home/hullzero/backup.sh
```

## 11. Atualizações

### 11.1 Processo de Atualização

```bash
# 1. Fazer backup
./backup.sh

# 2. Parar serviços
sudo systemctl stop hullzero-backend

# 3. Atualizar código
cd /home/hullzero/HullZero
git pull origin main

# 4. Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# 5. Executar migrações (se houver)
python src/database/migrate.py run

# 6. Rebuild frontend (se necessário)
cd frontend
npm install
npm run build

# 7. Reiniciar serviços
sudo systemctl start hullzero-backend
sudo systemctl restart nginx
```

## 12. Troubleshooting

### 12.1 Backend não inicia

```bash
# Verificar logs
sudo journalctl -u hullzero-backend -n 50

# Verificar porta
sudo netstat -tlnp | grep 8000

# Testar manualmente
cd /home/hullzero/HullZero
source venv/bin/activate
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 12.2 Frontend não carrega

```bash
# Verificar build
ls -la /home/hullzero/HullZero/frontend/dist

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx

# Verificar permissões
sudo chown -R hullzero:hullzero /home/hullzero/HullZero/frontend/dist
```

### 12.3 Erros de banco de dados

```bash
# Verificar conexão
psql -U hullzero_user -d hullzero -h localhost

# Verificar logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## 13. Checklist de Deploy

- [ ] Servidor configurado com todas as dependências
- [ ] Aplicação clonada e configurada
- [ ] Banco de dados criado e migrado
- [ ] Variáveis de ambiente configuradas
- [ ] Backend rodando como serviço systemd
- [ ] Frontend buildado e servido pelo Nginx
- [ ] SSL configurado (Let's Encrypt)
- [ ] Firewall configurado (portas 80, 443 abertas)
- [ ] Backup configurado
- [ ] Monitoramento configurado
- [ ] Testes de funcionalidade realizados
- [ ] Documentação atualizada

## 14. Segurança

### 14.1 Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 14.2 Hardening

- Desabilitar login root via SSH
- Usar chaves SSH
- Manter sistema atualizado
- Configurar fail2ban
- Usar senhas fortes
- Habilitar HTTPS apenas

## 15. Recursos Adicionais

- [Documentação FastAPI](https://fastapi.tiangolo.com/deployment/)
- [Documentação React Build](https://react.dev/learn/start-a-new-react-project#building-for-production)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025

