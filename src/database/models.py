"""
Modelos de Banco de Dados - HullZero

Define todas as tabelas e relacionamentos usando SQLAlchemy ORM.
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Boolean,
    ForeignKey, JSON, DECIMAL, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Vessel(Base):
    """
    Tabela de Embarcações
    """
    __tablename__ = "vessels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    imo_number = Column(String(20), unique=True, index=True)
    call_sign = Column(String(20))
    
    # Tipo e Classe
    vessel_type = Column(String(100), index=True)  # tanker, gas_carrier, etc.
    vessel_class = Column(String(100), index=True)  # Suezmax, Aframax, etc.
    fleet_category = Column(String(100), index=True)  # suezmax, aframax, etc.
    
    # Dimensões
    length_m = Column(Float)
    width_m = Column(Float)
    draft_m = Column(Float)
    hull_area_m2 = Column(Float)
    displacement_tonnes = Column(Float)
    dwt = Column(Float)  # Deadweight tonnage
    
    # Características
    hull_material = Column(String(50), default="steel")
    paint_type = Column(String(100))
    paint_application_date = Column(DateTime)
    paint_age_days = Column(Integer)
    
    # Performance
    max_speed_knots = Column(Float)
    typical_speed_knots = Column(Float)
    engine_type = Column(String(50))
    engine_power_kw = Column(Float)
    fuel_type = Column(String(50))
    typical_consumption_kg_h = Column(Float)
    
    # Operação
    operating_routes = Column(JSON)  # Lista de rotas
    home_port = Column(String(255))
    status = Column(String(50), default="active", index=True)  # active, inactive, under_construction
    
    # Construção
    construction_year = Column(Integer)
    construction_country = Column(String(100))
    
    # Específicos
    dp2_capable = Column(Boolean, default=False)
    offshore_operations = Column(Boolean, default=False)
    dynamic_positioning = Column(String(20))
    cargo_types = Column(JSON)  # Para navios de produtos
    gas_capacity_m3 = Column(Float)  # Para gaseiros
    emission_standard = Column(String(50))  # Tier III, etc.
    fuel_alternatives = Column(JSON)  # Lista de combustíveis alternativos
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fouling_data = relationship("FoulingData", back_populates="vessel", cascade="all, delete-orphan")
    operational_data = relationship("OperationalData", back_populates="vessel", cascade="all, delete-orphan")
    maintenance_events = relationship("MaintenanceEvent", back_populates="vessel", cascade="all, delete-orphan")
    normam401_risks = relationship("NORMAM401Risk", back_populates="vessel", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="vessel", cascade="all, delete-orphan")
    corrective_actions = relationship("CorrectiveAction", back_populates="vessel", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_vessel_status", "status"),
        Index("idx_vessel_type_class", "vessel_type", "vessel_class"),
    )


class FoulingData(Base):
    """
    Dados de Bioincrustação (Time Series)
    """
    __tablename__ = "fouling_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    # Dados de bioincrustação
    estimated_thickness_mm = Column(Float)
    estimated_roughness_um = Column(Float)
    fouling_severity = Column(String(50), index=True)  # light, moderate, severe, critical
    confidence_score = Column(Float)
    
    # Impactos
    predicted_fuel_impact_percent = Column(Float)
    predicted_co2_impact_kg = Column(Float)
    
    # Modelo usado
    model_type = Column(String(50))  # physical, ml, hybrid, advanced
    model_version = Column(String(20))
    
    # Features usadas na predição
    features = Column(JSON)  # Features usadas na predição
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="fouling_data")
    
    __table_args__ = (
        Index("idx_fouling_vessel_time", "vessel_id", "timestamp"),
        Index("idx_fouling_timestamp", "timestamp"),
    )


class OperationalData(Base):
    """
    Dados Operacionais (Time Series)
    """
    __tablename__ = "operational_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    # Navegação
    latitude = Column(Float)
    longitude = Column(Float)
    speed_knots = Column(Float)
    heading = Column(Float)
    
    # Propulsão
    engine_power_kw = Column(Float)
    rpm = Column(Integer)
    fuel_consumption_kg_h = Column(Float)
    
    # Condições ambientais
    water_temperature_c = Column(Float)
    salinity_psu = Column(Float)
    wind_speed_knots = Column(Float)
    wave_height_m = Column(Float)
    current_velocity = Column(Float)
    depth_m = Column(Float)
    
    # Qualidade da água
    port_water_quality_index = Column(Float)
    chlorophyll_a_concentration = Column(Float)
    dissolved_oxygen = Column(Float)
    ph_level = Column(Float)
    turbidity = Column(Float)
    
    # Carga
    cargo_load_percent = Column(Float)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="operational_data")
    
    __table_args__ = (
        Index("idx_operational_vessel_time", "vessel_id", "timestamp"),
        Index("idx_operational_timestamp", "timestamp"),
    )


class MaintenanceEvent(Base):
    """
    Eventos de Manutenção e Limpeza
    """
    __tablename__ = "maintenance_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    
    # Tipo de evento
    event_type = Column(String(50), nullable=False, index=True)  # cleaning, inspection, repair, paint_application
    maintenance_type = Column(String(50))  # preventive, corrective, emergency
    
    # Datas
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime)
    duration_hours = Column(Float)
    
    # Detalhes
    description = Column(Text)
    location = Column(String(255))  # Porto, estaleiro, etc.
    contractor = Column(String(255))  # Empresa responsável
    
    # Método de limpeza
    cleaning_method = Column(String(100))
    cleaning_method_details = Column(JSON)
    photos_paths = Column(JSON)  # Lista de caminhos das fotos
    
    # Resultados
    fouling_thickness_before_mm = Column(Float)
    fouling_thickness_after_mm = Column(Float)
    roughness_before_um = Column(Float)
    roughness_after_um = Column(Float)
    
    # Custos
    cost_brl = Column(Float)
    cost_usd = Column(Float)
    
    # Status
    status = Column(String(50), default="completed", index=True)  # planned, in_progress, completed, cancelled
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="maintenance_events")
    
    __table_args__ = (
        Index("idx_maintenance_vessel_date", "vessel_id", "start_date"),
        Index("idx_maintenance_type", "event_type"),
    )


class NORMAM401Risk(Base):
    """
    Riscos NORMAM 401
    """
    __tablename__ = "normam401_risks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    
    # Risco
    risk_score = Column(Float, nullable=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    confidence_score = Column(Float)
    
    # Predições
    predicted_fouling_mm = Column(Float)
    predicted_roughness_um = Column(Float)
    days_ahead = Column(Integer)  # Quantos dias à frente
    
    # Fatores de risco
    risk_factors = Column(JSON)  # Lista de fatores identificados
    recommendations = Column(JSON)  # Recomendações
    
    # Timeline
    risk_timeline = Column(JSON)  # Evolução do risco ao longo do tempo
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="normam401_risks")
    
    __table_args__ = (
        Index("idx_risk_vessel_date", "vessel_id", "created_at"),
        Index("idx_risk_level", "risk_level"),
    )


class Anomaly(Base):
    """
    Anomalias Detectadas
    """
    __tablename__ = "anomalies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    
    # Tipo e severidade
    anomaly_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    # Detalhes
    description = Column(Text)
    detected_value = Column(Float)
    expected_value = Column(Float)
    deviation_percent = Column(Float)
    
    # Datas
    detected_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Status
    status = Column(String(50), default="open", index=True)  # open, investigating, resolved, false_positive
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="anomalies")
    
    __table_args__ = (
        Index("idx_anomaly_vessel_date", "vessel_id", "detected_at"),
        Index("idx_anomaly_status", "status"),
    )


class CorrectiveAction(Base):
    """
    Ações Corretivas
    """
    __tablename__ = "corrective_actions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    compliance_issue_id = Column(String)  # Referência a risco ou anomalia
    
    # Tipo e prioridade
    action_type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)  # low, medium, high, urgent
    
    # Detalhes
    description = Column(Text)
    deadline = Column(DateTime, index=True)
    
    # Estimativas
    estimated_cost_brl = Column(Float)
    estimated_cost_usd = Column(Float)
    estimated_duration_hours = Column(Float)
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, approved, in_progress, completed, cancelled
    
    # Execução
    executed_at = Column(DateTime)
    actual_cost_brl = Column(Float)
    actual_duration_hours = Column(Float)
    execution_notes = Column(Text)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    vessel = relationship("Vessel", back_populates="corrective_actions")
    
    __table_args__ = (
        Index("idx_action_vessel_status", "vessel_id", "status"),
        Index("idx_action_deadline", "deadline"),
    )


class PredictionExplanation(Base):
    """
    Explicações de Predições (Explicabilidade)
    """
    __tablename__ = "prediction_explanations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False, index=True)
    prediction_id = Column(String)  # Referência à predição (fouling_data.id)
    
    # Tipo de explicação
    explanation_type = Column(String(50), nullable=False)  # fouling, compliance, fuel_impact, etc.
    
    # Contribuições de features
    feature_contributions = Column(JSON)  # Dict com contribuição de cada feature
    feature_importance = Column(JSON)  # Importância de features
    
    # Explicação textual
    explanation_text = Column(Text)
    
    # SHAP values (se disponível)
    shap_values = Column(JSON)
    
    # Modelo usado
    model_type = Column(String(50))
    model_version = Column(String(20))
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_explanation_vessel_date", "vessel_id", "created_at"),
        Index("idx_explanation_type", "explanation_type"),
    )


class CleaningMethod(Base):
    """
    Métodos de Limpeza Disponíveis
    """
    __tablename__ = "cleaning_methods"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), unique=True, index=True)
    
    # Características
    description = Column(Text)
    category = Column(String(50), index=True)  # mechanical, chemical, biological, etc.
    
    # Eficácia
    efficacy_percent = Column(Float)  # 0-100
    suitable_for = Column(JSON)  # Tipos de bioincrustação
    
    # Custos
    cost_per_m2_brl = Column(Float)
    cost_per_m2_usd = Column(Float)
    
    # Tempo
    time_per_m2_hours = Column(Float)
    
    # Impacto ambiental
    environmental_impact = Column(String(50))  # low, medium, high
    environmental_notes = Column(Text)
    
    # Requisitos
    equipment_required = Column(JSON)
    safety_requirements = Column(JSON)
    
    # Status
    status = Column(String(50), default="available", index=True)  # available, deprecated, experimental
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_cleaning_method_category", "category"),
        Index("idx_cleaning_method_status", "status"),
    )

