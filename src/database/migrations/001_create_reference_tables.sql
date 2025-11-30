-- ============================================================
-- Script de Migração 001: Criar Tabelas de Referência
-- HullZero - Normalização de Banco de Dados
-- ============================================================

-- ============================================================
-- 1. TABELAS DE REFERÊNCIA (Lookup Tables)
-- ============================================================

-- 1.1 Tipos de Embarcação
CREATE TABLE IF NOT EXISTS vessel_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- 'tanker', 'cargo', 'container', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vessel_types_category ON vessel_types(category);

-- 1.2 Classes de Embarcação
CREATE TABLE IF NOT EXISTS vessel_classes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    typical_length_m FLOAT,
    typical_dwt FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 Tipos de Tinta
CREATE TABLE IF NOT EXISTS paint_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    manufacturer VARCHAR(100),
    category VARCHAR(50), -- 'AFS', 'Foul-release', etc.
    typical_lifespan_days INTEGER,
    environmental_rating VARCHAR(20), -- 'low', 'medium', 'high'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.4 Portos
CREATE TABLE IF NOT EXISTS ports (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(3), -- ISO 3166-1 alpha-3
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    port_code VARCHAR(20) UNIQUE, -- Código do porto
    timezone VARCHAR(50),
    water_quality_index FLOAT, -- Índice de qualidade da água
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ports_country ON ports(country);
CREATE INDEX IF NOT EXISTS idx_ports_country_code ON ports(country_code);

-- 1.5 Rotas
CREATE TABLE IF NOT EXISTS routes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    origin_port_id VARCHAR(50) REFERENCES ports(id),
    destination_port_id VARCHAR(50) REFERENCES ports(id),
    typical_duration_days INTEGER,
    distance_nm FLOAT, -- Nautical miles
    region VARCHAR(100), -- 'Brazil_Coast', 'Atlantic', etc.
    water_temperature_avg_c FLOAT,
    salinity_avg_psu FLOAT,
    risk_level VARCHAR(20), -- 'low', 'medium', 'high'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routes_origin ON routes(origin_port_id);
CREATE INDEX IF NOT EXISTS idx_routes_destination ON routes(destination_port_id);
CREATE INDEX IF NOT EXISTS idx_routes_region ON routes(region);

-- 1.6 Contratantes
CREATE TABLE IF NOT EXISTS contractors (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    country VARCHAR(100),
    specialization VARCHAR(100), -- 'cleaning', 'painting', 'inspection', etc.
    certification_level VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'suspended'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contractors_status ON contractors(status);
CREATE INDEX IF NOT EXISTS idx_contractors_specialization ON contractors(specialization);

-- 1.7 Tipos de Carga
CREATE TABLE IF NOT EXISTS cargo_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50), -- 'liquid', 'solid', 'gas', 'container'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.8 Tipos de Combustível
CREATE TABLE IF NOT EXISTS fuel_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50), -- 'fossil', 'biofuel', 'lng', 'electric'
    co2_emission_factor_kg_per_kg FLOAT,
    energy_density_mj_per_kg FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.9 Espécies Invasoras
CREATE TABLE IF NOT EXISTS invasive_species (
    id VARCHAR(50) PRIMARY KEY,
    scientific_name VARCHAR(255) NOT NULL UNIQUE,
    common_name VARCHAR(255),
    code VARCHAR(50) UNIQUE, -- 'CORAL_SOL', 'MEXILHAO_DOURADO', etc.
    category VARCHAR(50), -- 'coral', 'mollusk', 'barnacle', etc.
    description TEXT,
    native_region VARCHAR(255),
    invasive_regions JSON, -- Lista de regiões onde é invasora
    growth_rate_multiplier FLOAT DEFAULT 1.0,
    removal_difficulty FLOAT, -- 0-1, 1 = muito difícil
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invasive_species_code ON invasive_species(code);
CREATE INDEX IF NOT EXISTS idx_invasive_species_category ON invasive_species(category);

-- ============================================================
-- 2. TABELAS DE RELACIONAMENTO N:N
-- ============================================================

-- 2.1 Rotas de Embarcações
CREATE TABLE IF NOT EXISTS vessel_routes (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    route_id VARCHAR(50) NOT NULL REFERENCES routes(id),
    is_primary BOOLEAN DEFAULT FALSE,
    frequency_per_year INTEGER, -- Quantas vezes por ano navega nesta rota
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vessel_id, route_id)
);

CREATE INDEX IF NOT EXISTS idx_vessel_routes_vessel ON vessel_routes(vessel_id);
CREATE INDEX IF NOT EXISTS idx_vessel_routes_route ON vessel_routes(route_id);

-- 2.2 Tipos de Carga de Embarcações
CREATE TABLE IF NOT EXISTS vessel_cargo_types (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    cargo_type_id VARCHAR(50) NOT NULL REFERENCES cargo_types(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vessel_id, cargo_type_id)
);

CREATE INDEX IF NOT EXISTS idx_vessel_cargo_vessel ON vessel_cargo_types(vessel_id);

-- 2.3 Combustíveis Alternativos de Embarcações
CREATE TABLE IF NOT EXISTS vessel_fuel_alternatives (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    fuel_type_id VARCHAR(50) NOT NULL REFERENCES fuel_types(id),
    compatibility_level VARCHAR(20), -- 'full', 'partial', 'experimental'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vessel_id, fuel_type_id)
);

CREATE INDEX IF NOT EXISTS idx_vessel_fuel_vessel ON vessel_fuel_alternatives(vessel_id);

-- ============================================================
-- 3. INSERIR DADOS INICIAIS DE REFERÊNCIA
-- ============================================================

-- Tipos de Embarcação
INSERT INTO vessel_types (id, name, category) VALUES
    ('tanker', 'Tanker', 'tanker'),
    ('gas_carrier', 'Gas Carrier', 'tanker'),
    ('cargo', 'Cargo Ship', 'cargo'),
    ('container', 'Container Ship', 'container'),
    ('barge', 'Barge', 'barge'),
    ('tug', 'Tugboat', 'tug')
ON CONFLICT (id) DO NOTHING;

-- Classes de Embarcação
INSERT INTO vessel_classes (id, name, typical_length_m, typical_dwt) VALUES
    ('suezmax', 'Suezmax', 275, 160000),
    ('aframax', 'Aframax', 250, 120000),
    ('panamax', 'Panamax', 225, 80000),
    ('handysize', 'Handysize', 180, 50000),
    ('vlcc', 'VLCC', 330, 300000)
ON CONFLICT (id) DO NOTHING;

-- Tipos de Tinta
INSERT INTO paint_types (id, name, category, typical_lifespan_days, environmental_rating) VALUES
    ('afs_standard', 'AFS Standard', 'AFS', 1095, 'medium'),
    ('afs_plus', 'AFS Plus', 'AFS', 1460, 'low'),
    ('foul_release', 'Foul Release', 'Foul-release', 1825, 'low'),
    ('hybrid', 'Hybrid AFS', 'Hybrid', 1275, 'medium')
ON CONFLICT (id) DO NOTHING;

-- Tipos de Combustível
INSERT INTO fuel_types (id, name, category, co2_emission_factor_kg_per_kg, energy_density_mj_per_kg) VALUES
    ('mgo', 'Marine Gas Oil', 'fossil', 3.206, 42.7),
    ('hfo', 'Heavy Fuel Oil', 'fossil', 3.114, 40.2),
    ('lng', 'Liquefied Natural Gas', 'lng', 2.750, 50.0),
    ('biofuel', 'Biofuel', 'biofuel', 2.500, 37.0)
ON CONFLICT (id) DO NOTHING;

-- Espécies Invasoras
INSERT INTO invasive_species (id, scientific_name, common_name, code, category, removal_difficulty) VALUES
    ('coral_sol', 'Tubastraea coccinea', 'Coral Sol', 'CORAL_SOL', 'coral', 0.8),
    ('mexilhao_dourado', 'Limnoperna fortunei', 'Mexilhão Dourado', 'MEXILHAO_DOURADO', 'mollusk', 0.7),
    ('mexilhao_verde', 'Perna viridis', 'Mexilhão Verde', 'MEXILHAO_VERDE', 'mollusk', 0.6),
    ('barnacles', 'Amphibalanus amphitrite', 'Barnacles', 'BARNAQUES', 'barnacle', 0.5)
ON CONFLICT (id) DO NOTHING;

