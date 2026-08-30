# HeatGuard AI

**AI-Powered Hyperlocal Heat Risk Intelligence for Industrial Safety**

HeatGuard AI transforms hyperlocal temperature and environmental data into actionable heat-risk intelligence for industrial and HSE (Health, Safety, Environment) teams. It integrates with [FortyGuard's Temperature API](https://fortyguard.com) to provide real-time environmental monitoring, heatmap analysis, and risk scoring.

---

## Architecture

```
┌──────────────────────────────────┐
│      Frontend (Next.js)          │
│   Dashboard · Site Selector ·    │
│   Metrics · Heatmap · Alerts     │
└──────────────┬───────────────────┘
               │ HTTP REST
┌──────────────┴───────────────────┐
│      Backend (FastAPI)           │
│   Routes · Services · Jobs      │
│   ┌─────────────────────────┐   │
│   │  FortyGuard API Client  │───┼──→ FortyGuard API
│   └─────────────────────────┘   │
│   ┌─────────────────────────┐   │
│   │  Background Job Manager │   │
│   └─────────────────────────┘   │
└──────────────┬───────────────────┘
               │ asyncpg
┌──────────────┴───────────────────┐
│       PostgreSQL Database        │
│   Sites · AnalysisJobs ·        │
│   EnvironmentalReadings          │
└──────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Pydantic |
| Database | PostgreSQL 16, SQLAlchemy (async) |
| HTTP Client | httpx (async) |
| Infrastructure | Docker, docker-compose |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- A FortyGuard API key (obtain from [fortyguard.com](https://fortyguard.com))

### 1. Clone and configure

```bash
git clone <repo-url>
cd heatguard-ai
cp .env.example .env
```

Edit `.env` and set your FortyGuard API key:

```bash
FORTYGUARD_API_KEY=your_actual_api_key_here
```

### 2. Run with Docker

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Backend** (FastAPI) on [http://localhost:8000](http://localhost:8000)
- **Frontend** (Next.js) on [http://localhost:3000](http://localhost:3000)

### 3. Verify

```bash
# Health check
curl http://localhost:8000/health

# Open dashboard
open http://localhost:3000
```

---

## Running Locally (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ensure PostgreSQL is running and DATABASE_URL is set
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FORTYGUARD_API_KEY` | FortyGuard API authentication key | **(required)** |
| `FORTYGUARD_BASE_URL` | FortyGuard API base URL | `https://api.fortyguard.com/v1` |
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) | **(required)** |
| `POSTGRES_USER` | PostgreSQL username | `heatguard` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `heatguard_password` |
| `POSTGRES_DB` | PostgreSQL database name | `heatguard_db` |
| `POLL_INTERVAL_SECONDS` | Seconds between status polls | `5` |
| `MAX_POLL_ATTEMPTS` | Maximum polling attempts before timeout | `60` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend API calls | `http://localhost:8000` |

> **⚠️ Never commit `.env` to version control.** The `.gitignore` excludes it.

---

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check with DB status |

### Sites
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sites` | Create a new industrial site |
| GET | `/api/sites` | List all sites |
| GET | `/api/sites/{site_id}` | Get site details |

### Analysis
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sites/{site_id}/heatmap` | Submit heatmap analysis |
| POST | `/api/sites/{site_id}/environment` | Submit environmental analysis |

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/jobs/{job_id}` | Get job status and results |

Full API documentation: [docs/api.md](docs/api.md)

---

## FortyGuard Integration

HeatGuard AI integrates with the FortyGuard Temperature API for:

1. **Heatmap Analysis** (`POST /heatmap`) — Submit a polygon area for thermal analysis
2. **Environmental Parameters** (`POST /env_params`) — Get environmental readings for a point
3. **Status Polling** (`GET /status/{activity_id}`) — Check job completion

### Key Integration Details

- All FortyGuard code is isolated in `backend/app/services/fortyguard/`
- The API key is injected via environment variables, never hardcoded
- API keys are never logged (redaction filter applied)
- The frontend never communicates directly with FortyGuard

---

## Async Job Lifecycle

FortyGuard analysis endpoints are asynchronous. The system implements a non-blocking polling pattern:

```
1. Frontend submits analysis request
2. Backend creates AnalysisJob record (status: Pending)
3. Backend POSTs to FortyGuard API
4. FortyGuard returns activity_id
5. Backend updates job with activity_id (status: Processing)
6. HTTP response returns immediately to frontend
7. Background task polls GET /status/{activity_id}
   └── Bounded by POLL_INTERVAL_SECONDS and MAX_POLL_ATTEMPTS
8. On Completed → stores result, updates job
9. On Failed → stores error, updates job
10. On Timeout → marks job as Failed with timeout message
11. Frontend polls GET /api/jobs/{job_id} for updates
```

**Important**: Background polling uses `asyncio.create_task()` — tasks are in-memory and will be lost on server restart. This is acceptable for Phase 1.

---

## Database Schema

### Sites
Stores industrial site locations and boundaries.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | String | Site name |
| description | String? | Optional description |
| latitude | Float | Site latitude |
| longitude | Float | Site longitude |
| boundary_geojson | JSON? | GeoJSON boundary |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### AnalysisJobs
Tracks FortyGuard analysis requests and their results.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| site_id | UUID | FK to sites |
| provider | String | Always "fortyguard" |
| activity_id | String? | FortyGuard activity UUID |
| analysis_type | String | "heatmap" or "environmental" |
| status | String | Pending / Processing / Completed / Failed |
| request_payload | JSON | Original request |
| result_payload | JSON? | FortyGuard result (when Completed) |
| error_message | String? | Error details (when Failed) |
| created_at | DateTime | Submission time |
| completed_at | DateTime? | Completion time |

### EnvironmentalReadings
Stores environmental measurements. **All measurement fields are nullable** — `null` means "data unavailable", never zero.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| site_id | UUID | FK to sites |
| timestamp | DateTime | Measurement time |
| temperature | Float? | Temperature °C |
| heat_index | Float? | Heat index °C |
| apparent_temperature | Float? | Apparent temperature °C |
| wet_bulb_temperature | Float? | Wet bulb temperature °C |
| relative_humidity | Float? | Relative humidity % |
| solar_ghi | Float? | Global horizontal irradiance |
| solar_dni | Float? | Direct normal irradiance |
| solar_dhi | Float? | Diffuse horizontal irradiance |

---

## Testing

Run the backend tests (no real API key required):

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Test Coverage

| Test File | What It Tests |
|-----------|--------------|
| `test_fortyguard_client.py` | Auth headers, request construction, timeouts, HTTP errors, malformed JSON |
| `test_heatmap_service.py` | Payload structure (FeatureCollection), granularity validation, optional params |
| `test_environmental_service.py` | Payload format, null value preservation |
| `test_status_service.py` | Processing/Completed/Failed status handling |
| `test_job_manager.py` | Job creation, polling lifecycle, timeout handling |
| `test_api_routes.py` | Health endpoint, site CRUD, 404 handling, validation |

All tests mock FortyGuard API calls — no external network access required.

---

## Project Structure

```
heatguard-ai/
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Dashboard UI components
│   │   ├── lib/              # API client, mock data
│   │   └── types/            # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI endpoints
│   │   ├── core/             # Config, logging
│   │   ├── db/               # Database, repositories
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/
│   │       ├── fortyguard/   # FortyGuard API client (isolated)
│   │       └── jobs/         # Background job manager
│   ├── tests/                # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   └── api.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Current MVP Limitations

- **No ML model** — Heat risk scoring uses simple thresholds, not ML predictions
- **No AI agent** — AI assistant placeholder only, no LLM integration
- **No real heatmap visualization** — Map placeholder prepared for future Leaflet/Mapbox
- **In-memory background tasks** — Polling tasks lost on server restart (no Celery/Redis)
- **No Alembic migrations** — Tables created via `create_all()` on startup
- **No authentication** — No user auth or API key management for the internal API
- **No satellite/street-view** — Placeholder for future integration
- **Mock dashboard data** — Environmental cards show demo values until backend wiring is complete

---

## Future Phases

| Phase | Feature |
|-------|---------|
| Phase 2 | ML heat risk scoring model, real heatmap visualization (Leaflet/Mapbox) |
| Phase 3 | AI safety assistant (LLM agent), what-if simulation |
| Phase 4 | HSE alerts system, notification pipelines |
| Phase 5 | Satellite/street-view intelligence, advanced analytics |

---

## License

Proprietary — All rights reserved.
