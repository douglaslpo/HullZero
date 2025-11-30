-- ============================================================
-- Script de Migração 002: Criar Novas Entidades Normalizadas
-- HullZero - Normalização de Banco de Dados
-- ============================================================

-- ============================================================
-- 1. APLICAÇÕES DE TINTA
-- ============================================================

CREATE TABLE IF NOT EXISTS paint_applications (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    paint_type_id VARCHAR(50) NOT NULL REFERENCES paint_types(id),
    application_date DATE NOT NULL,
    application_port_id VARCHAR(50) REFERENCES ports(id),
    contractor_id VARCHAR(50) REFERENCES contractors(id),
    area_m2 FLOAT CHECK (area_m2 > 0),
    cost_brl FLOAT CHECK (cost_brl >= 0),
    warranty_days INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_paint_applications_vessel ON paint_applications(vessel_id);
CREATE INDEX IF NOT EXISTS idx_paint_applications_date ON paint_applications(application_date);

-- ============================================================
-- 2. CALIBRAÇÕES DE SENSORES
-- ============================================================

CREATE TABLE IF NOT EXISTS sensor_calibrations (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL, -- 'fouling', 'roughness', 'temperature', etc.
    calibration_date DATE NOT NULL,
    calibration_port_id VARCHAR(50) REFERENCES ports(id),
    contractor_id VARCHAR(50) REFERENCES contractors(id),
    calibration_value_before FLOAT,
    calibration_value_after FLOAT,
    next_calibration_due DATE,
    certificate_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensor_calibrations_vessel ON sensor_calibrations(vessel_id);
CREATE INDEX IF NOT EXISTS idx_sensor_calibrations_date ON sensor_calibrations(calibration_date);
CREATE INDEX IF NOT EXISTS idx_sensor_calibrations_due ON sensor_calibrations(next_calibration_due);

-- ============================================================
-- 3. INSPEÇÕES
-- ============================================================

CREATE TABLE IF NOT EXISTS inspections (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    maintenance_event_id VARCHAR(50) REFERENCES maintenance_events(id), -- Se vinculada a um evento
    
    -- Tipo de inspeção
    inspection_type VARCHAR(50) NOT NULL CHECK (inspection_type IN ('routine', 'compliance', 'pre_maintenance', 'post_maintenance', 'emergency')),
    
    -- Datas
    inspection_date DATE NOT NULL,
    next_inspection_due DATE,
    
    -- Localização
    inspection_port_id VARCHAR(50) REFERENCES ports(id),
    inspector_name VARCHAR(255),
    inspector_company VARCHAR(255),
    contractor_id VARCHAR(50) REFERENCES contractors(id),
    
    -- Resultados
    fouling_thickness_mm FLOAT CHECK (fouling_thickness_mm >= 0),
    roughness_um FLOAT CHECK (roughness_um >= 0),
    compliance_status VARCHAR(20) CHECK (compliance_status IN ('compliant', 'at_risk', 'non_compliant', 'critical')),
    compliance_score FLOAT CHECK (compliance_score >= 0 AND compliance_score <= 1),
    
    -- Documentação
    report_path VARCHAR(500), -- Caminho para relatório PDF
    photos_paths JSON, -- Array de caminhos para fotos
    certificate_number VARCHAR(100),
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inspections_vessel_date ON inspections(vessel_id, inspection_date DESC);
CREATE INDEX IF NOT EXISTS idx_inspections_type ON inspections(inspection_type);
CREATE INDEX IF NOT EXISTS idx_inspections_compliance ON inspections(compliance_status);
CREATE INDEX IF NOT EXISTS idx_inspections_due ON inspections(next_inspection_due);

-- ============================================================
-- 4. VERIFICAÇÕES DE CONFORMIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS compliance_checks (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    inspection_id VARCHAR(50) REFERENCES inspections(id),
    
    -- Data da verificação
    check_date TIMESTAMP NOT NULL,
    
    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('compliant', 'at_risk', 'non_compliant', 'critical')),
    
    -- Valores medidos
    fouling_thickness_mm FLOAT NOT NULL CHECK (fouling_thickness_mm >= 0),
    roughness_um FLOAT NOT NULL CHECK (roughness_um >= 0),
    
    -- Limites aplicados
    max_allowed_thickness_mm FLOAT NOT NULL CHECK (max_allowed_thickness_mm > 0),
    max_allowed_roughness_um FLOAT NOT NULL CHECK (max_allowed_roughness_um > 0),
    
    -- Score
    compliance_score FLOAT NOT NULL CHECK (compliance_score >= 0 AND compliance_score <= 1),
    
    -- Próxima inspeção
    next_inspection_due DATE,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compliance_vessel_date ON compliance_checks(vessel_id, check_date DESC);
CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_checks(status);
CREATE INDEX IF NOT EXISTS idx_compliance_due ON compliance_checks(next_inspection_due);

-- ============================================================
-- 5. VIOLAÇÕES DE CONFORMIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS compliance_violations (
    id VARCHAR(50) PRIMARY KEY,
    compliance_check_id VARCHAR(50) NOT NULL REFERENCES compliance_checks(id) ON DELETE CASCADE,
    violation_type VARCHAR(50) NOT NULL, -- 'thickness_exceeded', 'roughness_exceeded', 'inspection_overdue', etc.
    violation_description TEXT NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compliance_violations_check ON compliance_violations(compliance_check_id);

-- ============================================================
-- 6. AVISOS DE CONFORMIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS compliance_warnings (
    id VARCHAR(50) PRIMARY KEY,
    compliance_check_id VARCHAR(50) NOT NULL REFERENCES compliance_checks(id) ON DELETE CASCADE,
    warning_type VARCHAR(50) NOT NULL,
    warning_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compliance_warnings_check ON compliance_warnings(compliance_check_id);

-- ============================================================
-- 7. RECOMENDAÇÕES DE CONFORMIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS compliance_recommendations (
    id VARCHAR(50) PRIMARY KEY,
    compliance_check_id VARCHAR(50) NOT NULL REFERENCES compliance_checks(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compliance_recommendations_check ON compliance_recommendations(compliance_check_id);

-- ============================================================
-- 8. FATORES DE RISCO NORMAM 401
-- ============================================================

CREATE TABLE IF NOT EXISTS risk_factors (
    id VARCHAR(50) PRIMARY KEY,
    risk_id VARCHAR(50) NOT NULL REFERENCES normam401_risks(id) ON DELETE CASCADE,
    factor_type VARCHAR(50) NOT NULL, -- 'high_temperature', 'long_port_stay', 'old_paint', etc.
    factor_description TEXT NOT NULL,
    contribution_score FLOAT CHECK (contribution_score >= 0 AND contribution_score <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_factors_risk ON risk_factors(risk_id);

-- ============================================================
-- 9. RECOMENDAÇÕES DE RISCO NORMAM 401
-- ============================================================

CREATE TABLE IF NOT EXISTS risk_recommendations (
    id VARCHAR(50) PRIMARY KEY,
    risk_id VARCHAR(50) NOT NULL REFERENCES normam401_risks(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_recommendations_risk ON risk_recommendations(risk_id);

-- ============================================================
-- 10. RISCOS DE ESPÉCIES INVASORAS
-- ============================================================

CREATE TABLE IF NOT EXISTS invasive_species_risks (
    id VARCHAR(50) PRIMARY KEY,
    vessel_id VARCHAR(50) NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    species_id VARCHAR(50) NOT NULL REFERENCES invasive_species(id),
    
    -- Risco
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_score FLOAT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
    
    -- Fatores
    growth_rate_multiplier FLOAT CHECK (growth_rate_multiplier > 0),
    removal_difficulty FLOAT CHECK (removal_difficulty >= 0 AND removal_difficulty <= 1),
    
    -- Regiões afetadas (JSON mantido para flexibilidade)
    regions_affected JSONB,
    
    -- Fatores sazonais (JSON mantido para flexibilidade temporal)
    seasonal_factors JSONB,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(vessel_id, species_id, created_at)
);

CREATE INDEX IF NOT EXISTS idx_invasive_risks_vessel ON invasive_species_risks(vessel_id);
CREATE INDEX IF NOT EXISTS idx_invasive_risks_species ON invasive_species_risks(species_id);
CREATE INDEX IF NOT EXISTS idx_invasive_risks_level ON invasive_species_risks(risk_level);

-- ============================================================
-- 11. RECOMENDAÇÕES DE ESPÉCIES INVASORAS
-- ============================================================

CREATE TABLE IF NOT EXISTS invasive_species_recommendations (
    id VARCHAR(50) PRIMARY KEY,
    risk_id VARCHAR(50) NOT NULL REFERENCES invasive_species_risks(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    recommendation_type VARCHAR(50), -- 'biological_control', 'mechanical_removal', 'prevention', etc.
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invasive_recommendations_risk ON invasive_species_recommendations(risk_id);

