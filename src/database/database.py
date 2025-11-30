"""
Configuração e Sessão do Banco de Dados - HullZero
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from .config import DATABASE_URL, DB_ECHO, DB_POOL_SIZE, DB_MAX_OVERFLOW, USE_TIMESCALEDB
from .models import Base

# Configurar engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite para desenvolvimento
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=DB_ECHO
    )
else:
    # PostgreSQL/TimescaleDB para produção
    engine = create_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        echo=DB_ECHO,
        pool_pre_ping=True  # Verifica conexões antes de usar
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados.
    Usar com FastAPI: @app.get("/endpoint", dependencies=[Depends(get_db)])
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    """
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Se usar TimescaleDB, criar hypertables
    if USE_TIMESCALEDB and not DATABASE_URL.startswith("sqlite"):
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Criar extensão TimescaleDB
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            conn.commit()
            
            # Converter tabelas time series em hypertables
            try:
                conn.execute(text(
                    "SELECT create_hypertable('fouling_data', 'timestamp', if_not_exists => TRUE)"
                ))
                conn.commit()
            except Exception as e:
                print(f"Nota: Não foi possível criar hypertable para fouling_data: {e}")
            
            try:
                conn.execute(text(
                    "SELECT create_hypertable('operational_data', 'timestamp', if_not_exists => TRUE)"
                ))
                conn.commit()
            except Exception as e:
                print(f"Nota: Não foi possível criar hypertable para operational_data: {e}")


def drop_db():
    """
    Remove todas as tabelas do banco de dados.
    ATENÇÃO: Esta função apaga todos os dados!
    """
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    # Executar para criar o banco de dados
    print("Inicializando banco de dados...")
    init_db()
    print("Banco de dados inicializado com sucesso!")

