-- Script de Inicialização do Banco de Dados - HullZero

-- Extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela de Embarcações
CREATE TABLE IF NOT EXISTS vessels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    imo_number VARCHAR(20) UNIQUE,
    vessel_type VARCHAR(100),
    hull_area_m2 DECIMAL(10,2),
    paint_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Dados de Navegação (Time Series)
CREATE TABLE IF NOT EXISTS navigation_data (
    time TIMESTAMPTZ NOT NULL,
    vessel_id UUID REFERENCES vessels(id),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    speed_knots DECIMAL(5,2),
    heading DECIMAL(5,2),
    PRIMARY KEY (time, vessel_id)
);

-- Converte para hypertable (TimescaleDB)
SELECT create_hypertable('navigation_data', 'time', if_not_exists => TRUE);

-- Tabela de Dados de Consumo (Time Series)
CREATE TABLE IF NOT EXISTS fuel_consumption (
    time TIMESTAMPTZ NOT NULL,
    vessel_id UUID REFERENCES vessels(id),
    fuel_rate_kg_h DECIMAL(10,2),
    engine_power_kw DECIMAL(10,2),
    rpm INTEGER,
    PRIMARY KEY (time, vessel_id)
);

-- Converte para hypertable
SELECT create_hypertable('fuel_consumption', 'time', if_not_exists => TRUE);

-- Tabela de Dados de Bioincrustação (Time Series)
CREATE TABLE IF NOT EXISTS fouling_data (
    time TIMESTAMPTZ NOT NULL,
    vessel_id UUID REFERENCES vessels(id),
    estimated_thickness_mm DECIMAL(5,2),
    roughness_um DECIMAL(8,2),
    fouling_severity VARCHAR(50),
    confidence_score DECIMAL(3,2),
    PRIMARY KEY (time, vessel_id)
);

-- Converte para hypertable
SELECT create_hypertable('fouling_data', 'time', if_not_exists => TRUE);

-- Tabela de Limpezas e Manutenções
CREATE TABLE IF NOT EXISTS maintenance_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vessel_id UUID REFERENCES vessels(id),
    event_type VARCHAR(50), -- 'cleaning', 'painting', 'inspection'
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    cost_brl DECIMAL(12,2),
    method VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Recomendações
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id VARCHAR(100) UNIQUE,
    vessel_id UUID REFERENCES vessels(id),
    recommendation_type VARCHAR(50),
    priority INTEGER,
    estimated_benefit_brl DECIMAL(12,2),
    estimated_co2_reduction_kg DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending'
);

-- Tabela de Verificações de Conformidade
CREATE TABLE IF NOT EXISTS compliance_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vessel_id UUID REFERENCES vessels(id),
    check_date TIMESTAMP,
    status VARCHAR(50),
    fouling_thickness_mm DECIMAL(5,2),
    roughness_um DECIMAL(8,2),
    compliance_score DECIMAL(3,2),
    violations JSONB,
    warnings JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_navigation_vessel_time ON navigation_data(vessel_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_fuel_vessel_time ON fuel_consumption(vessel_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_fouling_vessel_time ON fouling_data(vessel_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_maintenance_vessel ON maintenance_events(vessel_id, start_date DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_vessel ON recommendations(vessel_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_compliance_vessel ON compliance_checks(vessel_id, check_date DESC);

-- Dados de exemplo (opcional)
INSERT INTO vessels (id, name, imo_number, vessel_type, hull_area_m2, paint_type)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'Petroleiro 001', 'IMO1234567', 'Tanker', 5000.0, 'Antifouling_Type_A'),
    ('550e8400-e29b-41d4-a716-446655440001', 'Rebocador 001', 'IMO1234568', 'Tug', 2000.0, 'Antifouling_Type_B')
ON CONFLICT (imo_number) DO NOTHING;

