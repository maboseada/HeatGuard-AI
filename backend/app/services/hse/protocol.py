from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.assessment import DataProvenance


class WorkloadCategory(str, Enum):
    LIGHT = "Light"         # Inspection, light tool handling, vehicle operation
    MODERATE = "Moderate"   # Walking, pipefitting, continuous equipment assembly
    HEAVY = "Heavy"         # Heavy lifting, scaffolding, trenching, manual shoveling


class HSEOperationalProtocol(BaseModel):
    provenance: DataProvenance = DataProvenance.DERIVED
    workload: WorkloadCategory
    estimated_wbgt: Optional[float] = None
    risk_category: str
    work_rest_ratio: str
    work_minutes_per_hour: int
    rest_minutes_per_hour: int
    mandatory_hydration_ml_per_hour: int
    recommended_ppe_modifications: List[str]
    critical_warnings: List[str]
    disclaimer: str = "Operational Decision Support only. Does not replace certified site safety officer discretion."


class HSEProtocolEngine:
    """Generates operational work-rest cycles, hydration rules, and safety advisories
    based on derived thermal strain and workload categories.
    """

    @staticmethod
    def generate_protocol(
        estimated_wbgt: Optional[float],
        workload: WorkloadCategory = WorkloadCategory.MODERATE,
        solar_irradiance: Optional[float] = None
    ) -> HSEOperationalProtocol:
        if estimated_wbgt is None:
            return HSEOperationalProtocol(
                provenance=DataProvenance.DERIVED,
                workload=workload,
                estimated_wbgt=None,
                risk_category="Awaiting Data",
                work_rest_ratio="Standard Shifts",
                work_minutes_per_hour=60,
                rest_minutes_per_hour=0,
                mandatory_hydration_ml_per_hour=500,
                recommended_ppe_modifications=["Standard industrial PPE."],
                critical_warnings=["Awaiting live thermal parameters before generating custom safety schedule."]
            )

        # Baseline Thresholds for Workload (WBGT in °C)
        # Thresholds adapted from NIOSH / ACGIH heat stress reference curves
        thresholds = {
            WorkloadCategory.LIGHT: {"mod": 28.0, "high": 31.0, "ext": 33.0},
            WorkloadCategory.MODERATE: {"mod": 26.0, "high": 29.0, "ext": 31.5},
            WorkloadCategory.HEAVY: {"mod": 24.5, "high": 27.5, "ext": 30.0},
        }

        th = thresholds[workload]

        warnings: List[List[str]] = []
        ppe_mods: List[str] = []

        if estimated_wbgt >= th["ext"]:
            risk_cat = "Extreme"
            work_min = 15
            rest_min = 45
            ratio = "15 min Work / 45 min Rest per hour"
            water_ml = 1000
            ppe_mods = ["Mandatory evaporative cooling vests", "Permeable high-ventilation flame-resistant coveralls"]
            warnings = [
                "DANGER: Heat stroke threshold reached for this workload.",
                "Enforce mandatory rest inside air-conditioned or active-misted cool zones.",
                "Two-man buddy system mandatory for all personnel."
            ]
        elif estimated_wbgt >= th["high"]:
            risk_cat = "High"
            work_min = 30
            rest_min = 30
            ratio = "30 min Work / 30 min Rest per hour"
            water_ml = 750
            ppe_mods = ["Shade neck flaps on hard hats", "Allow unbuttoning top layer in non-flash areas"]
            warnings = [
                "High thermal strain: limit continuous heavy exertion.",
                "Supervisor mandatory hydration checks every 30 minutes."
            ]
        elif estimated_wbgt >= th["mod"]:
            risk_cat = "Moderate"
            work_min = 45
            rest_min = 15
            ratio = "45 min Work / 15 min Rest per hour"
            water_ml = 600
            ppe_mods = ["Standard PPE with sweat-wicking base layers"]
            warnings = [
                "Elevated temperatures: ensure cold electrolyte replenishment is accessible."
            ]
        else:
            risk_cat = "Low"
            work_min = 60
            rest_min = 0
            ratio = "Normal Continuous Work (60m / 0m)"
            water_ml = 500
            ppe_mods = ["Standard site PPE"]
            warnings = ["Normal environmental conditions. Maintain standard hydration."]

        if solar_irradiance and solar_irradiance > 800:
            warnings.append("High direct solar radiation (>800 W/m²): Deploy temporary canopy shade over open work areas.")

        return HSEOperationalProtocol(
            provenance=DataProvenance.DERIVED,
            workload=workload,
            estimated_wbgt=estimated_wbgt,
            risk_category=risk_cat,
            work_rest_ratio=ratio,
            work_minutes_per_hour=work_min,
            rest_minutes_per_hour=rest_min,
            mandatory_hydration_ml_per_hour=water_ml,
            recommended_ppe_modifications=ppe_mods,
            critical_warnings=warnings
        )
