"""
Inicialização de Dados de Referência - HullZero

Popula as tabelas de referência com dados iniciais.
"""

from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .models_normalized import (
    VesselType,
    VesselClass,
    PaintType,
    FuelType,
    InvasiveSpecies as InvasiveSpeciesModel
)


def init_reference_data():
    """
    Inicializa dados de referência nas tabelas lookup.
    """
    print("🔄 Inicializando dados de referência...")
    
    # Garantir que o banco está inicializado
    init_db()
    
    db = SessionLocal()
    
    try:
        # ============================================================
        # TIPOS DE EMBARCAÇÃO
        # ============================================================
        vessel_types = [
            {"id": "tanker", "name": "Tanker", "category": "tanker"},
            {"id": "gas_carrier", "name": "Gas Carrier", "category": "tanker"},
            {"id": "cargo", "name": "Cargo Ship", "category": "cargo"},
            {"id": "container", "name": "Container Ship", "category": "container"},
            {"id": "barge", "name": "Barge", "category": "barge"},
            {"id": "tug", "name": "Tugboat", "category": "tug"},
        ]
        
        for vt_data in vessel_types:
            existing = db.query(VesselType).filter(VesselType.id == vt_data["id"]).first()
            if not existing:
                vessel_type = VesselType(**vt_data)
                db.add(vessel_type)
                print(f"  ✅ Criado: {vt_data['name']}")
            else:
                print(f"  ⏭️  Já existe: {vt_data['name']}")
        
        # ============================================================
        # CLASSES DE EMBARCAÇÃO
        # ============================================================
        vessel_classes = [
            {"id": "suezmax", "name": "Suezmax", "typical_length_m": 275, "typical_dwt": 160000},
            {"id": "aframax", "name": "Aframax", "typical_length_m": 250, "typical_dwt": 120000},
            {"id": "panamax", "name": "Panamax", "typical_length_m": 225, "typical_dwt": 80000},
            {"id": "handysize", "name": "Handysize", "typical_length_m": 180, "typical_dwt": 50000},
            {"id": "vlcc", "name": "VLCC", "typical_length_m": 330, "typical_dwt": 300000},
        ]
        
        for vc_data in vessel_classes:
            existing = db.query(VesselClass).filter(VesselClass.id == vc_data["id"]).first()
            if not existing:
                vessel_class = VesselClass(**vc_data)
                db.add(vessel_class)
                print(f"  ✅ Criado: {vc_data['name']}")
            else:
                print(f"  ⏭️  Já existe: {vc_data['name']}")
        
        # ============================================================
        # TIPOS DE TINTA
        # ============================================================
        paint_types = [
            {
                "id": "afs_standard",
                "name": "AFS Standard",
                "category": "AFS",
                "typical_lifespan_days": 1095,
                "environmental_rating": "medium"
            },
            {
                "id": "afs_plus",
                "name": "AFS Plus",
                "category": "AFS",
                "typical_lifespan_days": 1460,
                "environmental_rating": "low"
            },
            {
                "id": "foul_release",
                "name": "Foul Release",
                "category": "Foul-release",
                "typical_lifespan_days": 1825,
                "environmental_rating": "low"
            },
            {
                "id": "hybrid",
                "name": "Hybrid AFS",
                "category": "Hybrid",
                "typical_lifespan_days": 1275,
                "environmental_rating": "medium"
            },
        ]
        
        for pt_data in paint_types:
            existing = db.query(PaintType).filter(PaintType.id == pt_data["id"]).first()
            if not existing:
                paint_type = PaintType(**pt_data)
                db.add(paint_type)
                print(f"  ✅ Criado: {pt_data['name']}")
            else:
                print(f"  ⏭️  Já existe: {pt_data['name']}")
        
        # ============================================================
        # TIPOS DE COMBUSTÍVEL
        # ============================================================
        fuel_types = [
            {
                "id": "mgo",
                "name": "Marine Gas Oil",
                "category": "fossil",
                "co2_emission_factor_kg_per_kg": 3.206,
                "energy_density_mj_per_kg": 42.7
            },
            {
                "id": "hfo",
                "name": "Heavy Fuel Oil",
                "category": "fossil",
                "co2_emission_factor_kg_per_kg": 3.114,
                "energy_density_mj_per_kg": 40.2
            },
            {
                "id": "lng",
                "name": "Liquefied Natural Gas",
                "category": "lng",
                "co2_emission_factor_kg_per_kg": 2.750,
                "energy_density_mj_per_kg": 50.0
            },
            {
                "id": "biofuel",
                "name": "Biofuel",
                "category": "biofuel",
                "co2_emission_factor_kg_per_kg": 2.500,
                "energy_density_mj_per_kg": 37.0
            },
        ]
        
        for ft_data in fuel_types:
            existing = db.query(FuelType).filter(FuelType.id == ft_data["id"]).first()
            if not existing:
                fuel_type = FuelType(**ft_data)
                db.add(fuel_type)
                print(f"  ✅ Criado: {ft_data['name']}")
            else:
                print(f"  ⏭️  Já existe: {ft_data['name']}")
        
        # ============================================================
        # ESPÉCIES INVASORAS
        # ============================================================
        invasive_species = [
            {
                "id": "coral_sol",
                "scientific_name": "Tubastraea coccinea",
                "common_name": "Coral Sol",
                "code": "CORAL_SOL",
                "category": "coral",
                "removal_difficulty": 0.8
            },
            {
                "id": "mexilhao_dourado",
                "scientific_name": "Limnoperna fortunei",
                "common_name": "Mexilhão Dourado",
                "code": "MEXILHAO_DOURADO",
                "category": "mollusk",
                "removal_difficulty": 0.7
            },
            {
                "id": "mexilhao_verde",
                "scientific_name": "Perna viridis",
                "common_name": "Mexilhão Verde",
                "code": "MEXILHAO_VERDE",
                "category": "mollusk",
                "removal_difficulty": 0.6
            },
            {
                "id": "barnacles",
                "scientific_name": "Amphibalanus amphitrite",
                "common_name": "Barnacles",
                "code": "BARNAQUES",
                "category": "barnacle",
                "removal_difficulty": 0.5
            },
        ]
        
        for is_data in invasive_species:
            existing = db.query(InvasiveSpeciesModel).filter(InvasiveSpeciesModel.id == is_data["id"]).first()
            if not existing:
                species = InvasiveSpeciesModel(**is_data)
                db.add(species)
                print(f"  ✅ Criado: {is_data['common_name']}")
            else:
                print(f"  ⏭️  Já existe: {is_data['common_name']}")
        
        # Commit todas as alterações
        db.commit()
        print("\n✅ Dados de referência inicializados com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao inicializar dados de referência: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_reference_data()

