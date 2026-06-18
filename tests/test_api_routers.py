from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from travel_planner_co.api.routers.destinations_router import router as destinations_router
from travel_planner_co.api.routers.planner_router import router as planner_router


@pytest.fixture
def app(mock_destination_repo, mock_llm_provider, mock_plan_repo, mock_geo_enricher, mock_embedding_provider, mock_vector_store):
    app = FastAPI()
    app.include_router(destinations_router)
    app.include_router(planner_router)

    app.dependency_overrides = {}

    from travel_planner_co.api.dependencies import (
        get_destination_repository,
        get_sync_all_sources_use_case,
        get_update_destination_use_case,
        get_generate_plan_use_case,
    )
    from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
    from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
    from travel_planner_co.application.use_cases.generate_plan import GeneratePlanUseCase
    from unittest.mock import AsyncMock

    sync_uc = SyncAllSourcesUseCase(
        scraper_service=AsyncMock(),
        destination_repository=mock_destination_repo,
        text_chunker=AsyncMock(),
        embedding_provider=mock_embedding_provider,
        vector_store=mock_vector_store,
        geo_enricher=mock_geo_enricher,
    )
    sync_uc.execute = AsyncMock(return_value=5)

    update_uc = UpdateDestinationUseCase(
        scraper_service=AsyncMock(),
        destination_repository=mock_destination_repo,
        text_chunker=AsyncMock(),
        embedding_provider=mock_embedding_provider,
        vector_store=mock_vector_store,
        geo_enricher=mock_geo_enricher,
    )
    update_uc.execute = AsyncMock(return_value="Destino Actualizado")

    plan_uc = GeneratePlanUseCase(
        llm_provider=mock_llm_provider,
        destination_repository=mock_destination_repo,
        plan_repository=mock_plan_repo,
        geo_enricher=mock_geo_enricher,
        embedding_provider=mock_embedding_provider,
        vector_store=mock_vector_store,
    )
    from travel_planner_co.domain.entities.plan import Plan
    from datetime import datetime, timezone
    plan_uc.execute = AsyncMock(
        return_value=Plan(
            id="plan-123",
            location="Bogotá",
            days=3,
            preferences={},
            itinerary={"summary": "Plan generado", "daily_plans": []},
            created_at=datetime.now(timezone.utc),
        )
    )

    app.dependency_overrides[get_destination_repository] = lambda: mock_destination_repo
    app.dependency_overrides[get_sync_all_sources_use_case] = lambda: sync_uc
    app.dependency_overrides[get_update_destination_use_case] = lambda: update_uc
    app.dependency_overrides[get_generate_plan_use_case] = lambda: plan_uc

    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestDestinationsRouter:
    async def test_list_destinations_empty(self, client, mock_destination_repo):
        mock_destination_repo.list_all = AsyncMock(return_value=[])
        response = await client.get("/destinations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["destinations"] == []

    async def test_list_destinations(self, client, mock_destination_repo, sample_destination):
        mock_destination_repo.list_all = AsyncMock(return_value=[sample_destination])
        response = await client.get("/destinations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["destinations"][0]["name"] == "Parque Tayrona"

    async def test_sync_sources(self, client):
        response = await client.post("/destinations/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 5

    async def test_sync_sources_with_max_urls(self, client, app):
        response = await client.post("/destinations/sync?max_urls=3")
        assert response.status_code == 200

    async def test_update_destination_found(self, client):
        response = await client.post("/destinations/update", json={"url": "https://example.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["title"] == "Destino Actualizado"

    async def test_update_destination_not_found(self, client, app):
        from travel_planner_co.api.dependencies import get_update_destination_use_case
        from unittest.mock import AsyncMock

        update_uc = app.dependency_overrides[get_update_destination_use_case]()
        update_uc.execute = AsyncMock(return_value=None)

        response = await client.post("/destinations/update", json={"url": "https://example.com/bad"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"

    async def test_search_near(self, client, mock_destination_repo, sample_destination):
        mock_destination_repo.search_near = AsyncMock(return_value=[sample_destination])
        response = await client.post(
            "/destinations/near",
            json={"latitude": 4.7110, "longitude": -74.0721, "radius_km": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestPlannerRouter:
    async def test_generate_plan(self, client):
        response = await client.post(
            "/planner/generate-plan",
            json={"location": "Bogotá", "days": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == "plan-123"
        assert data["location"] == "Bogotá"
        assert data["days"] == 3

    async def test_generate_plan_with_preferences(self, client):
        response = await client.post(
            "/planner/generate-plan",
            json={
                "location": "Medellín",
                "days": 5,
                "categories": ["cultura"],
                "preferences": {"presupuesto": "bajo"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == ["cultura"]
        assert data["days"] == 3
