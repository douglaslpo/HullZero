"""
Script de Geração de Dados Variados - HullZero

Gera dados realistas e variados de bioincrustação para a frota,
garantindo que o dashboard mostre status diferentes (Conforme, Alerta, Crítico).
"""

import random
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from src.database.database import SessionLocal, init_db
from src.database.models import Vessel, FoulingData
from src.database.models_normalized import ComplianceCheck, ComplianceViolation, ComplianceRecommendation
from src.services.compliance_service import check_normam401_compliance

def generate_varied_data(db: Session):
    """Gera dados variados para todas as embarcações"""
    print("🎲 Gerando dados variados de bioincrustação...")
    
    vessels = db.query(Vessel).all()
    print(f"  Encontrados {len(vessels)} navios.")
    
    count_compliant = 0
    count_warning = 0
    count_critical = 0
    
    for i, vessel in enumerate(vessels):
        # Determinar perfil de risco aleatório para garantir variedade
        # 60% Conforme, 25% Alerta, 15% Crítico
        rand_val = random.random()
        
        if rand_val < 0.60:
            # CONFORME (Verde)
            # Espessura: 0.1 - 3.0 mm
            # Rugosidade: 50 - 200 um
            thickness = random.uniform(0.1, 3.0)
            roughness = random.uniform(50, 200)
            status_target = "compliant"
        elif rand_val < 0.85:
            # ALERTA (Amarelo)
            # Espessura: 3.1 - 5.0 mm
            # Rugosidade: 201 - 400 um
            thickness = random.uniform(3.1, 5.0)
            roughness = random.uniform(201, 400)
            status_target = "at_risk"
        else:
            # CRÍTICO (Vermelho)
            # Espessura: 5.1 - 10.0 mm
            # Rugosidade: 401 - 800 um
            thickness = random.uniform(5.1, 10.0)
            roughness = random.uniform(401, 800)
            status_target = "critical"
            
        # Adicionar ruído realista
        thickness += random.uniform(-0.2, 0.2)
        thickness = max(0.1, round(thickness, 2))
        roughness += random.uniform(-10, 10)
        roughness = max(10, round(roughness, 1))
        
        # Calcular impacto no combustível (fórmula simplificada)
        # Aumento de 1% a cada 100um de rugosidade + 0.5% a cada 1mm de espessura
        fuel_impact = (roughness / 100.0) * 1.0 + (thickness * 0.5)
        fuel_impact = round(fuel_impact, 2)
        
        # Criar registro de FoulingData
        fouling = FoulingData(
            id=str(uuid.uuid4()),
            vessel_id=vessel.id,
            timestamp=datetime.utcnow(),
            estimated_thickness_mm=thickness,
            estimated_roughness_um=roughness,
            fouling_severity="light" if thickness < 3 else "moderate" if thickness < 5 else "severe",
            confidence_score=random.uniform(0.85, 0.99),
            predicted_fuel_impact_percent=fuel_impact,
            predicted_co2_impact_kg=fuel_impact * 150 * 24 * 3.114, # Estimativa: 150kg/h base * 24h * fator CO2
            model_type="hybrid_v2",
            model_version="2.1.0"
        )
        db.add(fouling)
        
        # Gerar Verificação de Conformidade (ComplianceCheck)
        # Usar o serviço existente para garantir lógica consistente
        check = check_normam401_compliance(
            vessel_id=vessel.id,
            fouling_thickness_mm=thickness,
            roughness_um=roughness,
            vessel_type=vessel.vessel_type or "standard"
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
            
            compliance_check = ComplianceCheck(**check_data)
            compliance_check.id = str(uuid.uuid4())
            db.add(compliance_check)
            
            # Contadores
            if check.status.value == "compliant": count_compliant += 1
            elif check.status.value == "at_risk": count_warning += 1
            else: count_critical += 1
            
            # Criar violações se houver
            for violation in check.violations:
                viol = ComplianceViolation(
                    id=str(uuid.uuid4()),
                    compliance_check_id=compliance_check.id,
                    violation_type="limit_exceeded",
                    violation_description=violation,
                    severity="critical" if check.status.value == "critical" else "high"
                )
                db.add(viol)
                
            # Criar recomendações se houver
            for rec in check.recommendations:
                recommendation = ComplianceRecommendation(
                    id=str(uuid.uuid4()),
                    compliance_check_id=compliance_check.id,
                    recommendation_text=rec,
                    priority="urgent" if check.status.value == "critical" else "medium"
                )
                db.add(recommendation)
                
        except Exception as e:
            print(f"⚠️ Erro ao gerar compliance para {vessel.name}: {e}")
            
    db.commit()
    print("\n📊 Resumo da Geração:")
    print(f"  ✅ Conforme: {count_compliant} navios")
    print(f"  ⚠️  Alerta: {count_warning} navios")
    print(f"  ❌ Crítico: {count_critical} navios")
    print(f"  Total: {len(vessels)} navios atualizados.")

def main():
    print("🚀 Iniciando geração de dados variados...")
    init_db()
    db = SessionLocal()
    
    try:
        generate_varied_data(db)
        print("✨ Geração finalizada com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
