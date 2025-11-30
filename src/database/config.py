"""
Configuração do Banco de Dados - HullZero

NOTA: Este arquivo está sendo mantido para compatibilidade.
As configurações agora vêm de src/config.py que carrega o .env
"""

from ..config import (
    DATABASE_URL,
    DB_ECHO,
    DB_POOL_SIZE,
    DB_MAX_OVERFLOW,
    USE_TIMESCALEDB
)

# Re-exportar para compatibilidade com código existente
__all__ = [
    "DATABASE_URL",
    "DB_ECHO",
    "DB_POOL_SIZE",
    "DB_MAX_OVERFLOW",
    "USE_TIMESCALEDB"
]

