from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.assessment import DataProvenance
from app.services.hse.protocol import WorkloadCategory, HSEProtocolEngine, HSEOperationalProtocol
from app.services.risk.calculator import RiskCalculator, DerivedRiskMetrics


class SimulationRequest(BaseModel):
    temperature: float = Field(..., description="Baseline ambient temperature in °C")
    wet_bulb_temperature: float = Field(..., description="Baseline wet bulb temperature in °C")
    solar_irradiance: Optional[float] = Field(850.0, description="Baseline solar GHI in W/m²")
    shade_percent: float = Field(0.0, ge=0.0, le=100.0, description="Shading canopy coverage (0 - 100%)")
    misting_percent: float = Field(0.0, ge=0.0, le=100.0, description="Active evaporative misting intensity (0 - 100%)")
    workload: WorkloadCategory = WorkloadCategory.MODERATE


class SimulationMetricComparison(BaseModel):
    baseline: float
    simulated: float
    delta: float
    unit: str


class WhatIfSimulationResult(BaseModel):
    provenance: DataProvenance = DataProvenance.SIMULATED
    simulation_label: str = "ESTIMATED MITIGATION IMPACT"
    parameters_applied: Dict[str, Any]
    
    # Comparisons
    effective_solar_irradiance: SimulationMetricComparison
    effective_temperature: SimulationMetricComparison
    estimated_wbgt: SimulationMetricComparison
    heat_strain_index: SimulationMetricComparison
    
    baseline_protocol: HSEOperationalProtocol
    simulated_protocol: HSEOperationalProtocol
    recovered_work_minutes_per_hour: int
    
    modeled_assumptions: List[str]
    disclaimer: str = "ESTIMATED SIMULATION ONLY. Results are derived from parametric physics models and are not certified field measurements."


class WhatIfSimulator:
    """Parametric Heat Mitigation Simulator for HSE Safety Interventions."""

    @staticmethod
    def run_simulation(request: SimulationRequest) -> WhatIfSimulationResult:
        # 1. Baseline Calculations
        base_solar = max(0.0, request.solar_irradiance or 0.0)
        base_risk = RiskCalculator.calculate_derived_risk(
            temperature=request.temperature,
            wet_bulb_temperature=request.wet_bulb_temperature,
            solar_irradiance=base_solar
        )
        base_protocol = HSEProtocolEngine.generate_protocol(
            estimated_wbgt=base_risk.estimated_wbgt,
            workload=request.workload,
            solar_irradiance=base_solar
        )

        # 2. Model Solar Attenuation from Shading
        # Assumption: 100% shade reduces direct solar irradiance by up to 85% (diffuse light remains)
        solar_attenuation_factor = 1.0 - (0.85 * (request.shade_percent / 100.0))
        sim_solar = round(base_solar * solar_attenuation_factor, 1)

        # 3. Model Evaporative Cooling from Misting Fans
        # Assumption: Misting can bridge up to 35% of the psychrometric wet-bulb depression (T_dry - T_wet)
        wet_bulb_depression = max(0.0, request.temperature - request.wet_bulb_temperature)
        misting_cooling_delta = wet_bulb_depression * (0.35 * (request.misting_percent / 100.0))
        sim_temp = round(request.temperature - misting_cooling_delta, 1)

        # 4. Recalculate Derived Risk Metrics
        sim_risk = RiskCalculator.calculate_derived_risk(
            temperature=sim_temp,
            wet_bulb_temperature=request.wet_bulb_temperature,
            solar_irradiance=sim_solar
        )
        sim_protocol = HSEProtocolEngine.generate_protocol(
            estimated_wbgt=sim_risk.estimated_wbgt,
            workload=request.workload,
            solar_irradiance=sim_solar
        )

        # 5. Compute Recovered Productivity
        base_work_min = base_protocol.work_minutes_per_hour
        sim_work_min = sim_protocol.work_minutes_per_hour
        recovered_min = max(0, sim_work_min - base_work_min)

        return WhatIfSimulationResult(
            provenance=DataProvenance.SIMULATED,
            parameters_applied={
                "shade_percent": request.shade_percent,
                "misting_percent": request.misting_percent,
                "workload": request.workload.value
            },
            effective_solar_irradiance=SimulationMetricComparison(
                baseline=base_solar,
                simulated=sim_solar,
                delta=round(sim_solar - base_solar, 1),
                unit="W/m²"
            ),
            effective_temperature=SimulationMetricComparison(
                baseline=request.temperature,
                simulated=sim_temp,
                delta=round(sim_temp - request.temperature, 1),
                unit="°C"
            ),
            estimated_wbgt=SimulationMetricComparison(
                baseline=base_risk.estimated_wbgt or 0.0,
                simulated=sim_risk.estimated_wbgt or 0.0,
                delta=round((sim_risk.estimated_wbgt or 0.0) - (base_risk.estimated_wbgt or 0.0), 1),
                unit="°C"
            ),
            heat_strain_index=SimulationMetricComparison(
                baseline=base_risk.heat_strain_index or 0.0,
                simulated=sim_risk.heat_strain_index or 0.0,
                delta=round((sim_risk.heat_strain_index or 0.0) - (base_risk.heat_strain_index or 0.0), 1),
                unit="/100"
            ),
            baseline_protocol=base_protocol,
            simulated_protocol=sim_protocol,
            recovered_work_minutes_per_hour=recovered_min,
            modeled_assumptions=[
                "Shading attenuation modeled at max 85% direct solar irradiance reduction at 100% canopy coverage.",
                "Misting cooling modeled at max 35% wet-bulb depression reduction under active airflow.",
                "Simulated values are parameter estimates for planning and not recorded as live field observations."
            ]
        )
