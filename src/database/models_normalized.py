"""
Modelos Normalizados de Banco de Dados - HullZero

Modelos SQLAlchemy para as novas tabelas normalizadas.
Estes modelos complementam os modelos existentes em models.py.
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Boolean,
    ForeignKey, JSON, DECIMAL, Date, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .models import Base


# ============================================================
# TABELAS DE REFERÊNCIA (Lookup Tables)
# ============================================================

class VesselType(Base):
    """Tipos de Embarcação"""
    __tablename__ = "vessel_types"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))  # 'tanker', 'cargo', 'container', etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class VesselClass(Base):
    """Classes de Embarcação"""
    __tablename__ = "vessel_classes"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    typical_length_m = Column(Float)
    typical_dwt = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaintType(Base):
    """Tipos de Tinta"""
    __tablename__ = "paint_types"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    manufacturer = Column(String(100))
    category = Column(String(50))  # 'AFS', 'Foul-release', etc.
    typical_lifespan_days = Column(Integer)
    environmental_rating = Column(String(20))  # 'low', 'medium', 'high'
    created_at = Column(DateTime, default=datetime.utcnow)


class Port(Base):
    """Portos"""
    __tablename__ = "ports"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    country_code = Column(String(3))  # ISO 3166-1 alpha-3
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    port_code = Column(String(20), unique=True)
    timezone = Column(String(50))
    water_quality_index = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Route(Base):
    """Rotas entre Portos"""
    __tablename__ = "routes"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    origin_port_id = Column(String(50), ForeignKey("ports.id"))
    destination_port_id = Column(String(50), ForeignKey("ports.id"))
    typical_duration_days = Column(Integer)
    distance_nm = Column(Float)  # Nautical miles
    region = Column(String(100))  # 'Brazil_Coast', 'Atlantic', etc.
    water_temperature_avg_c = Column(Float)
    salinity_avg_psu = Column(Float)
    risk_level = Column(String(20))  # 'low', 'medium', 'high'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    origin_port = relationship("Port", foreign_keys=[origin_port_id])
    destination_port = relationship("Port", foreign_keys=[destination_port_id])


class Contractor(Base):
    """Contratantes"""
    __tablename__ = "contractors"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    country = Column(String(100))
    specialization = Column(String(100))  # 'cleaning', 'painting', 'inspection', etc.
    certification_level = Column(String(50))
    status = Column(String(20), default="active")  # 'active', 'inactive', 'suspended'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CargoType(Base):
    """Tipos de Carga"""
    __tablename__ = "cargo_types"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))  # 'liquid', 'solid', 'gas', 'container'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class FuelType(Base):
    """Tipos de Combustível"""
    __tablename__ = "fuel_types"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))  # 'fossil', 'biofuel', 'lng', 'electric'
    co2_emission_factor_kg_per_kg = Column(Float)
    energy_density_mj_per_kg = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class InvasiveSpecies(Base):
    """Espécies Invasoras"""
    __tablename__ = "invasive_species"
    
    id = Column(String(50), primary_key=True)
    scientific_name = Column(String(255), nullable=False, unique=True)
    common_name = Column(String(255))
    code = Column(String(50), unique=True)  # 'CORAL_SOL', 'MEXILHAO_DOURADO', etc.
    category = Column(String(50))  # 'coral', 'mollusk', 'barnacle', etc.
    description = Column(Text)
    native_region = Column(String(255))
    invasive_regions = Column(JSON)  # Lista de regiões onde é invasora
    growth_rate_multiplier = Column(Float, default=1.0)
    removal_difficulty = Column(Float)  # 0-1, 1 = muito difícil
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# TABELAS DE RELACIONAMENTO N:N
# ============================================================

class VesselRoute(Base):
    """Rotas de Embarcações (N:N)"""
    __tablename__ = "vessel_routes"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    route_id = Column(String(50), ForeignKey("routes.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    frequency_per_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('vessel_id', 'route_id', name='uq_vessel_route'),
    )


class VesselCargoType(Base):
    """Tipos de Carga de Embarcações (N:N)"""
    __tablename__ = "vessel_cargo_types"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    cargo_type_id = Column(String(50), ForeignKey("cargo_types.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('vessel_id', 'cargo_type_id', name='uq_vessel_cargo'),
    )


class VesselFuelAlternative(Base):
    """Combustíveis Alternativos de Embarcações (N:N)"""
    __tablename__ = "vessel_fuel_alternatives"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    fuel_type_id = Column(String(50), ForeignKey("fuel_types.id"), nullable=False)
    compatibility_level = Column(String(20))  # 'full', 'partial', 'experimental'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('vessel_id', 'fuel_type_id', name='uq_vessel_fuel'),
    )


# ============================================================
# NOVAS ENTIDADES
# ============================================================

class PaintApplication(Base):
    """Aplicações de Tinta"""
    __tablename__ = "paint_applications"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    paint_type_id = Column(String(50), ForeignKey("paint_types.id"), nullable=False)
    application_date = Column(Date, nullable=False)
    application_port_id = Column(String(50), ForeignKey("ports.id"))
    contractor_id = Column(String(50), ForeignKey("contractors.id"))
    area_m2 = Column(Float)
    cost_brl = Column(Float)
    warranty_days = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('area_m2 > 0', name='check_area_positive'),
        CheckConstraint('cost_brl >= 0', name='check_cost_non_negative'),
    )


class SensorCalibration(Base):
    """Calibrações de Sensores"""
    __tablename__ = "sensor_calibrations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50), nullable=False)  # 'fouling', 'roughness', 'temperature', etc.
    calibration_date = Column(Date, nullable=False)
    calibration_port_id = Column(String(50), ForeignKey("ports.id"))
    contractor_id = Column(String(50), ForeignKey("contractors.id"))
    calibration_value_before = Column(Float)
    calibration_value_after = Column(Float)
    next_calibration_due = Column(Date)
    certificate_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Inspection(Base):
    """Inspeções"""
    __tablename__ = "inspections"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    maintenance_event_id = Column(String(50), ForeignKey("maintenance_events.id"))
    
    inspection_type = Column(String(50), nullable=False)  # 'routine', 'compliance', etc.
    inspection_date = Column(Date, nullable=False)
    next_inspection_due = Column(Date)
    
    inspection_port_id = Column(String(50), ForeignKey("ports.id"))
    inspector_name = Column(String(255))
    inspector_company = Column(String(255))
    contractor_id = Column(String(50), ForeignKey("contractors.id"))
    
    fouling_thickness_mm = Column(Float)
    roughness_um = Column(Float)
    compliance_status = Column(String(20))  # 'compliant', 'at_risk', etc.
    compliance_score = Column(Float)
    
    report_path = Column(String(500))
    photos_paths = Column(JSON)
    certificate_number = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('fouling_thickness_mm >= 0', name='check_fouling_non_negative'),
        CheckConstraint('roughness_um >= 0', name='check_roughness_non_negative'),
        CheckConstraint('compliance_score >= 0 AND compliance_score <= 1', name='check_compliance_score_range'),
    )


class ComplianceCheck(Base):
    """Verificações de Conformidade"""
    __tablename__ = "compliance_checks"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    inspection_id = Column(String(50), ForeignKey("inspections.id"))
    
    check_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # 'compliant', 'at_risk', etc.
    
    fouling_thickness_mm = Column(Float, nullable=False)
    roughness_um = Column(Float, nullable=False)
    max_allowed_thickness_mm = Column(Float, nullable=False)
    max_allowed_roughness_um = Column(Float, nullable=False)
    compliance_score = Column(Float, nullable=False)
    next_inspection_due = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('fouling_thickness_mm >= 0', name='check_fouling_non_negative'),
        CheckConstraint('roughness_um >= 0', name='check_roughness_non_negative'),
        CheckConstraint('max_allowed_thickness_mm > 0', name='check_max_thickness_positive'),
        CheckConstraint('max_allowed_roughness_um > 0', name='check_max_roughness_positive'),
        CheckConstraint('compliance_score >= 0 AND compliance_score <= 1', name='check_score_range'),
    )


class ComplianceViolation(Base):
    """Violações de Conformidade"""
    __tablename__ = "compliance_violations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_check_id = Column(String(50), ForeignKey("compliance_checks.id", ondelete="CASCADE"), nullable=False)
    violation_type = Column(String(50), nullable=False)
    violation_description = Column(Text, nullable=False)
    severity = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceWarning(Base):
    """Avisos de Conformidade"""
    __tablename__ = "compliance_warnings"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_check_id = Column(String(50), ForeignKey("compliance_checks.id", ondelete="CASCADE"), nullable=False)
    warning_type = Column(String(50), nullable=False)
    warning_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceRecommendation(Base):
    """Recomendações de Conformidade"""
    __tablename__ = "compliance_recommendations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_check_id = Column(String(50), ForeignKey("compliance_checks.id", ondelete="CASCADE"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String(20))  # 'low', 'medium', 'high', 'urgent'
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskFactor(Base):
    """Fatores de Risco NORMAM 401"""
    __tablename__ = "risk_factors"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_id = Column(String(50), ForeignKey("normam401_risks.id", ondelete="CASCADE"), nullable=False)
    factor_type = Column(String(50), nullable=False)
    factor_description = Column(Text, nullable=False)
    contribution_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('contribution_score >= 0 AND contribution_score <= 1', name='check_contribution_range'),
    )


class RiskRecommendation(Base):
    """Recomendações de Risco NORMAM 401"""
    __tablename__ = "risk_recommendations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_id = Column(String(50), ForeignKey("normam401_risks.id", ondelete="CASCADE"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String(20))  # 'low', 'medium', 'high', 'urgent'
    created_at = Column(DateTime, default=datetime.utcnow)


class InvasiveSpeciesRisk(Base):
    """Riscos de Espécies Invasoras"""
    __tablename__ = "invasive_species_risks"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String(50), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    species_id = Column(String(50), ForeignKey("invasive_species.id"), nullable=False)
    
    risk_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    risk_score = Column(Float, nullable=False)
    growth_rate_multiplier = Column(Float)
    removal_difficulty = Column(Float)
    regions_affected = Column(JSON)
    seasonal_factors = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('risk_score >= 0 AND risk_score <= 1', name='check_risk_score_range'),
        CheckConstraint('growth_rate_multiplier > 0', name='check_growth_positive'),
        CheckConstraint('removal_difficulty >= 0 AND removal_difficulty <= 1', name='check_removal_range'),
        UniqueConstraint('vessel_id', 'species_id', 'created_at', name='uq_invasive_risk'),
    )


class InvasiveSpeciesRecommendation(Base):
    """Recomendações de Espécies Invasoras"""
    __tablename__ = "invasive_species_recommendations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_id = Column(String(50), ForeignKey("invasive_species_risks.id", ondelete="CASCADE"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    recommendation_type = Column(String(50))  # 'biological_control', 'mechanical_removal', etc.
    priority = Column(String(20))  # 'low', 'medium', 'high', 'urgent'
    created_at = Column(DateTime, default=datetime.utcnow)

