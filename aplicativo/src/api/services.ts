import apiClient from './client';

// ========== INTERFACES ==========

export interface DashboardKPIs {
    accumulated_economy_brl: number;
    co2_reduction_tonnes: number;
    compliance_rate_percent: number;
    monitored_vessels: number;
    period: string;
    last_update: string;
}

export interface VesselStatus {
    id: string;
    name: string;
    status: string;
    fouling_mm: number;
    roughness_um: number;
    compliance_status: string;
    last_update: string;
}

export interface FleetStatus {
    vessels: VesselStatus[];
}

export interface MaintenanceEvent {
    id: string;
    vessel_id: string;
    event_type: string;
    start_date: string;
    end_date?: string;
    cost_brl?: number;
    status?: string;
    vessel_name?: string; // Helper for list view
}

export interface InvasiveSpeciesRisk {
    species: string;
    risk_level: string;
    risk_score: number;
    regions_affected: string[];
    recommendations: string[];
}

export interface ComplianceCheck {
    is_compliant: boolean;
    compliance_rate: number;
    status: string;
    thickness_mm: number;
    roughness_um: number;
    violations: string[];
    recommendations: string[];
    vessel_name?: string;
}

// ========== SERVICES ==========

export const dashboardService = {
    async getKPIs(period: string = '6_months') {
        const response = await apiClient.get(`/api/dashboard/kpis?period=${period}`);
        return response.data as DashboardKPIs;
    },

    async getFleetStatus() {
        const response = await apiClient.get('/api/dashboard/fleet-status');
        return response.data as FleetStatus;
    },
};

export const vesselService = {
    async getById(id: string) {
        const response = await apiClient.get(`/api/vessels/${id}`);
        return response.data;
    },

    async getAll() {
        const response = await apiClient.get('/api/vessels');
        return response.data;
    }
};

export const maintenanceService = {
    async getHistory(vesselId?: string) {
        const url = vesselId
            ? `/api/vessels/${vesselId}/maintenance`
            : '/api/maintenance/history'; // Assuming a general endpoint or we filter client-side if needed
        // For now, let's fetch for a specific vessel or we might need a new endpoint for "all maintenance"
        // If the backend doesn't support "all", we might need to iterate or just show per vessel.
        // Let's assume we use the fleet status to get IDs and then fetch, or just show a placeholder.
        // Actually, let's use the vessel endpoint.
        if (vesselId) {
            const response = await apiClient.get(url);
            return response.data as MaintenanceEvent[];
        }
        return [];
    }
};

export const invasiveSpeciesService = {
    async list() {
        const response = await apiClient.get('/api/invasive-species/list');
        return response.data;
    },

    async assessRisk(vesselId: string, data: any) {
        const response = await apiClient.post(`/api/vessels/${vesselId}/invasive-species/assess`, data);
        return response.data;
    }
};

export const complianceService = {
    async getComplianceSummary() {
        const response = await apiClient.get('/api/compliance/status/summary');
        return response.data;
    },

    async checkCompliance(vesselId: string, thickness: number, roughness: number) {
        const response = await apiClient.post(`/api/vessels/${vesselId}/compliance/check`, {
            vessel_id: vesselId,
            fouling_thickness_mm: thickness,
            roughness_um: roughness
        });
        return response.data as ComplianceCheck;
    }
};
