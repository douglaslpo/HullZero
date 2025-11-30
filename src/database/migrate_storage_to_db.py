"""
Script de Migração: Storage em Memória -> Banco de Dados

Migra dados do armazenamento em memória (_vessels_storage) para o banco de dados.
"""

from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .repositories import VesselRepository
from ..data.transpetro_fleet_data import get_transpetro_fleet


def migrate_fleet_to_database():
    """
    Migra a frota Transpetro do módulo de dados para o banco de dados.
    """
    print("🔄 Migrando frota Transpetro para o banco de dados...")
    
    # Garantir que o banco está inicializado
    init_db()
    
    db = SessionLocal()
    
    try:
        fleet = get_transpetro_fleet()
        migrated = 0
        skipped = 0
        
        for vessel_data in fleet:
            # Verificar se já existe
            existing = VesselRepository.get_by_id(db, vessel_data["id"])
            if existing:
                skipped += 1
                continue
            
            # Converter dados
            vessel_dict = {
                "id": vessel_data["id"],
                "name": vessel_data["name"],
                "imo_number": vessel_data.get("imo_number"),
                "call_sign": vessel_data.get("call_sign"),
                "vessel_type": vessel_data.get("vessel_type"),
                "vessel_class": vessel_data.get("vessel_class"),
                "fleet_category": vessel_data.get("fleet_category"),
                "length_m": vessel_data.get("length_m"),
                "width_m": vessel_data.get("width_m"),
                "draft_m": vessel_data.get("draft_m"),
                "hull_area_m2": vessel_data.get("hull_area_m2"),
                "displacement_tonnes": vessel_data.get("displacement_tonnes"),
                "dwt": vessel_data.get("dwt"),
                "hull_material": vessel_data.get("hull_material", "steel"),
                "paint_type": vessel_data.get("paint_type"),
                "paint_application_date": None,
                "max_speed_knots": vessel_data.get("max_speed_knots"),
                "typical_speed_knots": vessel_data.get("typical_speed_knots"),
                "engine_type": vessel_data.get("engine_type"),
                "engine_power_kw": vessel_data.get("engine_power_kw"),
                "fuel_type": vessel_data.get("fuel_type"),
                "typical_consumption_kg_h": vessel_data.get("typical_consumption_kg_h"),
                "operating_routes": vessel_data.get("operating_routes"),
                "home_port": vessel_data.get("home_port"),
                "status": vessel_data.get("status", "active"),
                "construction_year": vessel_data.get("construction_year"),
                "construction_country": vessel_data.get("construction_country"),
                "dp2_capable": vessel_data.get("dp2_capable", False),
                "offshore_operations": vessel_data.get("offshore_operations", False),
                "dynamic_positioning": vessel_data.get("dynamic_positioning"),
                "cargo_types": vessel_data.get("cargo_types"),
                "gas_capacity_m3": vessel_data.get("gas_capacity_m3"),
                "emission_standard": vessel_data.get("emission_standard"),
                "fuel_alternatives": vessel_data.get("fuel_alternatives")
            }
            
            # Converter data de aplicação da tinta
            if vessel_data.get("paint_application_date"):
                from datetime import datetime
                try:
                    vessel_dict["paint_application_date"] = datetime.fromisoformat(
                        vessel_data["paint_application_date"]
                    )
                except:
                    pass
            
            # Criar no banco
            VesselRepository.create(db, vessel_dict)
            migrated += 1
        
        print(f"✅ Migração concluída:")
        print(f"   - {migrated} embarcações migradas")
        print(f"   - {skipped} embarcações já existentes (ignoradas)")
        print(f"   - Total no banco: {VesselRepository.get_all(db, limit=1000).__len__()}")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_fleet_to_database()

