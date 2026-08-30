from fastapi import Depends
from app.core.config import get_settings
from app.services.fortyguard.client import FortyGuardClient
from app.services.jobs.manager import JobManager
from app.services.jobs.assessment_manager import AssessmentManager


def get_fortyguard_client() -> FortyGuardClient:
    settings = get_settings()
    return FortyGuardClient(
        base_url=settings.FORTYGUARD_BASE_URL,
        api_key=settings.FORTYGUARD_API_KEY,
        timeout=settings.FORTYGUARD_TIMEOUT_SECONDS
    )


def get_job_manager() -> JobManager:
    return JobManager()


def get_assessment_manager() -> AssessmentManager:
    return AssessmentManager()
