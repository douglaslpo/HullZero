#!/usr/bin/env python3
"""
Script de Inicialização do Banco de Dados - HullZero

Uso:
    python scripts/init_database.py
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.init_data import initialize_database

if __name__ == "__main__":
    initialize_database()

