"""
Configuração Centralizada - HullZero

Carrega variáveis de ambiente do arquivo .env
"""

import os
from pathlib import Path
from typing import List, Optional

# Tentar importar python-dotenv
try:
    from dotenv import load_dotenv
    # Carregar .env do diretório raiz do projeto
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Tentar carregar do diretório atual
        load_dotenv()
except ImportError:
    # Se python-dotenv não estiver instalado, usar apenas os.getenv
    pass


# ============================================
# Ambiente
# ============================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# ============================================
# Banco de Dados
# ============================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./hullzero.db"
)

DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
USE_TIMESCALEDB = os.getenv("USE_TIMESCALEDB", "false").lower() == "true"

# ============================================
# Autenticação e Segurança
# ============================================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "sua-chave-secreta-super-segura-aqui-mude-em-producao"
)

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

# ============================================
# API e Servidor
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
API_WORKERS = int(os.getenv("API_WORKERS", "1"))

# ============================================
# CORS
# ============================================
CORS_ORIGINS_STR = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080"
)
CORS_ORIGINS = [
    origin.strip()
    for origin in CORS_ORIGINS_STR.split(",")
    if origin.strip()
]

CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
CORS_METHODS = os.getenv("CORS_METHODS", "*").split(",")
CORS_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")

# ============================================
# Frontend
# ============================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
VITE_API_URL = os.getenv("VITE_API_URL", "http://localhost:8000")

# ============================================
# Redis (Cache - Opcional)
# ============================================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# ============================================
# Logging
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/hullzero.log")

# ============================================
# Modelos de IA/ML
# ============================================
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "models/")
ML_CACHE_ENABLED = os.getenv("ML_CACHE_ENABLED", "true").lower() == "true"

# ============================================
# Email (Opcional)
# ============================================
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@hullzero.com.br")

# ============================================
# Upload de Arquivos
# ============================================
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB

# ============================================
# Segurança - Rate Limiting
# ============================================
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


# ============================================
# Validações
# ============================================
def validate_config():
    """Valida configurações críticas"""
    errors = []
    
    if ENVIRONMENT == "production":
        if SECRET_KEY == "sua-chave-secreta-super-segura-aqui-mude-em-producao":
            errors.append(
                "⚠️  SECRET_KEY deve ser alterada em produção! "
                "Gere uma chave segura com: "
                "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        if DATABASE_URL.startswith("sqlite"):
            errors.append(
                "⚠️  SQLite não é recomendado para produção. "
                "Use PostgreSQL ou TimescaleDB."
            )
    
    if errors:
        print("\n".join(errors))
    
    return len(errors) == 0


# Validar ao importar
if __name__ != "__main__":
    validate_config()

