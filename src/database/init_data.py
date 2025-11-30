"""
Script de Inicialização de Dados - HullZero

Popula o banco de dados com dados iniciais da frota Transpetro.
"""

from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .models import Vessel, CleaningMethod
from ..data.transpetro_fleet_data import get_transpetro_fleet
from ..services.cleaning_methods_service import CleaningMethodsService
from datetime import datetime


def populate_vessels(db: Session):
    """Popula a tabela de embarcações com dados da frota Transpetro"""
    print("Populando embarcações...")
    
    fleet = get_transpetro_fleet()
    count = 0
    
    for vessel_data in fleet:
        # Verificar se já existe
        existing = db.query(Vessel).filter(Vessel.id == vessel_data["id"]).first()
        if existing:
            continue
        
        # Converter dados para o modelo
        vessel = Vessel(
            id=vessel_data["id"],
            name=vessel_data["name"],
            imo_number=vessel_data.get("imo_number"),
            call_sign=vessel_data.get("call_sign"),
            vessel_type=vessel_data.get("vessel_type"),
            vessel_class=vessel_data.get("vessel_class"),
            fleet_category=vessel_data.get("fleet_category"),
            length_m=vessel_data.get("length_m"),
            width_m=vessel_data.get("width_m"),
            draft_m=vessel_data.get("draft_m"),
            hull_area_m2=vessel_data.get("hull_area_m2"),
            displacement_tonnes=vessel_data.get("displacement_tonnes"),
            dwt=vessel_data.get("dwt"),
            hull_material=vessel_data.get("hull_material", "steel"),
            paint_type=vessel_data.get("paint_type"),
            paint_application_date=datetime.fromisoformat(vessel_data["paint_application_date"]) if vessel_data.get("paint_application_date") else None,
            max_speed_knots=vessel_data.get("max_speed_knots"),
            typical_speed_knots=vessel_data.get("typical_speed_knots"),
            engine_type=vessel_data.get("engine_type"),
            engine_power_kw=vessel_data.get("engine_power_kw"),
            fuel_type=vessel_data.get("fuel_type"),
            typical_consumption_kg_h=vessel_data.get("typical_consumption_kg_h"),
            operating_routes=vessel_data.get("operating_routes"),
            home_port=vessel_data.get("home_port"),
            status=vessel_data.get("status", "active"),
            construction_year=vessel_data.get("construction_year"),
            construction_country=vessel_data.get("construction_country"),
            dp2_capable=vessel_data.get("dp2_capable", False),
            offshore_operations=vessel_data.get("offshore_operations", False),
            dynamic_positioning=vessel_data.get("dynamic_positioning"),
            cargo_types=vessel_data.get("cargo_types"),
            gas_capacity_m3=vessel_data.get("gas_capacity_m3"),
            emission_standard=vessel_data.get("emission_standard"),
            fuel_alternatives=vessel_data.get("fuel_alternatives")
        )
        
        db.add(vessel)
        count += 1
    
    db.commit()
    print(f"✅ {count} embarcações adicionadas ao banco de dados")


def populate_cleaning_methods(db: Session):
    """Popula a tabela de métodos de limpeza"""
    print("Populando métodos de limpeza...")
    
    service = CleaningMethodsService()
    count = 0
    
    for method_code_enum, method_info in service.METHODS_DATABASE.items():
        # Usar o valor do enum (string)
        method_code = method_code_enum.value
        
        # Verificar se já existe
        existing = db.query(CleaningMethod).filter(CleaningMethod.code == method_code).first()
        if existing:
            continue
        
        method = CleaningMethod(
            name=method_info.name,
            code=method_code,
            description=method_info.description,
            category="mechanical", # Default, já que não está no Info explicitamente como string simples as vezes
            efficacy_percent=method_info.effectiveness * 100,
            suitable_for=method_info.suitable_for_vessel_types, # Ajustado para lista de tipos
            cost_per_m2_usd=method_info.cost_per_m2,
            time_per_m2_hours=method_info.duration_hours,
            environmental_impact=method_info.environmental_impact,
            environmental_notes="",
            equipment_required=[],
            safety_requirements=[],
            status="available"
        )
        
        db.add(method)
        count += 1
    
    db.commit()
    print(f"✅ {count} métodos de limpeza adicionados ao banco de dados")


def initialize_database():
    """Inicializa o banco de dados e popula com dados iniciais"""
    print("🚀 Inicializando banco de dados HullZero...")
    
    # Criar tabelas
    init_db()
    print("✅ Tabelas criadas")
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Popular dados
        populate_vessels(db)
        populate_cleaning_methods(db)
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        print(f"📊 Total de embarcações: {db.query(Vessel).count()}")
        print(f"📊 Total de métodos de limpeza: {db.query(CleaningMethod).count()}")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()

