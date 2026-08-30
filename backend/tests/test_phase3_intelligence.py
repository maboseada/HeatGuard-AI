import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db
from app.services.risk.calculator import RiskCalculator
from app.services.hse.protocol import HSEProtocolEngine, WorkloadCategory
from app.services.explainability.service import ExplainabilityService
from app.services.simulator.simulator import WhatIfSimulator, SimulationRequest
from app.schemas.assessment import DataProvenance


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield


# ---------------- 1. Risk Calculator Tests ----------------
def test_risk_calculator_outdoor_solar():
    metrics = RiskCalculator.calculate_derived_risk(
        temperature=40.0,
        wet_bulb_temperature=29.0,
        solar_irradiance=900.0
    )
    assert metrics.provenance == DataProvenance.DERIVED
    assert metrics.estimated_wbgt is not None
    # 0.7 * 29 + 0.2 * (40 + 0.0128 * 900) + 0.1 * 40 = 20.3 + 10.3 + 4.0 = 34.6
    assert metrics.estimated_wbgt >= 33.0
    assert metrics.thermal_severity_category == "Extreme"
    assert metrics.heat_strain_index is not None
    assert metrics.heat_strain_index > 70.0


def test_risk_calculator_shaded_fallback():
    metrics = RiskCalculator.calculate_derived_risk(
        temperature=35.0,
        wet_bulb_temperature=25.0,
        solar_irradiance=None
    )
    assert metrics.estimated_wbgt is not None
    # 0.7 * 25 + 0.3 * 35 = 17.5 + 10.5 = 28.0
    assert metrics.estimated_wbgt == 28.0
    assert metrics.thermal_severity_category in ("Moderate", "High")


def test_risk_calculator_strict_null_handling():
    # If dry-bulb or wet-bulb is None, MUST return None (never zero)
    metrics_no_temp = RiskCalculator.calculate_derived_risk(None, 25.0, 500.0)
    assert metrics_no_temp.estimated_wbgt is None
    assert metrics_no_temp.heat_strain_index is None

    metrics_no_wb = RiskCalculator.calculate_derived_risk(35.0, None, 500.0)
    assert metrics_no_wb.estimated_wbgt is None
    assert metrics_no_wb.heat_strain_index is None


# ---------------- 2. HSE Protocol Tests ----------------
def test_hse_protocol_workloads():
    # Heavy workload should trigger extreme risk at lower WBGT than Light workload
    wbgt = 30.5
    proto_light = HSEProtocolEngine.generate_protocol(wbgt, WorkloadCategory.LIGHT)
    proto_heavy = HSEProtocolEngine.generate_protocol(wbgt, WorkloadCategory.HEAVY)

    assert proto_light.risk_category in ("Moderate", "High")
    assert proto_heavy.risk_category == "Extreme"
    assert proto_heavy.rest_minutes_per_hour >= 45
    assert proto_heavy.mandatory_hydration_ml_per_hour >= 1000


def test_hse_protocol_solar_advisory():
    proto = HSEProtocolEngine.generate_protocol(
        estimated_wbgt=28.0,
        workload=WorkloadCategory.MODERATE,
        solar_irradiance=950.0
    )
    # Check that high solar irradiance warning is included
    has_solar_warning = any("solar radiation" in w.lower() for w in proto.critical_warnings)
    assert has_solar_warning


# ---------------- 3. Explainability Service Tests ----------------
def test_explainability_report_triad():
    report = ExplainabilityService.generate_report(
        site_name="Test Refinery Yard",
        coordinates=[25.2, 55.2],
        temperature=39.0,
        wet_bulb=28.5,
        solar_ghi=900.0,
        humidity=50.0,
        cell_id="cell_hotspot_1",
        zone_label="Tank Farm B",
        cell_temp=44.0,
        exceedance=5.0
    )
    # WHERE
    assert report.where.grid_cell_id == "cell_hotspot_1"
    assert report.where.thermal_exceedance_delta == 5.0

    # WHY
    assert len(report.why.factor_contributions) >= 3
    assert any(c.factor == "Solar Radiation (GHI)" for c in report.why.factor_contributions)

    # WHAT
    assert report.what.risk_category in ("High", "Extreme")
    assert report.what.hydration_guidance is not None
    assert len(report.what.critical_ppe_actions) > 0


# ---------------- 4. What-If Simulator Tests ----------------
def test_what_if_simulation_physics():
    req = SimulationRequest(
        temperature=42.0,
        wet_bulb_temperature=28.0,
        solar_irradiance=900.0,
        shade_percent=80.0,
        misting_percent=60.0,
        workload=WorkloadCategory.HEAVY
    )
    result = WhatIfSimulator.run_simulation(req)
    assert result.provenance == DataProvenance.SIMULATED

    # Solar irradiance should be attenuated
    assert result.effective_solar_irradiance.simulated < result.effective_solar_irradiance.baseline
    # Effective temperature should drop due to misting
    assert result.effective_temperature.simulated < result.effective_temperature.baseline
    # Estimated WBGT should decrease
    assert result.estimated_wbgt.simulated < result.estimated_wbgt.baseline
    # Work minutes recovered should be >= 0
    assert result.recovered_work_minutes_per_hour >= 0


# ---------------- 5. API Routes Tests ----------------
@pytest.mark.asyncio
async def test_simulate_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/simulate", json={
            "temperature": 40.0,
            "wet_bulb_temperature": 27.0,
            "solar_irradiance": 800.0,
            "shade_percent": 50.0,
            "misting_percent": 50.0,
            "workload": "Moderate"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provenance"] == "simulated"
        assert "effective_temperature" in data
        assert "recovered_work_minutes_per_hour" in data
