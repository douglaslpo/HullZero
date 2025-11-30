"""
Script de Ingestão de Dados Reais - HullZero

Este script lê os dados da pasta `dados/` e popula o banco de dados com:
1. Dados da Frota (Dados navios Hackathon.xlsx)
2. Eventos Operacionais (ResultadoQueryEventos.csv)
3. Consumo de Combustível (ResultadoQueryConsumo.csv)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from src.database.database import SessionLocal, init_db
from src.database.models import Vessel, OperationalData, MaintenanceEvent
from src.database.models_normalized import VesselClass, VesselType

# Configuração de caminhos
BASE_PATH = Path("dados")
FLEET_FILE = BASE_PATH / "Dados navios Hackathon.xlsx"
EVENTS_FILE = BASE_PATH / "ResultadoQueryEventos.csv"
CONSUMPTION_FILE = BASE_PATH / "ResultadoQueryConsumo.csv"

def ingest_fleet_data(db: Session):
    """Ingere dados da frota"""
    print("🚢 Ingerindo dados da frota...")
    
    if not FLEET_FILE.exists():
        print(f"❌ Arquivo não encontrado: {FLEET_FILE}")
        return

    try:
        df = pd.read_excel(FLEET_FILE)
        # Normalizar nomes de colunas se necessário
        
        count = 0
        for _, row in df.iterrows():
            # Mapeamento de colunas baseado na estrutura real do Excel
            # ['Nome do navio', 'Classe', 'Tipo', 'Porte Bruto', 'Comprimento total (m)', 'Boca (m)', 'Calado (m)', 'Pontal (m)']
            name = row.get('Nome do navio')
            if not name:
                continue
                
            # Verificar se navio já existe
            vessel = db.query(Vessel).filter(Vessel.name == name).first()
            if not vessel:
                vessel = Vessel(id=str(uuid.uuid4()))
                db.add(vessel)
            
            # Atualizar dados
            vessel.name = name
            vessel.vessel_type = 'tanker' # Default
            
            # Tipo específico
            tipo = row.get('Tipo')
            if tipo:
                vessel.vessel_type = str(tipo).lower()
            
            # Classe
            classe = row.get('Classe')
            if classe:
                vessel.vessel_class = str(classe).lower()
                vessel.fleet_category = str(classe).lower()
            
            # Dimensões
            if 'Porte Bruto' in row: vessel.dwt = float(row['Porte Bruto'])
            if 'Comprimento total (m)' in row: vessel.length_m = float(row['Comprimento total (m)'])
            if 'Boca (m)' in row: vessel.width_m = float(row['Boca (m)'])
            if 'Calado (m)' in row: vessel.draft_m = float(row['Calado (m)'])
            
            count += 1
        
        db.commit()
        print(f"✅ {count} navios processados.")
        
    except Exception as e:
        print(f"❌ Erro ao ingerir frota: {e}")
        db.rollback()

def ingest_events_and_consumption(db: Session):
    """Ingere eventos e consumo"""
    print("📅 Ingerindo eventos e consumo...")
    
    if not EVENTS_FILE.exists() or not CONSUMPTION_FILE.exists():
        print("❌ Arquivos de eventos ou consumo não encontrados.")
        return

    try:
        # Carregar dados
        print("  ⏳ Lendo arquivos CSV...")
        df_events = pd.read_csv(EVENTS_FILE)
        df_consumption = pd.read_csv(CONSUMPTION_FILE)
        
        # Limpar e preparar dados de consumo
        # Agrupar consumo por SESSION_ID (pode haver múltiplos registros por sessão?)
        # Assumindo que SESSION_ID é único por evento ou precisa ser somado
        consumption_map = df_consumption.groupby('SESSION_ID')['CONSUMED_QUANTITY'].sum().to_dict()
        
        count_ops = 0
        count_maint = 0
        
        # Cache de navios para evitar queries repetidas
        vessels_cache = {v.name: v.id for v in db.query(Vessel).all()}
        
        print(f"  ⏳ Processando {len(df_events)} eventos...")
        
        for _, row in df_events.iterrows():
            ship_name = row.get('shipName')
            if not ship_name or ship_name not in vessels_cache:
                continue
                
            vessel_id = vessels_cache[ship_name]
            session_id = row.get('sessionId')
            event_name = row.get('eventName')
            
            start_date = pd.to_datetime(row.get('startGMTDate'))
            end_date = pd.to_datetime(row.get('endGMTDate'))
            
            # Consumo associado
            fuel_consumed = consumption_map.get(session_id, 0) if session_id else 0
            
            if event_name == 'NAVEGACAO':
                # Criar OperationalData (ponto de dados ou resumo da viagem)
                # Como OperationalData é TimeSeries, podemos criar um registro para o início
                # Ou idealmente teríamos dados diários. Aqui vamos criar um registro representando o evento.
                
                op_data = OperationalData(
                    id=str(uuid.uuid4()),
                    vessel_id=vessel_id,
                    timestamp=start_date,
                    speed_knots=row.get('speed'),
                    fuel_consumption_kg_h=None, # Difícil calcular sem horas exatas de consumo vs duração
                    # Mas podemos salvar o total em algum lugar ou estimar
                    latitude=row.get('decLatitude'),
                    longitude=row.get('decLongitude')
                )
                
                # Se tivermos duração e consumo total, podemos estimar kg/h
                duration = row.get('duration') # Horas
                if duration and duration > 0 and fuel_consumed > 0:
                     # Consumo está em toneladas? O dataset diz 'CONSUMED_QUANTITY'. 
                     # Geralmente é MT (toneladas métricas). Converter para kg.
                     op_data.fuel_consumption_kg_h = (fuel_consumed * 1000) / duration
                
                db.add(op_data)
                count_ops += 1
                
            elif event_name in ['DOCAGEM', 'EM PORTO']:
                # Criar MaintenanceEvent ou apenas registrar parada
                # Se for DOCAGEM, é manutenção importante
                
                maint_type = 'docking' if event_name == 'DOCAGEM' else 'port_stay'
                
                maint_event = MaintenanceEvent(
                    id=str(uuid.uuid4()),
                    vessel_id=vessel_id,
                    event_type=maint_type,
                    start_date=start_date,
                    end_date=end_date,
                    duration_hours=row.get('duration'),
                    location=row.get('Porto'),
                    description=f"Evento importado: {event_name}",
                    status='completed'
                )
                db.add(maint_event)
                count_maint += 1
                
            # Commit em lotes para não estourar memória
            if (count_ops + count_maint) % 1000 == 0:
                db.commit()
        
        db.commit()
        print(f"✅ Processamento concluído: {count_ops} dados operacionais, {count_maint} eventos de manutenção.")
        
    except Exception as e:
        print(f"❌ Erro ao ingerir eventos: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

def main():
    print("🚀 Iniciando ingestão de dados reais...")
    init_db()
    db = SessionLocal()
    
    try:
        ingest_fleet_data(db)
        ingest_events_and_consumption(db)
        print("✨ Ingestão finalizada com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
