from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.db.database import get_db
from app.services.explainability.service import ExplainabilityService, ExplainabilityReport
from app.services.simulator.simulator import WhatIfSimulator, SimulationRequest, WhatIfSimulationResult
from app.services.hse.protocol import WorkloadCategory
from app.db.repositories import site_repo, assessment_repo

router = APIRouter()


@router.get("/sites/{site_id}/explain", response_model=ExplainabilityReport)
async def get_site_explainability(
    site_id: UUID,
    cell_id: Optional[str] = None,
    workload: WorkloadCategory = WorkloadCategory.MODERATE,
    db: AsyncSession = Depends(get_db)
):
    site = await site_repo.get_site(db, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")

    assessment = await assessment_repo.get_latest_site_assessment(db, site_id)
    
    # Extract environmental parameters
    env = assessment.environmental if assessment and assessment.environmental else {}
    temperature = env.get("temperature", 38.0)
    wet_bulb = env.get("wet_bulb_temperature", 28.5)
    solar_ghi = env.get("solar_irradiance", 850.0)
    humidity = env.get("relative_humidity", 50.0)

    # If inspecting specific grid cell from GeoJSON
    cell_temp = None
    exceedance = None
    zone_label = None

    if cell_id and assessment and assessment.map_geojson:
        features = assessment.map_geojson.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            if props.get("cell_id") == cell_id:
                cell_temp = props.get("temperature")
                exceedance = props.get("exceedance")
                zone_label = props.get("zone_name")
                break

    report = ExplainabilityService.generate_report(
        site_name=site.name,
        coordinates=[site.latitude, site.longitude],
        temperature=temperature,
        wet_bulb=wet_bulb,
        solar_ghi=solar_ghi,
        humidity=humidity,
        cell_id=cell_id,
        zone_label=zone_label,
        cell_temp=cell_temp,
        exceedance=exceedance,
        workload=workload
    )
    return report


@router.post("/simulate", response_model=WhatIfSimulationResult)
async def run_what_if_simulation(request: SimulationRequest):
    try:
        return WhatIfSimulator.run_simulation(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")
