from typing import Dict, Any

"""Explicitly labeled Synthetic Demo Data for HeatGuard AI.

DISCLAIMER: These fixtures are SYNTHETIC MOCK DATA designed for demonstration,
offline testing, and development fallback. They are NOT raw FortyGuard outputs.
Every normalized object derived from these fixtures is stamped with
provenance: 'demo_synthetic'.
"""

SYNTHETIC_DUBAI_INDUSTRIAL_HEATMAP: Dict[str, Any] = {
    "error": False,
    "status_code": 200,
    "message": "Completed [SYNTHETIC DEMO FIXTURE]",
    "data": {
        "activity_id": "demo-synthetic-dubai-heatmap-001",
        "status": "Completed",
        "result": {
            "map_data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "cell_id": "cell_1",
                            "temperature": 44.2,
                            "exceedance": 6.2,
                            "zone_name": "Fabrication Yard Alpha",
                            "is_hotspot": True
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [55.2700, 25.2040],
                                    [55.2710, 25.2040],
                                    [55.2710, 25.2050],
                                    [55.2700, 25.2050],
                                    [55.2700, 25.2040]
                                ]
                            ]
                        }
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "cell_id": "cell_2",
                            "temperature": 41.5,
                            "exceedance": 3.5,
                            "zone_name": "Central Storage Facility",
                            "is_hotspot": False
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [55.2710, 25.2040],
                                    [55.2720, 25.2040],
                                    [55.2720, 25.2050],
                                    [55.2710, 25.2050],
                                    [55.2710, 25.2040]
                                ]
                            ]
                        }
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "cell_id": "cell_3",
                            "temperature": 37.8,
                            "exceedance": 0.0,
                            "zone_name": "Covered Logistics Dock",
                            "is_hotspot": False
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [55.2700, 25.2050],
                                    [55.2710, 25.2050],
                                    [55.2710, 25.2060],
                                    [55.2700, 25.2060],
                                    [55.2700, 25.2050]
                                ]
                            ]
                        }
                    }
                ]
            },
            "stats_data": {
                "min_temperature": 37.8,
                "max_temperature": 44.2,
                "mean_temperature": 41.2,
                "median_temperature": 41.5,
                "standard_deviation": 2.6,
                "granularity": 60
            }
        }
    }
}

SYNTHETIC_DUBAI_INDUSTRIAL_ENV: Dict[str, Any] = {
    "error": False,
    "status_code": 200,
    "message": "Completed [SYNTHETIC DEMO FIXTURE]",
    "data": {
        "activity_id": "demo-synthetic-dubai-env-001",
        "status": "Completed",
        "result": {
            "temperature": 39.5,
            "heat_index_celsius": 46.2,
            "apparent_temperature_celsius": 44.8,
            "wet_bulb_temperature_celsius": 29.4,
            "relative_humidity_percent": 48.0,
            "solar_irradiance": 930.0,
            "precipitation_mm": 0.0,
            "cloud_cover_octas": 0.0,
            "elevation": 12.0,
            "air_quality:idx": None,
            "air_quality_pm2p5:idx": None
        }
    }
}
