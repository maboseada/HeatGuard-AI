import pytest
from app.services.fortyguard.transformer import FortyGuardTransformer
from app.schemas.assessment import DataProvenance


def test_transformer_environmental_real_shape():
    raw_env = {
        "data": {
            "activity_id": "test-env-123",
            "status": "Completed",
            "result": {
                "temperature": 38.2,
                "heat_index_celsius": 44.5,
                "apparent_temperature_celsius": 43.1,
                "wet_bulb_temperature_celsius": 29.0,
                "relative_humidity_percent": 52.0,
                "solar_irradiance": 910.0,
                "precipitation_mm": 0.0,
                "cloud_cover_octas": 2.0,
                "air_quality:idx": None
            }
        }
    }
    norm = FortyGuardTransformer.normalize_environmental(raw_env, DataProvenance.RAW_FORTYGUARD)
    assert norm is not None
    assert norm.provenance == DataProvenance.RAW_FORTYGUARD
    assert norm.temperature == 38.2
    assert norm.heat_index == 44.5
    assert norm.solar_irradiance == 910.0
    assert norm.air_quality_index is None  # Null preserved


def test_transformer_null_environmental_values_never_zero():
    raw_env = {
        "data": {
            "result": {
                "temperature": 35.0,
                "heat_index_celsius": None,
                "apparent_temperature_celsius": None,
                "wet_bulb_temperature_celsius": None,
                "relative_humidity_percent": None,
                "solar_irradiance": None,
            }
        }
    }
    norm = FortyGuardTransformer.normalize_environmental(raw_env, DataProvenance.RAW_FORTYGUARD)
    assert norm is not None
    assert norm.temperature == 35.0
    assert norm.heat_index is None
    assert norm.apparent_temperature is None
    assert norm.wet_bulb_temperature is None
    assert norm.relative_humidity is None
    assert norm.solar_irradiance is None


def test_transformer_malformed_environmental_response():
    assert FortyGuardTransformer.normalize_environmental(None) is None
    assert FortyGuardTransformer.normalize_environmental({}) is None
    assert FortyGuardTransformer.normalize_environmental({"data": "invalid_string"}) is None


def test_transformer_heatmap_real_shape():
    raw_heatmap = {
        "data": {
            "result": {
                "map_data": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"temperature": 40.1, "exceedance": 2.1},
                            "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
                        }
                    ]
                },
                "stats_data": {
                    "min_temperature": 36.0,
                    "max_temperature": 42.0,
                    "mean_temperature": 39.5,
                    "median_temperature": 39.0,
                    "standard_deviation": 1.5,
                    "granularity": 100
                }
            }
        }
    }
    map_geo, stats = FortyGuardTransformer.normalize_heatmap(raw_heatmap, DataProvenance.RAW_FORTYGUARD)
    assert map_geo is not None
    assert map_geo["type"] == "FeatureCollection"
    assert len(map_geo["features"]) == 1
    assert stats is not None
    assert stats.provenance == DataProvenance.RAW_FORTYGUARD
    assert stats.min_temperature == 36.0
    assert stats.max_temperature == 42.0
    assert stats.mean_temperature == 39.5
    assert stats.granularity == 100


def test_transformer_malformed_heatmap_data():
    raw_bad = {
        "data": {
            "result": {
                "map_data": {"type": "NotAGeoJSONType"},
                "stats_data": None
            }
        }
    }
    map_geo, stats = FortyGuardTransformer.normalize_heatmap(raw_bad, DataProvenance.RAW_FORTYGUARD)
    assert map_geo is None
    assert stats is None
