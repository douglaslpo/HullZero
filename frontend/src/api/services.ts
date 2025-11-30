/**
 * Serviços de API - HullZero
 * 
 * Centraliza todas as chamadas de API do frontend
 */

import apiClient from './client'

// ========== EMBARCAÇÕES ==========

export interface Vessel {
  id: string
  name: string
  imo_number?: string
  call_sign?: string
  vessel_type?: string
  vessel_class?: string
  fleet_category?: string
  length_m?: number
  width_m?: number
  draft_m?: number
  hull_area_m2?: number
  displacement_tonnes?: number
  dwt?: number
  status: string
  construction_year?: number
  construction_country?: string
  home_port?: string
  operating_routes?: string[]
}

export const vesselService = {
  // Listar todas (com fallback para banco de dados)
  async getAll(useDb: boolean = true) {
    const endpoint = useDb ? '/api/db/vessels' : '/api/vessels'
    const response = await apiClient.get(endpoint)
    return response.data
  },

  // Obter por ID
  async getById(id: string, useDb: boolean = true) {
    try {
      if (useDb) {
        const response = await apiClient.get(`/api/db/vessels/${id}`)
        return response.data
      } else {
        const response = await apiClient.get(`/api/vessels/${id}`)
        return response.data
      }
    } catch (error) {
      // Fallback para endpoint alternativo
      try {
        const response = await apiClient.get(`/api/vessels/${id}`)
        return response.data
      } catch (fallbackError) {
        // Se ambos falharem, lançar o erro original
        throw error
      }
    }
  },

  // Obter por IMO
  async getByIMO(imo: string) {
    const response = await apiClient.get(`/api/db/vessels/imo/${imo}`)
    return response.data
  },

  // Criar
  async create(vessel: Partial<Vessel>) {
    const response = await apiClient.post('/api/vessels', vessel)
    return response.data
  },

  // Atualizar
  async update(id: string, updates: Partial<Vessel>) {
    const response = await apiClient.put(`/api/vessels/${id}`, updates)
    return response.data
  },

  // Deletar
  async delete(id: string) {
    const response = await apiClient.delete(`/api/vessels/${id}`)
    return response.data
  },

  // Estatísticas da frota
  async getStatistics(useDb: boolean = true) {
    if (useDb) {
      const response = await apiClient.get('/api/db/statistics/fleet')
      return response.data
    }
    const response = await apiClient.get('/api/transpetro/fleet/statistics')
    return response.data
  }
}

// ========== BIOINCRUSTAÇÃO ==========

export interface FoulingData {
  id: string
  vessel_id: string
  timestamp: string
  estimated_thickness_mm: number
  estimated_roughness_um: number
  fouling_severity: string
  confidence_score: number
  predicted_fuel_impact_percent?: number
  predicted_co2_impact_kg?: number
}

export interface AdvancedFoulingPrediction {
  timestamp: string
  estimated_thickness_mm: number
  estimated_roughness_um: number
  fouling_severity: string
  confidence_score: number
  predicted_fuel_impact_percent: number
  predicted_co2_impact_kg: number
  invasive_species_risk: Record<string, number>
  natural_control_recommendations: string[]
  model_ensemble_contributions: Record<string, number>
  feature_importance: Record<string, number>
}

export const foulingService = {
  // Criar predição (salvar no banco)
  async create(vesselId: string, data: Partial<FoulingData>) {
    const response = await apiClient.post(`/api/db/vessels/${vesselId}/fouling`, data)
    return response.data
  },

  // Obter histórico
  async getHistory(vesselId: string, days: number = 30) {
    try {
      const response = await apiClient.get(`/api/db/vessels/${vesselId}/fouling?days=${days}`)
      return response.data
    } catch {
      // Fallback para endpoint alternativo
      const response = await apiClient.get(`/api/vessels/${vesselId}/fouling?days=${days}`)
      return response.data
    }
  },

  // Obter última predição
  async getLatest(vesselId: string) {
    try {
      const response = await apiClient.get(`/api/db/vessels/${vesselId}/fouling/latest`)
      return response.data
    } catch {
      // Fallback para endpoint alternativo
      const response = await apiClient.get(`/api/vessels/${vesselId}/fouling/latest`)
      return response.data
    }
  },

  // Predição avançada (usa dados reais do banco)
  async predictAdvanced(vesselId: string, useAdvanced: boolean = true) {
    try {
      // Usar endpoint do banco que carrega dados reais automaticamente
      const response = await apiClient.post(
        `/api/db/vessels/${vesselId}/fouling/predict?use_advanced=${useAdvanced}`
      )
      return response.data as AdvancedFoulingPrediction
    } catch {
      // Fallback para endpoint antigo se necessário
      const response = await apiClient.post(
        `/api/vessels/${vesselId}/fouling/predict/advanced`,
        { vessel_id: vesselId }
      )
      return response.data as AdvancedFoulingPrediction
    }
  },

  // Predição simples (usa dados reais do banco)
  async predict(vesselId: string) {
    try {
      // Usar endpoint do banco que carrega dados reais automaticamente
      const response = await apiClient.post(
        `/api/db/vessels/${vesselId}/fouling/predict?use_advanced=false`
      )
      return response.data
    } catch {
      // Fallback para endpoint antigo se necessário
      const response = await apiClient.post(
        `/api/vessels/${vesselId}/fouling/predict`,
        { vessel_id: vesselId }
      )
      return response.data
    }
  }
}

// ========== DADOS OPERACIONAIS ==========

export interface OperationalData {
  id: string
  vessel_id: string
  timestamp: string
  latitude: number
  longitude: number
  speed_knots: number
  engine_power_kw: number
  fuel_consumption_kg_h: number
  water_temperature_c: number
  wind_speed_knots: number
  wave_height_m: number
  salinity_psu?: number
}

export const operationalDataService = {
  // Criar
  async create(vesselId: string, data: Partial<OperationalData>) {
    const response = await apiClient.post(`/api/vessels/${vesselId}/operational-data`, data)
    return response.data
  },

  // Obter histórico
  async getHistory(vesselId: string, startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const response = await apiClient.get(
      `/api/vessels/${vesselId}/operational-data?${params.toString()}`
    )
    return response.data
  },

  // Obter últimos dados
  async getLatest(vesselId: string) {
    try {
      const response = await apiClient.get(`/api/db/vessels/${vesselId}/operational-data/latest`)
      return response.data
    } catch {
      const response = await apiClient.get(`/api/vessels/${vesselId}/operational-data/latest`)
      return response.data
    }
  }
}

// ========== MANUTENÇÃO ==========

export interface MaintenanceEvent {
  id: string
  vessel_id: string
  event_type: string
  start_date: string
  end_date?: string
  duration_hours?: number
  cleaning_method?: string
  fouling_before_mm?: number
  fouling_after_mm?: number
  roughness_before_um?: number
  roughness_after_um?: number
  cost_brl?: number
  downtime_cost_brl?: number
  total_cost_brl?: number
  port_name?: string
  port_country?: string
  inspector_name?: string
  notes?: string
  status?: string
  photos_paths?: string[]
}

export const maintenanceService = {
  // Upload de imagem
  async uploadImage(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Criar
  async create(vesselId: string, data: Partial<MaintenanceEvent>) {
    const response = await apiClient.post(`/api/vessels/${vesselId}/maintenance`, data)
    return response.data
  },

  // Obter histórico
  async getHistory(vesselId: string, eventType?: string) {
    const params = eventType ? `?event_type=${eventType}` : ''
    const response = await apiClient.get(`/api/vessels/${vesselId}/maintenance${params}`)
    return response.data
  },

  // Obter último evento
  async getLatest(vesselId: string) {
    try {
      const response = await apiClient.get(`/api/db/vessels/${vesselId}/maintenance/latest`)
      return response.data
    } catch {
      const response = await apiClient.get(`/api/vessels/${vesselId}/maintenance/latest`)
      return response.data
    }
  }
}

// ========== ESPÉCIES INVASORAS ==========

export interface InvasiveSpeciesRisk {
  species: string
  risk_level: string
  risk_score: number
  growth_rate_multiplier: number
  removal_difficulty: number
  regions_affected: string[]
  seasonal_factors: Record<string, number>
  recommendations: string[]
}

export const invasiveSpeciesService = {
  // Avaliar risco
  async assessRisk(vesselId: string, data: {
    route_region: string
    water_temperature_c: number
    salinity_psu: number
    depth_m?: number
    seasonal_factor?: string
  }) {
    const response = await apiClient.post(
      `/api/vessels/${vesselId}/invasive-species/assess`,
      data
    )
    return response.data as InvasiveSpeciesRisk[]
  },

  // Obter informações
  async getInfo(species: string) {
    const response = await apiClient.get(`/api/invasive-species/info/${species}`)
    return response.data
  },

  // Listar espécies
  async list() {
    const response = await apiClient.get('/api/invasive-species/list')
    return response.data
  }
}

// ========== DASHBOARD ==========

export interface DashboardKPIs {
  accumulated_economy_brl: number
  co2_reduction_tonnes: number
  compliance_rate_percent: number
  monitored_vessels: number
  period: string
  last_update: string
}

export interface TrendDataPoint {
  month: string
  economy_brl: number
  co2_tonnes: number
  compliance_rate_percent: number
  avg_fouling_mm: number
  avg_roughness_um: number
  monitored_vessels: number
  maintenance_events: number
}

export interface Trends {
  period: string
  data: TrendDataPoint[]
}

export interface VesselStatus {
  id: string
  name: string
  status: string
  fouling_mm: number
  roughness_um: number
  compliance_status: string
  last_update: string
}

export interface FleetStatus {
  vessels: VesselStatus[]
}

export const dashboardService = {
  // KPIs
  async getKPIs(period: string = '6_months') {
    const response = await apiClient.get(`/api/dashboard/kpis?period=${period}`)
    return response.data as DashboardKPIs
  },

  // Tendências
  async getTrends(period: string = '6_months') {
    const response = await apiClient.get(`/api/dashboard/trends?period=${period}`)
    return response.data as Trends
  },

  // Status da frota
  async getFleetStatus() {
    const response = await apiClient.get('/api/dashboard/fleet-status')
    return response.data as FleetStatus
  }
}

// ========== CONFORMIDADE NORMAM 401 ==========

export interface ComplianceCheck {
  is_compliant: boolean
  compliance_rate: number
  compliance_score?: number // Alias for compliance_rate
  status?: 'compliant' | 'warning' | 'critical' | string
  thickness_mm: number
  fouling_thickness_mm?: number // Alias for thickness_mm
  roughness_um: number
  max_allowed_thickness_mm?: number
  max_allowed_roughness_um?: number
  violations: string[]
  warnings?: string[]
  recommendations: string[]
  next_inspection_due?: string
}

export interface NORMAM401Risk {
  risk_score: number
  risk_level: string
  predicted_fouling_mm: number
  predicted_roughness_um: number
  days_ahead: number
  risk_factors: string[]
  recommendations: string[]
}

export const complianceService = {
  // Verificar conformidade
  async checkCompliance(vesselId: string, thickness: number, roughness: number, vesselType: string = 'standard') {
    const response = await apiClient.post(
      `/api/vessels/${vesselId}/compliance/check`,
      {
        vessel_id: vesselId,
        fouling_thickness_mm: thickness,
        roughness_um: roughness,
        vessel_type: vesselType
      }
    )
    return response.data as ComplianceCheck
  },

  // Predizer risco
  async predictRisk(vesselId: string, data: any) {
    const response = await apiClient.post(
      `/api/vessels/${vesselId}/normam401/risk-predict`,
      data
    )
    return response.data as NORMAM401Risk
  },

  // Obter ações corretivas
  async getCorrectiveActions(vesselId: string, thickness: number, roughness: number) {
    const response = await apiClient.get(
      `/api/vessels/${vesselId}/normam401/corrective-actions?fouling_thickness_mm=${thickness}&roughness_um=${roughness}`
    )
    return response.data
  },

  // ========== NOVOS ENDPOINTS NORMALIZADOS ==========

  // Obter histórico de verificações de conformidade
  async getComplianceChecks(vesselId: string, startDate?: string, endDate?: string, limit: number = 100) {
    try {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      params.append('limit', limit.toString())

      const response = await apiClient.get(
        `/api/compliance/vessels/${vesselId}/checks?${params.toString()}`
      )
      return response.data
    } catch {
      // Fallback: retornar array vazio se endpoint não estiver disponível
      return []
    }
  },

  // Obter última verificação de conformidade
  async getLatestComplianceCheck(vesselId: string) {
    try {
      const response = await apiClient.get(
        `/api/compliance/vessels/${vesselId}/checks/latest`
      )
      return response.data
    } catch {
      // Fallback: usar endpoint antigo
      return null
    }
  },

  // Obter histórico de inspeções
  async getInspections(vesselId: string, inspectionType?: string, startDate?: string, endDate?: string, limit: number = 100) {
    try {
      const params = new URLSearchParams()
      if (inspectionType) params.append('inspection_type', inspectionType)
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      params.append('limit', limit.toString())

      const response = await apiClient.get(
        `/api/compliance/vessels/${vesselId}/inspections?${params.toString()}`
      )
      return response.data
    } catch {
      return []
    }
  },

  // Obter resumo de conformidade da frota
  async getComplianceSummary(status?: string) {
    try {
      const params = new URLSearchParams()
      if (status) params.append('status', status)

      const response = await apiClient.get(
        `/api/compliance/status/summary?${params.toString()}`
      )
      return response.data
    } catch {
      return null
    }
  }
}

// ========== FROTA TRANSPETRO ==========

export const transpetroService = {
  // Obter frota completa
  async getFleet() {
    const response = await apiClient.get('/api/transpetro/fleet')
    return response.data
  },

  // Obter embarcação
  async getVessel(vesselId: string) {
    const response = await apiClient.get(`/api/transpetro/fleet/${vesselId}`)
    return response.data
  },

  // Obter dados de bioincrustação
  async getFoulingData(vesselId: string, daysSinceCleaning?: number) {
    const params = daysSinceCleaning ? `?days_since_cleaning=${daysSinceCleaning}` : ''
    const response = await apiClient.get(`/api/transpetro/fleet/${vesselId}/fouling-data${params}`)
    return response.data
  },

  // Inicializar frota
  async initialize() {
    const response = await apiClient.post('/api/transpetro/fleet/initialize')
    return response.data
  },

  // Estatísticas
  async getStatistics() {
    const response = await apiClient.get('/api/transpetro/fleet/statistics')
    return response.data
  },

  // Por categoria
  async getByCategory(category: string) {
    const response = await apiClient.get(`/api/transpetro/fleet/category/${category}`)
    return response.data
  },

  // Por classe
  async getByClass(vesselClass: string) {
    const response = await apiClient.get(`/api/transpetro/fleet/class/${vesselClass}`)
    return response.data
  }
}

// ========== GESTÃO DE FROTA (DASHBOARD) ==========

export interface FleetSummary {
  monitored_vessels: number
  average_additional_consumption_percent: number
  fr_distribution: {
    'FR 0': number
    'FR 1': number
    'FR 2': number
    'FR 3+4': number
  }
  last_update: string
}

export interface VesselDetailedStatus {
  id: string
  name: string
  vessel_id: string
  vessel_class?: string
  fr_level: number
  fr_label: string
  performance_loss_percent: number
  fouling_mm: number
  roughness_um: number
  last_cleaning_date?: string
  last_painting_date?: string
  sensor_calibration_date?: string
  risk_15_days: number
  risk_30_days: number
  alert_message?: string
  alert_type?: 'critical' | 'warning' | 'info'
}

export interface FleetDetailedStatus {
  vessels: VesselDetailedStatus[]
  last_update: string
}

export const fleetManagementService = {
  // Sumário da frota
  async getSummary() {
    const response = await apiClient.get('/api/fleet/summary')
    return response.data as FleetSummary
  },

  // Status detalhado
  async getDetailedStatus() {
    const response = await apiClient.get('/api/fleet/detailed-status')
    return response.data as FleetDetailedStatus
  }
}

