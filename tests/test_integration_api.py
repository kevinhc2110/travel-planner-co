"""Integration tests for the API endpoints.

These tests use FastAPI TestClient with overridden dependencies,
testing the full request-response cycle including validation.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from travel_planner_co.api.routers.destinations_router import router as destinations_router
from travel_planner_co.api.routers.planner_router import router as planner_router
from travel_planner_co.api.routers.jobs_router import router as jobs_router
from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.entities.plan import Plan


@pytest.fixture
def integration_app():
    app = FastAPI()
    app.include_router(destinations_router)
    app.include_router(planner_router)
    app.include_router(jobs_router)

    mock_repo = AsyncMock()
    mock_repo.list_all = AsyncMock(
        return_value=[
            Destination(
                id="dest-1",
                name="Parque Tayrona",
                description="Parque natural en Santa Marta",
                full_content="Contenido completo...",
                source="Travelgrafia",
                url="https://travelgrafia.co/tayrona",
                city="Santa Marta",
                department="Magdalena",
                category="naturaleza",
                rating=4.5,
                estimated_days=3,
                best_season="diciembre a marzo",
                latitude=11.3100,
                longitude=-74.0800,
                tags=["playa", "senderismo"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            Destination(
                id="dest-2",
                name="Museo del Oro",
                description="Museo de orfebrería precolombina",
                full_content="Contenido del museo...",
                source="Travelgrafia",
                url="https://travelgrafia.co/oro",
                city="Bogotá",
                department="Cundinamarca",
                category="cultura",
                rating=4.8,
                estimated_days=1,
                best_season="todo el año",
                latitude=4.6019,
                longitude=-74.0721,
                tags=["cultura", "historia"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
    )
    mock_repo.search_near = AsyncMock(return_value=[])
    mock_repo.get_by_id = AsyncMock(
        return_value=Destination(
            id="dest-1",
            name="Parque Tayrona",
            source="Test",
            url="https://example.com",
        )
    )

    mock_plan_uc = AsyncMock()
    mock_plan_uc.execute = AsyncMock(
        return_value=Plan(
            id="plan-int-1",
            location="Cartagena",
            days=4,
            preferences={"intereses": "playa"},
            itinerary={
                "summary": "Plan de playa en Cartagena",
                "daily_plans": [
                    {
                        "day": 1,
                        "title": "Llegada a Cartagena",
                        "activities": [
                            {
                                "time": "10:00",
                                "activity": "Recorrido por el Centro Histórico",
                                "destination": "Centro Histórico",
                                "duration_hours": 3,
                                "notes": "Caminar por las calles coloniales",
                            }
                        ],
                    }
                ],
                "total_cost_estimate": "COP 1.500.000 - 2.000.000",
                "recommendations": ["Llevar bloqueador solar", "Usar zapatos cómodos"],
            },
            created_at=datetime.now(timezone.utc),
        )
    )

    mock_sync_uc = AsyncMock()
    mock_sync_uc.execute = AsyncMock(return_value=3)

    mock_update_uc = AsyncMock()
    mock_update_uc.execute = AsyncMock(return_value="Destino Actualizado")

    mock_redis = AsyncMock()
    mock_job = AsyncMock()
    mock_job.id = "job-123"
    mock_redis.enqueue_job = AsyncMock(return_value=mock_job)

    mock_job_info = AsyncMock()
    mock_job_info.info = AsyncMock()

    from unittest.mock import MagicMock

    mock_job_cls = MagicMock()
    mock_job_instance = AsyncMock()
    mock_job_instance.info = AsyncMock(
        return_value=MagicMock(
            start_time=datetime.now(timezone.utc),
            finish_time=datetime.now(timezone.utc),
            success=True,
            result={"count": 3},
            error=None,
        )
    )
    mock_job_cls.return_value = mock_job_instance

    app.state.db = AsyncMock()
    app.state.redis = mock_redis

    from travel_planner_co.api.dependencies import (
        get_destination_repository,
        get_generate_plan_use_case,
        get_sync_all_sources_use_case,
        get_update_destination_use_case,
        get_redis_pool,
    )

    app.dependency_overrides[get_destination_repository] = lambda: mock_repo
    app.dependency_overrides[get_generate_plan_use_case] = lambda: mock_plan_uc
    app.dependency_overrides[get_sync_all_sources_use_case] = lambda: mock_sync_uc
    app.dependency_overrides[get_update_destination_use_case] = lambda: mock_update_uc
    app.dependency_overrides[get_redis_pool] = lambda: mock_redis

    return app, mock_repo, mock_plan_uc, mock_sync_uc, mock_update_uc, mock_redis


@pytest.fixture
async def integration_client(integration_app):
    app = integration_app[0]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, integration_app


class TestIntegrationDestinations:
    async def test_list_all_destinations(self, integration_client):
        client, (app, mock_repo, *_) = integration_client
        response = await client.get("/destinations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [d["name"] for d in data["destinations"]]
        assert "Parque Tayrona" in names
        assert "Museo del Oro" in names

    async def test_full_sync_flow(self, integration_client):
        client, (app, mock_repo, mock_plan_uc, mock_sync_uc, *_) = integration_client
        response = await client.post("/destinations/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 3
        mock_sync_uc.execute.assert_awaited_once()

    async def test_update_destination(self, integration_client):
        client, (app, *_, mock_update_uc, _) = integration_client
        response = await client.post(
            "/destinations/update",
            json={"url": "https://travelgrafia.co/nuevo-destino"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["title"] == "Destino Actualizado"

    async def test_near_search(self, integration_client):
        client, (app, mock_repo, *_) = integration_client
        response = await client.post(
            "/destinations/near",
            json={"latitude": 4.7110, "longitude": -74.0721, "radius_km": 50},
        )
        assert response.status_code == 200
        data = response.json()
        mock_repo.search_near.assert_awaited_once()


class TestIntegrationPlanner:
    async def test_generate_plan_full_response(self, integration_client):
        client, (app, mock_repo, mock_plan_uc, *_) = integration_client
        response = await client.post(
            "/planner/generate-plan",
            json={"location": "Cartagena", "days": 4, "categories": ["playa"], "preferences": {"intereses": "playa"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == "plan-int-1"
        assert data["location"] == "Cartagena"
        assert data["days"] == 4
        assert data["categories"] == ["playa"]
        assert "summary" in data["itinerary"]
        assert "daily_plans" in data["itinerary"]
        assert len(data["itinerary"]["daily_plans"]) == 1

    async def test_generate_plan_validation_error(self, integration_client):
        client = integration_client[0]
        response = await client.post(
            "/planner/generate-plan",
            json={"location": "Bogotá"},
        )
        assert response.status_code == 422

    async def test_generate_plan_minimal_request(self, integration_client):
        client, (app, mock_repo, mock_plan_uc, *_) = integration_client
        response = await client.post(
            "/planner/generate-plan",
            json={"location": "Bogotá", "days": 1},
        )
        assert response.status_code == 200


class TestIntegrationJobs:
    async def test_enqueue_sync_job(self, integration_client):
        client, (app, *_, mock_redis) = integration_client
        response = await client.post("/jobs/sync")
        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "job-123"
        assert data["status"] == "queued"
        mock_redis.enqueue_job.assert_awaited_once_with("sync_all_sources_worker")

    async def test_enqueue_update_job(self, integration_client):
        client, (app, *_, mock_redis) = integration_client
        response = await client.post(
            "/jobs/update",
            json={"url": "https://example.com/destino"},
        )
        assert response.status_code == 202
        data = response.json()
        mock_redis.enqueue_job.assert_awaited_with("update_destination_worker", url="https://example.com/destino")

    async def test_get_job_status_not_found(self, integration_client):
        client, (app, *_, mock_redis) = integration_client
        from arq.jobs import Job
        original_job_init = Job.__init__
        Job.__init__ = lambda self, job_id, redis: setattr(self, '_redis', AsyncMock()) or setattr(self, 'job_id', job_id) or None
        Job.info = AsyncMock(return_value=None)
        try:
            response = await client.get("/jobs/non-existent-job")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_found"
        finally:
            Job.__init__ = original_job_init

    async def test_get_job_status_complete(self, integration_client):
        client = integration_client[0]
        from arq.jobs import Job
        from unittest.mock import MagicMock
        original_job_init = Job.__init__
        Job.__init__ = lambda self, job_id, redis: setattr(self, '_redis', AsyncMock()) or setattr(self, 'job_id', job_id) or None
        mock_info = MagicMock()
        mock_info.start_time = datetime.now(timezone.utc)
        mock_info.finish_time = datetime.now(timezone.utc)
        mock_info.success = True
        mock_info.result = {"count": 3}
        mock_info.error = None
        Job.info = AsyncMock(return_value=mock_info)
        try:
            response = await client.get("/jobs/some-job-id")
            assert response.status_code == 200
        finally:
            Job.__init__ = original_job_init

    async def test_validation_near_search(self, integration_client):
        client = integration_client[0]
        response = await client.post(
            "/destinations/near",
            json={"latitude": "invalid", "longitude": -74.0721},
        )
        assert response.status_code == 422
