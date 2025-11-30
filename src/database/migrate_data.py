"""
Script de Migração de Dados - HullZero

Migra dados existentes de estruturas antigas para o novo modelo normalizado.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .repositories import (
    VesselRepository,
    FoulingDataRepository,
    OperationalDataRepository,
    MaintenanceEventRepository
)
from .repositories_normalized import (
    ComplianceCheckRepository,
    ComplianceViolationRepository,
    ComplianceWarningRepository,
    ComplianceRecommendationRepository,
    InspectionRepository,
    PaintApplicationRepository,
    SensorCalibrationRepository
)
from ..services.compliance_service import check_normam401_compliance


def migrate_compliance_checks(db: Session):
    """
    Migra verificações de conformidade baseadas em dados de fouling existentes.
    """
    print("🔄 Migrando verificações de conformidade...")
    
    vessels = VesselRepository.get_all(db, limit=1000)
    migrated_count = 0
    
    for vessel in vessels:
        # Buscar última predição de fouling
        latest_fouling = FoulingDataRepository.get_latest(db, vessel.id)
        
        if not latest_fouling:
            continue
        
        # Verificar se já existe uma verificação de conformidade para esta embarcação
        existing_check = ComplianceCheckRepository.get_latest(db, vessel.id)
        if existing_check:
            # Verificar se a data é recente (últimos 7 dias)
            days_diff = (datetime.now() - existing_check.check_date).days
            if days_diff < 7:
                continue  # Já existe verificação recente
        
        # Criar verificação de conformidade
        vessel_type = vessel.vessel_type or "standard"
        check = check_normam401_compliance(
            vessel_id=vessel.id,
            fouling_thickness_mm=latest_fouling.estimated_thickness_mm or 0.0,
            roughness_um=latest_fouling.estimated_roughness_um or 0.0,
            vessel_type=vessel_type
        )
        
        # Persistir verificação
        try:
            check_data = {
                "vessel_id": check.vessel_id,
                "check_date": check.check_date,
                "status": check.status.value,
                "fouling_thickness_mm": check.fouling_thickness_mm,
                "roughness_um": check.roughness_um,
                "max_allowed_thickness_mm": check.max_allowed_thickness_mm,
                "max_allowed_roughness_um": check.max_allowed_roughness_um,
                "compliance_score": check.compliance_score,
                "next_inspection_due": check.next_inspection_due.date() if check.next_inspection_due else None
            }
            
            compliance_check = ComplianceCheckRepository.create(db, check_data)
            
            # Criar violações
            for violation in check.violations:
                violation_data = {
                    "compliance_check_id": compliance_check.id,
                    "violation_type": "thickness_exceeded" if "espessura" in violation.lower() else "roughness_exceeded" if "rugosidade" in violation.lower() else "inspection_overdue",
                    "violation_description": violation,
                    "severity": "critical" if check.status.value == "critical" else "high" if check.status.value == "non_compliant" else "medium"
                }
                ComplianceViolationRepository.create(db, violation_data)
            
            # Criar avisos
            for warning in check.warnings:
                warning_data = {
                    "compliance_check_id": compliance_check.id,
                    "warning_type": "approaching_limit",
                    "warning_description": warning
                }
                ComplianceWarningRepository.create(db, warning_data)
            
            # Criar recomendações
            for recommendation in check.recommendations:
                priority = "urgent" if check.status.value == "critical" else "high" if check.status.value == "non_compliant" else "medium" if check.status.value == "at_risk" else "low"
                recommendation_data = {
                    "compliance_check_id": compliance_check.id,
                    "recommendation_text": recommendation,
                    "priority": priority
                }
                ComplianceRecommendationRepository.create(db, recommendation_data)
            
            migrated_count += 1
        except Exception as e:
            print(f"  ⚠️  Erro ao migrar verificação para {vessel.id}: {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"  ✅ {migrated_count} verificações de conformidade migradas")
    return migrated_count


def migrate_inspections_from_maintenance(db: Session):
    """
    Migra eventos de manutenção do tipo 'inspection' para a tabela de inspeções.
    """
    print("🔄 Migrando inspeções de eventos de manutenção...")
    
    # Buscar todos os eventos de manutenção do tipo 'inspection'
    all_vessels = VesselRepository.get_all(db, limit=1000)
    migrated_count = 0
    
    for vessel in all_vessels:
        maintenance_events = MaintenanceEventRepository.get_by_vessel(
            db, vessel.id, event_type="inspection"
        )
        
        for event in maintenance_events:
            # Verificar se já existe inspeção com esta data
            # Verificar se já existe inspeção próxima a esta data (mesmo mês)
            existing_inspections = InspectionRepository.get_by_vessel(db, vessel.id)
            event_month = event.start_date.month
            event_year = event.start_date.year
            if any(
                i.inspection_date.month == event_month and 
                i.inspection_date.year == event_year
                for i in existing_inspections
            ):
                continue
            
            # Criar inspeção
            try:
                inspection_data = {
                    "vessel_id": vessel.id,
                    "inspection_type": "routine",  # ou determinar baseado em outros campos
                    "inspection_date": event.start_date.date(),
                    "next_inspection_due": (event.start_date + timedelta(days=90)).date(),
                    "fouling_thickness_mm": event.fouling_thickness_before_mm,
                    "roughness_um": event.roughness_before_um,
                    "compliance_status": "compliant",  # Será atualizado se houver verificação
                    "inspector_name": event.inspector_name or "Inspetor NORMAM",
                    "inspection_port_id": None  # TODO: Mapear port_name para port_id
                }
                
                InspectionRepository.create(db, inspection_data)
                migrated_count += 1
            except Exception as e:
                print(f"  ⚠️  Erro ao migrar inspeção para {vessel.id}: {e}")
                db.rollback()
                continue
    
    db.commit()
    print(f"  ✅ {migrated_count} inspeções migradas")
    return migrated_count


def migrate_paint_applications(db: Session):
    """
    Migra informações de pintura das embarcações para a tabela de aplicações de tinta.
    """
    print("🔄 Migrando aplicações de tinta...")
    
    vessels = VesselRepository.get_all(db, limit=1000)
    migrated_count = 0
    
    for vessel in vessels:
        if not vessel.paint_application_date or not vessel.paint_type:
            continue
        
        # Verificar se já existe aplicação de tinta
        existing = PaintApplicationRepository.get_by_vessel(
            db, vessel.id, limit=1
        )
        if existing:
            continue
        
        # Buscar paint_type_id (usar ID padrão ou criar se necessário)
        # Por enquanto, usar um ID padrão baseado no nome
        paint_type_id = f"PAINT_{vessel.paint_type.upper().replace(' ', '_')}" if vessel.paint_type else "PAINT_AFS_STANDARD"
        
        # Criar aplicação de tinta
        try:
            app_date = vessel.paint_application_date.date() if hasattr(vessel.paint_application_date, 'date') else vessel.paint_application_date
            application_data = {
                "vessel_id": vessel.id,
                "paint_type_id": paint_type_id,
                "application_date": app_date,
                "application_port_id": None,  # TODO: Mapear home_port para port_id
                "contractor_id": None,
                "area_m2": vessel.hull_area_m2,
                "cost_brl": None,
                "warranty_days": 1095,  # 3 anos padrão
                "notes": "Migrado de dados existentes"
            }
            
            PaintApplicationRepository.create(db, application_data)
            migrated_count += 1
        except Exception as e:
            print(f"  ⚠️  Erro ao migrar aplicação de tinta para {vessel.id}: {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"  ✅ {migrated_count} aplicações de tinta migradas")
    return migrated_count


def main():
    """
    Executa todas as migrações de dados.
    """
    print("🚀 Iniciando migração de dados...")
    print("")
    
    # Garantir que o banco está inicializado
    init_db()
    
    db = SessionLocal()
    try:
        # Executar migrações
        compliance_count = migrate_compliance_checks(db)
        inspection_count = migrate_inspections_from_maintenance(db)
        paint_count = migrate_paint_applications(db)
        
        print("")
        print("=" * 60)
        print("📊 Resumo da Migração:")
        print(f"  ✅ Verificações de conformidade: {compliance_count}")
        print(f"  ✅ Inspeções: {inspection_count}")
        print(f"  ✅ Aplicações de tinta: {paint_count}")
        print("=" * 60)
        print("")
        print("✅ Migração de dados concluída com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

