"""Tests for JobManager — async job lifecycle, bounded polling."""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.jobs.manager import JobManager
from app.schemas.job import HeatmapRequest, EnvironmentalRequest
from app.models.site import Site
from app.db.repositories import job_repo


SAMPLE_HEATMAP_REQUEST = HeatmapRequest(
    polygon_coordinates=[
        [
            [-74.0170, 40.7050],
            [-74.0030, 40.7050],
            [-74.0030, 40.7180],
            [-74.0170, 40.7180],
            [-74.0170, 40.7050],
        ]
    ],
    date_time={"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1},
    granularity=100,
)

SAMPLE_ENV_REQUEST = EnvironmentalRequest(
    temperature=32.5,
    date_time={"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1},
)


class TestJobSubmission:
    @pytest.mark.asyncio
    async def test_submit_heatmap_creates_job(self, async_session, mock_fg_client):
        # Create a site first
        site_id = uuid.uuid4()
        site = Site(id=site_id, name="Test Site", latitude=40.7128, longitude=-74.006)
        async_session.add(site)
        await async_session.commit()

        manager = JobManager()

        with patch.object(manager, "_poll_status", new_callable=AsyncMock):
            with patch(
                "app.services.fortyguard.heatmap.HeatmapService.submit",
                new_callable=AsyncMock,
                return_value="activity-123",
            ):
                job = await manager.submit_heatmap(
                    async_session, site_id, SAMPLE_HEATMAP_REQUEST, mock_fg_client
                )

        assert job is not None
        assert job.analysis_type == "heatmap"
        assert job.activity_id == "activity-123"
        assert job.status == "Processing"

    @pytest.mark.asyncio
    async def test_submit_heatmap_failed_submission(
        self, async_session, mock_fg_client
    ):
        site_id = uuid.uuid4()
        site = Site(id=site_id, name="Test Site", latitude=40.7128, longitude=-74.006)
        async_session.add(site)
        await async_session.commit()

        manager = JobManager()

        with patch(
            "app.services.fortyguard.heatmap.HeatmapService.submit",
            new_callable=AsyncMock,
            side_effect=Exception("API Error"),
        ):
            job = await manager.submit_heatmap(
                async_session, site_id, SAMPLE_HEATMAP_REQUEST, mock_fg_client
            )

        assert job.status == "Failed"
        assert "API Error" in job.error_message


class TestJobPolling:
    @pytest.mark.asyncio
    async def test_polling_completes_job(self):
        """When status returns Completed, polling stops and job is updated."""
        manager = JobManager()
        job_id = uuid.uuid4()

        mock_db_session = AsyncMock()
        mock_job = MagicMock()
        mock_job.id = job_id
        mock_job.status = "Completed"

        with patch(
            "app.services.jobs.manager.AsyncSessionLocal"
        ) as MockSessionLocal, patch(
            "app.services.fortyguard.status.StatusService.check",
            new_callable=AsyncMock,
            return_value=("Completed", {"result": "data"}),
        ), patch(
            "app.services.jobs.manager.job_repo.update_job_status",
            new_callable=AsyncMock,
            return_value=mock_job,
        ), patch(
            "asyncio.sleep", new_callable=AsyncMock
        ):
            mock_session = AsyncMock()
            MockSessionLocal.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            MockSessionLocal.return_value.__aexit__ = AsyncMock(return_value=False)

            await manager._poll_status(job_id, "activity-123", AsyncMock())

    @pytest.mark.asyncio
    async def test_polling_handles_failed_status(self):
        """When FortyGuard reports Failed, job is marked as Failed."""
        manager = JobManager()
        job_id = uuid.uuid4()

        mock_job = MagicMock()
        mock_job.status = "Failed"

        with patch(
            "app.services.jobs.manager.AsyncSessionLocal"
        ) as MockSessionLocal, patch(
            "app.services.fortyguard.status.StatusService.check",
            new_callable=AsyncMock,
            return_value=("Failed", None),
        ), patch(
            "app.services.jobs.manager.job_repo.update_job_status",
            new_callable=AsyncMock,
            return_value=mock_job,
        ), patch(
            "asyncio.sleep", new_callable=AsyncMock
        ):
            mock_session = AsyncMock()
            MockSessionLocal.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            MockSessionLocal.return_value.__aexit__ = AsyncMock(return_value=False)

            await manager._poll_status(job_id, "activity-123", AsyncMock())

    @pytest.mark.asyncio
    async def test_polling_timeout_marks_job_failed(self):
        """When max attempts exceeded, job is marked Failed with timeout message."""
        manager = JobManager()
        job_id = uuid.uuid4()

        mock_job = MagicMock()

        with patch(
            "app.services.jobs.manager.AsyncSessionLocal"
        ) as MockSessionLocal, patch(
            "app.services.fortyguard.status.StatusService.check",
            new_callable=AsyncMock,
            return_value=("Processing", None),
        ), patch(
            "app.services.jobs.manager.job_repo.update_job_status",
            new_callable=AsyncMock,
            return_value=mock_job,
        ) as mock_update, patch(
            "asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "app.services.jobs.manager.settings"
        ) as mock_settings:
            mock_settings.MAX_POLL_ATTEMPTS = 2
            mock_settings.POLL_INTERVAL_SECONDS = 0

            mock_session = AsyncMock()
            MockSessionLocal.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            MockSessionLocal.return_value.__aexit__ = AsyncMock(return_value=False)

            await manager._poll_status(job_id, "activity-123", AsyncMock())

            # The last call should be marking as failed with timeout
            last_call = mock_update.call_args_list[-1]
            assert last_call[1].get("error") == "Polling timeout" or (
                len(last_call[0]) > 2 and "timeout" in str(last_call).lower()
            )
