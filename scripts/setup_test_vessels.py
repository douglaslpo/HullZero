import sys
import os
from datetime import datetime, timedelta
import random
import uuid

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import SessionLocal
from src.database.repositories import VesselRepository, FoulingDataRepository
from src.database.models import Vessel, FoulingData

def setup_test_vessels():
    print("🚀 Configurando Navios de Teste...")
    db = SessionLocal()
    
    test_vessels = [
        {"name": "NAVIO TESTE 1", "type": "Tanker", "class": "Suezmax"},
        {"name": "NAVIO TESTE 2", "type": "Gas Carrier", "class": "LPG"},
        {"name": "NAVIO TESTE 3", "type": "Bulk Carrier", "class": "Panamax"},
        {"name": "NAVIO TESTE 4", "type": "Container Ship", "class": "Post-Panamax"}
    ]
    
    try:
        for v_data in test_vessels:
            name = v_data["name"]
            print(f"\n🚢 Processando {name}...")
            
            # 1. Verificar/Criar Navio
            vessel = VesselRepository.get_by_name(db, name)
            if not vessel:
                print(f"   🆕 Criando navio...")
                vessel = Vessel(
                    id=str(uuid.uuid4()),
                    name=name,
                    imo_number=f"TEST{random.randint(10000, 99999)}",
                    vessel_type=v_data["type"],
                    vessel_class=v_data["class"],
                    status="active",
                    hull_area_m2=5000.0 + random.uniform(-500, 500),
                    dwt=100000.0,
                    length_m=250.0,
                    width_m=45.0,
                    draft_m=15.0
                )
                db.add(vessel)
                db.commit()
                db.refresh(vessel)
            else:
                print(f"   ✅ Navio já existe.")
            
            # 2. Gerar Histórico de Dados (últimos 6 meses)
            print(f"   📊 Gerando histórico de dados...")
            
            # Verificar se já tem dados
            existing_data = FoulingDataRepository.get_by_vessel(db, vessel.id)
            if len(existing_data) > 10:
                print("   ✅ Histórico já existe.")
                continue
                
            # Gerar dados diários
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            current_date = start_date
            
            # Estado inicial aleatório
            thickness = random.uniform(0.1, 1.0)
            roughness = random.uniform(50, 100)
            
            while current_date <= end_date:
                # Evolução natural
                thickness += random.uniform(0.005, 0.02) # Crescimento diário
                roughness += random.uniform(0.5, 2.0)
                
                # Severidade
                if thickness < 3.0: severity = "light"
                elif thickness < 6.0: severity = "moderate"
                else: severity = "severe"
                
                # Impacto
                fuel_impact = (thickness * 0.5) + (roughness / 100.0)
                
                data = FoulingData(
                    id=str(uuid.uuid4()),
                    vessel_id=vessel.id,
                    timestamp=current_date,
                    estimated_thickness_mm=round(thickness, 3),
                    estimated_roughness_um=round(roughness, 1),
                    fouling_severity=severity,
                    confidence_score=random.uniform(0.85, 0.99),
                    predicted_fuel_impact_percent=round(fuel_impact, 2),
                    predicted_co2_impact_kg=round(fuel_impact * 1000, 2),
                    model_type="simulation",
                    features={}
                )
                db.add(data)
                
                current_date += timedelta(days=1)
            
            db.commit()
            print("   ✅ Histórico gerado com sucesso.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_vessels()
