"""
Importador de Dados Reais - HullZero

Este módulo importa dados reais da pasta dados/ para o banco de dados,
incluindo:
- Dados AIS da frota TP (CSV)
- Dados de consumo (CSV)
- Dados de eventos (CSV)
- Dados de navios (Excel)
"""

import csv
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

# SQLAlchemy
from sqlalchemy.orm import Session

# Modelos do banco
from ..database.models import (
    Vessel,
    FoulingData,
    OperationalData,
    MaintenanceEvent
)
from ..database.repositories import (
    VesselRepository,
    FoulingDataRepository,
    OperationalDataRepository,
    MaintenanceEventRepository
)
from .vessel_name_mapper import VesselNameMapper

# Base path para dados
DATA_BASE_PATH = Path(__file__).parent.parent.parent / "dados"


def parse_datetime(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """Tenta parsear uma string de data em vários formatos"""
    if formats is None:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    
    return None


def import_ais_data(db: Session, vessel_name: str, csv_path: str) -> int:
    """
    Importa dados AIS de um CSV para operational_data
    
    Args:
        db: Sessão do banco de dados
        vessel_id: ID da embarcação
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        Número de registros importados
    """
    if not os.path.exists(csv_path):
        print(f"⚠️  Arquivo não encontrado: {csv_path}")
        return 0
    
    count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Detectar delimitador
            first_line = f.readline()
            f.seek(0)
            
            delimiter = ',' if ',' in first_line else ';'
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Mapear colunas (flexível)
            for row in reader:
                try:
                    # Extrair dados baseado em nomes de colunas comuns
                    timestamp = None
                    latitude = None
                    longitude = None
                    speed_knots = None
                    heading = None
                    
                    # Tentar diferentes nomes de colunas
                    for key, value in row.items():
                        key_lower = key.lower()
                        
                        # Timestamp
                        if any(x in key_lower for x in ['timestamp', 'data', 'date', 'hora', 'time']):
                            timestamp = parse_datetime(str(value))
                        
                        # Latitude
                        if any(x in key_lower for x in ['latitude', 'lat']):
                            try:
                                latitude = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                        
                        # Longitude
                        if any(x in key_lower for x in ['longitude', 'lon', 'lng']):
                            try:
                                longitude = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                        
                        # Velocidade
                        if any(x in key_lower for x in ['speed', 'velocidade', 'sog']):
                            try:
                                speed_knots = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                        
                        # Direção
                        if any(x in key_lower for x in ['heading', 'direção', 'course', 'cog']):
                            try:
                                heading = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                    
                    # Se não encontrou timestamp, usar data atual
                    if not timestamp:
                        timestamp = datetime.utcnow() - timedelta(days=count/24)  # Distribuir no tempo
                    
                    # Criar registro apenas se tiver dados mínimos
                    if latitude is not None or longitude is not None or speed_knots is not None:
                        operational_data = {
                            "vessel_id": vessel_id,
                            "timestamp": timestamp,
                            "latitude": latitude,
                            "longitude": longitude,
                            "speed_knots": speed_knots,
                            "heading": heading,
                        }
                        
                        OperationalDataRepository.create(db, operational_data)
                        count += 1
                        
                        # Limitar para não sobrecarregar
                        if count >= 1000:
                            break
                            
                except Exception as e:
                    print(f"⚠️  Erro ao processar linha: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erro ao importar {csv_path}: {e}")
    
    return count


def import_consumption_data(db: Session, csv_path: str) -> int:
    """
    Importa dados de consumo do CSV para operational_data
    
    Args:
        db: Sessão do banco de dados
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        Número de registros importados
    """
    if not os.path.exists(csv_path):
        print(f"⚠️  Arquivo não encontrado: {csv_path}")
        return 0
    
    count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            f.seek(0)
            delimiter = ',' if ',' in first_line else ';'
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                try:
                    # Extrair dados
                    vessel_id = None
                    timestamp = None
                    fuel_consumption = None
                    engine_power = None
                    
                    for key, value in row.items():
                        key_lower = key.lower()
                        
                        # ID da embarcação
                        if any(x in key_lower for x in ['vessel', 'navio', 'embarcação', 'id', 'imo']):
                            vessel_id = str(value).strip()
                        
                        # Timestamp
                        if any(x in key_lower for x in ['timestamp', 'data', 'date', 'hora', 'time']):
                            timestamp = parse_datetime(str(value))
                        
                        # Consumo de combustível
                        if any(x in key_lower for x in ['consumo', 'consumption', 'fuel', 'combustivel']):
                            try:
                                fuel_consumption = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                        
                        # Potência do motor
                        if any(x in key_lower for x in ['power', 'potencia', 'engine']):
                            try:
                                engine_power = float(value) if value else None
                            except (ValueError, TypeError):
                                pass
                    
                    if vessel_id and timestamp:
                        # Buscar embarcação por ID ou nome
                        vessel = VesselRepository.get_by_id(db, vessel_id)
                        if not vessel:
                            # Tentar buscar por nome
                            vessels = VesselRepository.get_all(db)
                            for v in vessels:
                                if vessel_id.lower() in v.name.lower() or v.name.lower() in vessel_id.lower():
                                    vessel = v
                                    break
                        
                        if vessel:
                            operational_data = {
                                "vessel_id": vessel.id,
                                "timestamp": timestamp,
                                "fuel_consumption_kg_h": fuel_consumption,
                                "engine_power_kw": engine_power,
                            }
                            
                            OperationalDataRepository.create(db, operational_data)
                            count += 1
                            
                            if count >= 5000:
                                break
                                
                except Exception as e:
                    print(f"⚠️  Erro ao processar linha: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erro ao importar {csv_path}: {e}")
    
    return count


def import_events_data(db: Session, csv_path: str) -> int:
    """
    Importa dados de eventos do CSV para maintenance_events
    
    Args:
        db: Sessão do banco de dados
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        Número de registros importados
    """
    if not os.path.exists(csv_path):
        print(f"⚠️  Arquivo não encontrado: {csv_path}")
        return 0
    
    count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            f.seek(0)
            delimiter = ',' if ',' in first_line else ';'
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                try:
                    # Extrair dados
                    vessel_id = None
                    start_date = None
                    event_type = None
                    description = None
                    
                    for key, value in row.items():
                        key_lower = key.lower()
                        
                        # ID da embarcação
                        if any(x in key_lower for x in ['vessel', 'navio', 'embarcação', 'id']):
                            vessel_id = str(value).strip()
                        
                        # Data
                        if any(x in key_lower for x in ['data', 'date', 'timestamp', 'inicio', 'start']):
                            start_date = parse_datetime(str(value))
                        
                        # Tipo de evento
                        if any(x in key_lower for x in ['tipo', 'type', 'evento', 'event']):
                            event_type = str(value).strip().lower()
                        
                        # Descrição
                        if any(x in key_lower for x in ['descrição', 'description', 'descricao', 'obs', 'observação']):
                            description = str(value).strip()
                    
                    # Extrair shipName se disponível
                    ship_name = None
                    for key, value in row.items():
                        key_lower = key.lower()
                        if 'shipname' in key_lower or 'ship_name' in key_lower:
                            ship_name = str(value).strip()
                            break
                    
                    # Se não tem vessel_id mas tem shipName, usar mapper
                    if not vessel_id and ship_name:
                        vessel = VesselNameMapper.find_vessel_by_name(db, ship_name)
                        if vessel:
                            vessel_id = vessel.id
                    
                    if vessel_id and start_date:
                        # Buscar embarcação por ID
                        vessel = VesselRepository.get_by_id(db, vessel_id)
                        if not vessel:
                            # Tentar buscar por nome usando mapper
                            vessel = VesselNameMapper.find_vessel_by_name(db, vessel_id)
                            if vessel:
                                vessel_id = vessel.id
                        
                        if vessel:
                            # Normalizar tipo de evento
                            if not event_type:
                                event_type = "maintenance"
                            
                            if "limpeza" in event_type or "cleaning" in event_type:
                                event_type = "cleaning"
                            elif "inspeção" in event_type or "inspection" in event_type:
                                event_type = "inspection"
                            elif "reparo" in event_type or "repair" in event_type:
                                event_type = "repair"
                            else:
                                event_type = "maintenance"
                            
                            maintenance_data = {
                                "vessel_id": vessel.id,
                                "event_type": event_type,
                                "start_date": start_date,
                                "description": description or f"Evento importado de {csv_path}",
                                "maintenance_type": "preventive",
                            }
                            
                            MaintenanceEventRepository.create(db, maintenance_data)
                            count += 1
                            
                            if count >= 1000:
                                break
                                
                except Exception as e:
                    print(f"⚠️  Erro ao processar linha: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erro ao importar {csv_path}: {e}")
    
    return count


def map_vessel_name_to_id(vessel_name: str, db: Session) -> Optional[str]:
    """
    Mapeia nome de embarcação para ID no banco (wrapper para VesselNameMapper)
    
    Args:
        vessel_name: Nome da embarcação
        db: Sessão do banco de dados
        
    Returns:
        ID da embarcação ou None
    """
    vessel = VesselNameMapper.find_vessel_by_name(db, vessel_name)
    return vessel.id if vessel else None


def import_all_ais_data(db: Session) -> Dict[str, int]:
    """
    Importa todos os arquivos CSV AIS da pasta dados/
    
    Returns:
        Dicionário com contagem por embarcação
    """
    ais_folder = DATA_BASE_PATH / "Dados AIS frota TP"
    
    if not ais_folder.exists():
        print(f"⚠️  Pasta não encontrada: {ais_folder}")
        return {}
    
    results = {}
    
    # Listar todos os CSVs
    csv_files = list(ais_folder.glob("*.csv"))
    print(f"📁 Encontrados {len(csv_files)} arquivos CSV AIS")
    
    for csv_file in csv_files:
        vessel_name = csv_file.stem  # Nome do arquivo sem extensão
        print(f"\n📊 Processando: {vessel_name}")
        
        # Importar dados (a função import_ais_data agora recebe vessel_name e faz o mapeamento internamente)
        count = import_ais_data(db, vessel_name, str(csv_file))
        results[vessel_name] = count
        print(f"✅ {count} registros importados para {vessel_name}")
    
    return results


def import_all_real_data(db: Session) -> Dict[str, any]:
    """
    Importa todos os dados reais da pasta dados/
    
    Returns:
        Dicionário com resultados da importação
    """
    print("🚀 Iniciando importação de dados reais...")
    print(f"📁 Pasta de dados: {DATA_BASE_PATH}")
    
    results = {
        "ais_data": {},
        "consumption_data": 0,
        "events_data": 0,
    }
    
    # 1. Importar dados AIS
    print("\n" + "="*60)
    print("1️⃣  Importando dados AIS...")
    print("="*60)
    results["ais_data"] = import_all_ais_data(db)
    
    # 2. Importar dados de consumo
    print("\n" + "="*60)
    print("2️⃣  Importando dados de consumo...")
    print("="*60)
    consumption_file = DATA_BASE_PATH / "ResultadoQueryConsumo.csv"
    if consumption_file.exists():
        results["consumption_data"] = import_consumption_data(db, str(consumption_file))
        print(f"✅ {results['consumption_data']} registros de consumo importados")
    else:
        print(f"⚠️  Arquivo não encontrado: {consumption_file}")
    
    # 3. Importar dados de eventos
    print("\n" + "="*60)
    print("3️⃣  Importando dados de eventos...")
    print("="*60)
    events_file = DATA_BASE_PATH / "ResultadoQueryEventos.csv"
    if events_file.exists():
        results["events_data"] = import_events_data(db, str(events_file))
        print(f"✅ {results['events_data']} registros de eventos importados")
    else:
        print(f"⚠️  Arquivo não encontrado: {events_file}")
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DA IMPORTAÇÃO")
    print("="*60)
    print(f"✅ Dados AIS: {sum(results['ais_data'].values())} registros")
    print(f"✅ Dados de consumo: {results['consumption_data']} registros")
    print(f"✅ Dados de eventos: {results['events_data']} registros")
    print(f"📈 Total: {sum(results['ais_data'].values()) + results['consumption_data'] + results['events_data']} registros")
    
    return results


if __name__ == "__main__":
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        import_all_real_data(db)
    finally:
        db.close()

