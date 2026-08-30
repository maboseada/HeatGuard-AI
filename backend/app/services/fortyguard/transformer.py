import logging
from typing import Dict, Any, Optional, Tuple, List
from app.schemas.assessment import (
    DataProvenance,
    NormalizedEnvironmental,
    NormalizedHeatmapStats,
)

logger = logging.getLogger(__name__)


class FortyGuardTransformer:
    """Safely normalizes raw FortyGuard API responses into HeatGuard internal schemas.
    
    Strictly adheres to data provenance rules:
    - Never fabricates or defaults missing values to 0.0 (null is preserved).
    - Preserves unmutated raw responses alongside normalized representations.
    - Accurately parses live FortyGuard structures (including locations arrays, parameter lists, and nested clear_sky irradiance).
    """

    @staticmethod
    def normalize_environmental(
        raw_response: Optional[Dict[str, Any]],
        provenance: DataProvenance = DataProvenance.RAW_FORTYGUARD
    ) -> Optional[NormalizedEnvironmental]:
        """Extracts environmental parameters from FortyGuard /env_params status result."""
        if not raw_response or not isinstance(raw_response, dict):
            return None

        # Unwrap FortyGuard response envelope
        data = raw_response.get("data", raw_response)
        if not isinstance(data, dict):
            return None
        
        result = data.get("result", data)
        if not isinstance(result, dict) or not result:
            return None

        # Check if structured as live FortyGuard 'locations' array
        location_obj = None
        params_obj = {}
        solar_obj = {}

        if "locations" in result and isinstance(result["locations"], list) and len(result["locations"]) > 0:
            location_obj = result["locations"][0]
            params_obj = location_obj.get("parameters", {})
            solar_obj = location_obj.get("solar_irradiance", {})
        else:
            # Fallback to direct top-level result dict
            location_obj = result
            params_obj = result
            solar_obj = result

        def _extract_val(obj: Dict[str, Any], key: str) -> Optional[float]:
            val = obj.get(key)
            if val is None:
                return None
            if isinstance(val, list):
                if len(val) == 0 or val[0] is None:
                    return None
                val = val[0]
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        # Extract temperature
        temp = _extract_val(location_obj, "temperature")

        # Extract parameters (supports both params_obj and top level)
        heat_idx = _extract_val(params_obj, "heat_index_celsius") or _extract_val(result, "heat_index_celsius")
        app_temp = _extract_val(params_obj, "apparent_temperature_celsius") or _extract_val(result, "apparent_temperature_celsius")
        wb_temp = _extract_val(params_obj, "wet_bulb_temperature_celsius") or _extract_val(result, "wet_bulb_temperature_celsius")
        rh = _extract_val(params_obj, "relative_humidity_percent") or _extract_val(result, "relative_humidity_percent")
        precip = _extract_val(params_obj, "precipitation_mm") or _extract_val(result, "precipitation_mm")
        cloud = _extract_val(params_obj, "cloud_cover_octas") or _extract_val(result, "cloud_cover_octas")
        aqi = _extract_val(params_obj, "air_quality:idx") or _extract_val(result, "air_quality:idx")

        # Extract solar irradiance (supports clear_sky.ghi or flat solar_irradiance)
        solar_ghi = None
        if isinstance(solar_obj, dict):
            clear_sky = solar_obj.get("clear_sky")
            if isinstance(clear_sky, dict) and "ghi" in clear_sky:
                solar_ghi = _extract_val(clear_sky, "ghi")
            elif "solar_irradiance" in solar_obj:
                solar_ghi = _extract_val(solar_obj, "solar_irradiance")

        return NormalizedEnvironmental(
            provenance=provenance,
            temperature=temp,
            heat_index=heat_idx,
            apparent_temperature=app_temp,
            wet_bulb_temperature=wb_temp,
            relative_humidity=rh,
            solar_irradiance=solar_ghi,
            precipitation_mm=precip,
            cloud_cover_octas=cloud,
            air_quality_index=aqi,
        )

    @staticmethod
    def normalize_heatmap(
        raw_response: Optional[Dict[str, Any]],
        provenance: DataProvenance = DataProvenance.RAW_FORTYGUARD
    ) -> Tuple[Optional[Dict[str, Any]], Optional[NormalizedHeatmapStats]]:
        """Extracts GeoJSON map_data and stats_data from FortyGuard /heatmap status result."""
        if not raw_response or not isinstance(raw_response, dict):
            return None, None

        data = raw_response.get("data", raw_response)
        if not isinstance(data, dict):
            return None, None

        result = data.get("result", data)
        if not isinstance(result, dict) or not result:
            return None, None

        # 1. Parse and validate GeoJSON map_data
        map_geojson = None
        raw_map_data = result.get("map_data")
        if isinstance(raw_map_data, dict):
            if raw_map_data.get("type") in ("FeatureCollection", "Feature", "Polygon", "MultiPolygon"):
                map_geojson = raw_map_data
        elif isinstance(result.get("features"), list):
            map_geojson = {
                "type": "FeatureCollection",
                "features": result.get("features", [])
            }

        # 2. Parse stats_data
        stats = None
        raw_stats = result.get("stats_data") or result.get("statistics")
        if isinstance(raw_stats, dict):
            def _get_stat_float(key: str) -> Optional[float]:
                val = raw_stats.get(key)
                if val is None:
                    return None
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None

            stats = NormalizedHeatmapStats(
                provenance=provenance,
                min_temperature=_get_stat_float("min_temperature") or _get_stat_float("min"),
                max_temperature=_get_stat_float("max_temperature") or _get_stat_float("max"),
                mean_temperature=_get_stat_float("mean_temperature") or _get_stat_float("mean"),
                median_temperature=_get_stat_float("median_temperature") or _get_stat_float("median"),
                standard_deviation=_get_stat_float("standard_deviation") or _get_stat_float("std"),
                granularity=raw_stats.get("granularity"),
            )

        return map_geojson, stats
