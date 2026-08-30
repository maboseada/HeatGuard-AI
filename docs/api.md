# HeatGuard AI — API Documentation

## Base URL

```
http://localhost:8000
```

---

## Health Check

### `GET /health`

Returns the health status of the backend and database connection.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## Unified Site Assessment (Phase 2A Core)

### `POST /api/sites/{site_id}/assess`

Triggers a unified microclimate assessment for an industrial facility. Runs both `/heatmap` and `/env_params` under a single coordinated job.

**Request Body**
```json
{
  "mode": "DEMO",
  "granularity": 60,
  "temperature": 38.5,
  "analytic_type": "tcm",
  "threshold": 40.0,
  "direction": "above"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `"DEMO"` | `"LIVE"` (polls real FortyGuard API) or `"DEMO"` (instant synthetic benchmark fixture) |
| `granularity` | int | `60` | Grid resolution: `60`, `80`, or `100` meters |
| `temperature` | float | `null` | Optional current ambient temperature in °C |
| `analytic_type` | string | `"tcm"` | Analysis type: `tcm`, `time_of_measure`, `exceedance`, `persistence` |

**Response** `200 OK` (or `202 Accepted` during live polling)
```json
{
  "id": "c1f7a46e-1d33-4f9e-a0e2-348b61c47281",
  "site_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "mode": "DEMO",
  "status": "Completed",
  "heatmap_activity_id": "demo-synthetic-dubai-heatmap-001",
  "env_activity_id": "demo-synthetic-dubai-env-001",
  "created_at": "2026-08-30T15:00:00Z",
  "completed_at": "2026-08-30T15:00:01Z",
  "raw_heatmap_payload": { ... },
  "raw_env_payload": { ... },
  "map_geojson": {
    "type": "FeatureCollection",
    "features": [ ... ]
  },
  "stats": {
    "provenance": "demo_synthetic",
    "min_temperature": 37.8,
    "max_temperature": 44.2,
    "mean_temperature": 41.2,
    "granularity": 60
  },
  "environmental": {
    "provenance": "demo_synthetic",
    "temperature": 39.5,
    "heat_index": 46.2,
    "apparent_temperature": 44.8,
    "wet_bulb_temperature": 29.4,
    "relative_humidity": 48.0,
    "solar_irradiance": 930.0
  }
}
```

---

### `GET /api/sites/{site_id}/assessment/latest`

Retrieves the most recent assessment for a specific facility location.

**Response** `200 OK`
Returns the `AssessmentResponse` object shown above.

---

## Sites

### `POST /api/sites`

Create a new industrial facility location.

### `GET /api/sites`

List all registered facilities.

### `GET /api/sites/{site_id}`

Get details for a specific site.
