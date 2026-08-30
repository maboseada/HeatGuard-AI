import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api.routes import health, sites, analysis, jobs, assessment, intelligence
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="HeatGuard AI",
    description="Backend for HeatGuard AI - Hyperlocal Industrial Heat Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(sites.router, prefix="/api/sites", tags=["sites"])
app.include_router(analysis.router, prefix="/api/sites", tags=["analysis"])
app.include_router(assessment.router, prefix="/api/sites", tags=["assessment"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(intelligence.router, prefix="/api", tags=["intelligence"])
