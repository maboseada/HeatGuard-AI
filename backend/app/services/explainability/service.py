from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.schemas.assessment import DataProvenance
from app.services.risk.calculator import RiskCalculator, DerivedRiskMetrics
from app.services.hse.protocol import HSEProtocolEngine, HSEOperationalProtocol, WorkloadCategory


class WhereDimension(BaseModel):
    site_name: str
    coordinates: List[float] # [lat, lng]
    grid_cell_id: Optional[str] = None
    zone_label: Optional[str] = None
    micro_surface_temperature: Optional[float] = None
    thermal_exceedance_delta: Optional[float] = None


class EnvironmentalFactorContribution(BaseModel):
    factor: str
    raw_value: Optional[str]
    contribution_level: str # Low, Moderate, High, Critical
    explanation: str


class WhyDimension(BaseModel):
    surface_thermal_impact: str
    factor_contributions: List[EnvironmentalFactorContribution]
    primary_risk_driver: str


class WhatDimension(BaseModel):
    risk_category: str
    heat_strain_score: Optional[float]
    estimated_wbgt: Optional[float]
    work_rest_guidance: str
    hydration_guidance: str
    critical_ppe_actions: List[str]
    warnings: List[str]


class ExplainabilityReport(BaseModel):
    provenance_summary: Dict[str, str]
    where: WhereDimension
    why: WhyDimension
    what: WhatDimension
    disclaimer: str = "Explainability analysis based on FortyGuard microclimate parameters and HeatGuard AI physiological thermal models."


class ExplainabilityService:
    """Generates the structured WHERE / WHY / WHAT explainability diagnostic."""

    @staticmethod
    def generate_report(
        site_name: str,
        coordinates: List[float],
        temperature: Optional[float],
        wet_bulb: Optional[float],
        solar_ghi: Optional[float],
        humidity: Optional[float],
        cell_id: Optional[str] = None,
        zone_label: Optional[str] = None,
        cell_temp: Optional[float] = None,
        exceedance: Optional[float] = None,
        workload: WorkloadCategory = WorkloadCategory.MODERATE
    ) -> ExplainabilityReport:
        # 1. Compute Derived Risk Metrics
        effective_temp = cell_temp if cell_temp is not None else temperature
        risk_metrics: DerivedRiskMetrics = RiskCalculator.calculate_derived_risk(
            temperature=effective_temp,
            wet_bulb_temperature=wet_bulb,
            solar_irradiance=solar_ghi
        )

        # 2. Compute HSE Protocols
        hse_protocol: HSEOperationalProtocol = HSEProtocolEngine.generate_protocol(
            estimated_wbgt=risk_metrics.estimated_wbgt,
            workload=workload,
            solar_irradiance=solar_ghi
        )

        # 3. Build WHERE
        delta_t = exceedance
        if delta_t is None and cell_temp is not None and temperature is not None:
            delta_t = round(cell_temp - temperature, 1)

        where = WhereDimension(
            site_name=site_name,
            coordinates=coordinates,
            grid_cell_id=cell_id or "Facility Baseline",
            zone_label=zone_label or "General Site Area",
            micro_surface_temperature=cell_temp or temperature,
            thermal_exceedance_delta=delta_t
        )

        # 4. Build WHY (Factor Contribution Decomposition)
        contributions: List[EnvironmentalFactorContribution] = []

        # Temperature Factor
        t_val = effective_temp
        if t_val is not None:
            t_level = "Critical" if t_val >= 42 else ("High" if t_val >= 38 else ("Moderate" if t_val >= 32 else "Low"))
            contributions.append(EnvironmentalFactorContribution(
                factor="Dry-Bulb Ambient & Surface Heat",
                raw_value=f"{t_val:.1f}°C",
                contribution_level=t_level,
                explanation="High convective and radiant ambient air temperature heating the body."
            ))

        # Wet-Bulb Factor (Evaporative Resistance)
        if wet_bulb is not None:
            wb_level = "Critical" if wet_bulb >= 30 else ("High" if wet_bulb >= 28 else ("Moderate" if wet_bulb >= 24 else "Low"))
            contributions.append(EnvironmentalFactorContribution(
                factor="Wet-Bulb Evaporative Limit",
                raw_value=f"{wet_bulb:.1f}°C",
                contribution_level=wb_level,
                explanation="Humid air limits the efficiency of sweat evaporation for human thermoregulation."
            ))

        # Solar Irradiance Factor
        if solar_ghi is not None:
            sol_level = "Critical" if solar_ghi >= 900 else ("High" if solar_ghi >= 700 else ("Moderate" if solar_ghi >= 400 else "Low"))
            contributions.append(EnvironmentalFactorContribution(
                factor="Solar Radiation (GHI)",
                raw_value=f"{solar_ghi:.0f} W/m²",
                contribution_level=sol_level,
                explanation="Direct solar radiation adds radiant thermal load on dark, unshaded surfaces and workers."
            ))

        # Relative Humidity
        if humidity is not None:
            rh_level = "High" if humidity >= 65 else ("Moderate" if humidity >= 40 else "Low")
            contributions.append(EnvironmentalFactorContribution(
                factor="Relative Humidity",
                raw_value=f"{humidity:.0f}%",
                contribution_level=rh_level,
                explanation="Moisture in the air dampens physiological cooling mechanisms."
            ))

        primary_driver = "Intense Solar Radiation & Impervious Surface Trapping" if (solar_ghi and solar_ghi > 750) else "Elevated Ambient Air & Wet Bulb Temperature"

        why = WhyDimension(
            surface_thermal_impact=f"Surface thermal exceedance of +{delta_t:.1f}°C above ambient due to high thermal mass and unshaded exposure." if delta_t and delta_t > 0 else "Baseline ambient thermal conditions.",
            factor_contributions=contributions,
            primary_risk_driver=primary_driver
        )

        # 5. Build WHAT
        what = WhatDimension(
            risk_category=risk_metrics.thermal_severity_category or "Moderate",
            heat_strain_score=risk_metrics.heat_strain_index,
            estimated_wbgt=risk_metrics.estimated_wbgt,
            work_rest_guidance=hse_protocol.work_rest_ratio,
            hydration_guidance=f"Mandatory minimum {hse_protocol.mandatory_hydration_ml_per_hour} ml/hr cold electrolyte water.",
            critical_ppe_actions=hse_protocol.recommended_ppe_modifications,
            warnings=hse_protocol.critical_warnings
        )

        return ExplainabilityReport(
            provenance_summary={
                "raw_fortyguard": "Measured/modeled ambient temperature, wet bulb, and solar irradiance.",
                "derived_heatguard": "Estimated WBGT, Heat Strain Index, and factor decomposition.",
                "hse_protocol": "Operational decision support thresholds (ACGIH/NIOSH based)."
            },
            where=where,
            why=why,
            what=what
        )
