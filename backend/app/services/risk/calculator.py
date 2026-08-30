from typing import Optional, Dict, Any
from app.schemas.assessment import DataProvenance
from pydantic import BaseModel


class DerivedRiskMetrics(BaseModel):
    provenance: DataProvenance = DataProvenance.DERIVED
    estimated_wbgt: Optional[float] = None
    heat_strain_index: Optional[float] = None
    thermal_severity_category: Optional[str] = None
    calculation_notes: str


class RiskCalculator:
    """Scientific Risk Calculation Engine for Industrial Heat Exposure.
    
    FORMULAS AND ASSUMPTIONS:
    1. Estimated WBGT (Outdoor with Solar Load):
       WBGT_est = 0.7 * T_wetbulb + 0.2 * T_globe_est + 0.1 * T_drybulb
       where T_globe_est ≈ T_drybulb + 0.0128 * Solar_GHI (Liljegren solar approximation)
       If Solar GHI is unavailable, uses shaded approximation:
       WBGT_shaded = 0.7 * T_wetbulb + 0.3 * T_drybulb

    2. Physiological Heat Strain Index (0 - 100 scale):
       Strain Index = clamp(0, 100, ((WBGT_est - 20) / 18) * 100)
       - < 25: Low Strain (Safe)
       - 25 - 55: Moderate Strain
       - 55 - 75: High Strain (Action Required)
       - > 75: Extreme Strain (Critical Danger)

    STRICT NULL RULES:
    - If temperature or wet bulb temperature is missing (None), returns None.
    - Missing values are NEVER converted to zero.
    """

    @staticmethod
    def calculate_derived_risk(
        temperature: Optional[float],
        wet_bulb_temperature: Optional[float],
        solar_irradiance: Optional[float] = None
    ) -> DerivedRiskMetrics:
        # Check prerequisites
        if temperature is None or wet_bulb_temperature is None:
            return DerivedRiskMetrics(
                provenance=DataProvenance.DERIVED,
                estimated_wbgt=None,
                heat_strain_index=None,
                thermal_severity_category=None,
                calculation_notes="Insufficient inputs: dry bulb temperature or wet bulb temperature is unavailable."
            )

        # 1. Calculate Estimated WBGT
        wbgt_est: float
        if solar_irradiance is not None and solar_irradiance >= 0:
            # Full Outdoor Solar Radiation Model
            t_globe_est = temperature + (0.0128 * solar_irradiance)
            wbgt_est = (0.7 * wet_bulb_temperature) + (0.2 * t_globe_est) + (0.1 * temperature)
            notes = "Outdoor WBGT estimated using Liljegren solar radiation approximation."
        else:
            # Shaded / Ambient approximation
            wbgt_est = (0.7 * wet_bulb_temperature) + (0.3 * temperature)
            notes = "Shaded WBGT estimated without direct solar radiation component."

        wbgt_est = round(wbgt_est, 1)

        # 2. Calculate Heat Strain Index (0 - 100)
        strain_raw = ((wbgt_est - 20.0) / 18.0) * 100.0
        strain_index = round(max(0.0, min(100.0, strain_raw)), 1)

        # 3. Categorize Severity
        if strain_index >= 75.0 or wbgt_est >= 32.0:
            category = "Extreme"
        elif strain_index >= 55.0 or wbgt_est >= 29.5:
            category = "High"
        elif strain_index >= 25.0 or wbgt_est >= 26.0:
            category = "Moderate"
        else:
            category = "Low"

        return DerivedRiskMetrics(
            provenance=DataProvenance.DERIVED,
            estimated_wbgt=wbgt_est,
            heat_strain_index=strain_index,
            thermal_severity_category=category,
            calculation_notes=notes
        )
