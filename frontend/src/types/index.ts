export type DataProvenance = 'raw_fortyguard' | 'derived' | 'simulated' | 'demo_synthetic';

export type AssessmentMode = 'LIVE' | 'DEMO';

export type AssessmentStatus = 'Pending' | 'Processing' | 'Completed' | 'Failed';

export type WorkloadCategory = 'Light' | 'Moderate' | 'Heavy';

export interface Site {
  id: string;
  name: string;
  description: string | null;
  latitude: number;
  longitude: number;
  boundary_geojson: any | null;
  created_at: string;
  updated_at: string;
}

export interface NormalizedEnvironmental {
  provenance: DataProvenance;
  temperature: number | null;
  heat_index: number | null;
  apparent_temperature: number | null;
  wet_bulb_temperature: number | null;
  relative_humidity: number | null;
  solar_irradiance: number | null;
  precipitation_mm: number | null;
  cloud_cover_octas: number | null;
  air_quality_index: number | null;
}

export interface NormalizedHeatmapStats {
  provenance: DataProvenance;
  min_temperature: number | null;
  max_temperature: number | null;
  mean_temperature: number | null;
  median_temperature: number | null;
  standard_deviation: number | null;
  granularity: number | null;
}

export interface AssessmentResponse {
  id: string;
  site_id: string;
  mode: AssessmentMode;
  status: AssessmentStatus;
  heatmap_activity_id: string | null;
  env_activity_id: string | null;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  raw_heatmap_payload: any | null;
  raw_env_payload: any | null;
  map_geojson: any | null;
  stats: NormalizedHeatmapStats | null;
  environmental: NormalizedEnvironmental | null;
}

// ----------------- Phase 3 Intelligence Types -----------------

export interface WhereDimension {
  site_name: string;
  coordinates: [number, number];
  grid_cell_id: string;
  zone_label: string;
  micro_surface_temperature: number | null;
  thermal_exceedance_delta: number | null;
}

export interface EnvironmentalFactorContribution {
  factor: string;
  raw_value: string | null;
  contribution_level: 'Low' | 'Moderate' | 'High' | 'Critical';
  explanation: string;
}

export interface WhyDimension {
  surface_thermal_impact: string;
  factor_contributions: EnvironmentalFactorContribution[];
  primary_risk_driver: string;
}

export interface WhatDimension {
  risk_category: string;
  heat_strain_score: number | null;
  estimated_wbgt: number | null;
  work_rest_guidance: string;
  hydration_guidance: string;
  critical_ppe_actions: string[];
  warnings: string[];
}

export interface ExplainabilityReport {
  provenance_summary: Record<string, string>;
  where: WhereDimension;
  why: WhyDimension;
  what: WhatDimension;
  disclaimer: string;
}

export interface SimulationMetricComparison {
  baseline: number;
  simulated: number;
  delta: number;
  unit: string;
}

export interface HSEOperationalProtocol {
  provenance: DataProvenance;
  workload: WorkloadCategory;
  estimated_wbgt: number | null;
  risk_category: string;
  work_rest_ratio: string;
  work_minutes_per_hour: number;
  rest_minutes_per_hour: number;
  mandatory_hydration_ml_per_hour: number;
  recommended_ppe_modifications: string[];
  critical_warnings: string[];
  disclaimer: string;
}

export interface WhatIfSimulationResult {
  provenance: DataProvenance;
  simulation_label: string;
  parameters_applied: {
    shade_percent: number;
    misting_percent: number;
    workload: string;
  };
  effective_solar_irradiance: SimulationMetricComparison;
  effective_temperature: SimulationMetricComparison;
  estimated_wbgt: SimulationMetricComparison;
  heat_strain_index: SimulationMetricComparison;
  baseline_protocol: HSEOperationalProtocol;
  simulated_protocol: HSEOperationalProtocol;
  recovered_work_minutes_per_hour: number;
  modeled_assumptions: string[];
  disclaimer: string;
}
