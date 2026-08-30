# HeatGuard AI — Architecture

## System Overview

HeatGuard AI is an AI-powered hyperlocal heat risk intelligence platform for industrial safety. It integrates with FortyGuard's Temperature API to provide heat risk analysis, environmental monitoring, and safety intelligence for industrial/HSE teams.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │   Site    │ │  Metric  │ │  Heatmap │ │   AI Assistant   │   │
│  │ Selector │ │  Cards   │ │ Viewer   │ │   (Phase 2)      │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP (REST API)
┌───────────────────────┴─────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                    API Routes                          │     │
│  │  /health  /api/sites  /api/sites/{id}/heatmap  /jobs  │     │
│  └────────────────────┬───────────────────────────────────┘     │
│  ┌────────────────────┴───────────────────────────────────┐     │
│  │                  Service Layer                         │     │
│  │  ┌─────────────────────┐  ┌─────────────────────┐     │     │
│  │  │  FortyGuard Client  │  │    Job Manager       │     │     │
│  │  │  - Heatmap Service  │  │  - Submit job        │     │     │
│  │  │  - Env Service      │  │  - Background poll   │     │     │
│  │  │  - Status Service   │  │  - Store results     │     │     │
│  │  └─────────┬───────────┘  └──────────┬────────────┘     │     │
│  └────────────┼─────────────────────────┼────────────────┘     │
│  ┌────────────┼─────────────────────────┼────────────────┐     │
│  │            │    DB Repositories      │                │     │
│  │  ┌─────────┴──┐ ┌──────────┐ ┌──────┴──────┐         │     │
│  │  │  SiteRepo  │ │ JobRepo  │ │ ReadingRepo │         │     │
│  │  └────────────┘ └──────────┘ └─────────────┘         │     │
│  └────────────────────────┬──────────────────────────────┘     │
└───────────────────────────┼─────────────────────────────────────┘
                            │ asyncpg
┌───────────────────────────┴─────────────────────────────────────┐
│                     PostgreSQL Database                          │
│  ┌────────┐  ┌──────────────┐  ┌──────────────────────┐        │
│  │ sites  │  │ analysis_jobs│  │ environmental_readings│        │
│  └────────┘  └──────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## FortyGuard Integration Pattern

All FortyGuard API communication is isolated in `backend/app/services/fortyguard/`. This ensures:

1. **Isolation**: Provider-specific logic doesn't leak into business logic
2. **Testability**: Easy to mock the entire FortyGuard layer
3. **Swapability**: Different providers can be added without changing routes

### Async Job Flow

FortyGuard analysis endpoints are asynchronous — they return an `activity_id` immediately and process in the background.

```
1. User submits analysis request via frontend
2. Backend creates AnalysisJob (status: Pending)
3. Backend calls FortyGuard API (POST /heatmap or /env_params)
4. FortyGuard returns activity_id
5. Backend updates job with activity_id
6. Backend launches background polling task (asyncio.create_task)
7. HTTP response returns immediately with job_id
8. Background task polls GET /status/{activity_id} at intervals
9. On Completed: stores result, updates job status
10. On Failed: stores error, updates job status
11. On timeout: marks job as Failed
12. Frontend polls GET /api/jobs/{job_id} for updates
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS | Dashboard UI |
| Backend | Python 3.11, FastAPI, Pydantic | REST API & business logic |
| Database | PostgreSQL 16, SQLAlchemy (async) | Data persistence |
| HTTP Client | httpx | Async FortyGuard API calls |
| Containerization | Docker, docker-compose | Development environment |

## Key Design Decisions

1. **UUID primary keys** — Distributed-friendly, no sequential leaks
2. **Nullable environmental fields** — `null` = unavailable, never zero
3. **In-memory background tasks** — `asyncio.create_task()` for Phase 1 (Celery in Phase 2)
4. **SQLAlchemy async** — Non-blocking DB matching FastAPI's async nature
5. **create_all() on startup** — No Alembic migrations in Phase 1
