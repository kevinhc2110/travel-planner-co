from unittest.mock import AsyncMock

import pytest

from travel_planner_co.application.use_cases.generate_plan import GeneratePlanUseCase
from travel_planner_co.domain.entities.destination import Destination


class TestGeneratePlanUseCase:
    @pytest.fixture
    def use_case(self, mock_llm_provider, mock_destination_repo, mock_plan_repo, mock_geo_enricher, mock_embedding_provider, mock_vector_store):
        return GeneratePlanUseCase(
            llm_provider=mock_llm_provider,
            destination_repository=mock_destination_repo,
            plan_repository=mock_plan_repo,
            geo_enricher=mock_geo_enricher,
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

    async def test_execute_returns_plan(self, use_case, mock_llm_provider):
        mock_llm_provider.generate = AsyncMock(
            return_value='{"summary": "Plan de viaje", "daily_plans": []}'
        )
        plan = await use_case.execute(location="Bogotá", days=3)
        assert plan.location == "Bogotá"
        assert plan.days == 3
        assert plan.itinerary is not None
        assert plan.itinerary["summary"] == "Plan de viaje"
        assert plan.id is not None

    async def test_execute_with_categories_and_preferences(self, use_case, mock_llm_provider):
        mock_llm_provider.generate = AsyncMock(
            return_value='{"summary": "Plan cultural", "daily_plans": []}'
        )
        plan = await use_case.execute(
            location="Medellín",
            days=5,
            categories=["cultura", "gastronomía"],
            preferences={"presupuesto": "medio"},
        )
        assert plan.preferences == {"presupuesto": "medio", "categories": ["cultura", "gastronomía"]}

    async def test_execute_with_nearby_destinations(self, use_case, mock_destination_repo, mock_llm_provider):
        mock_llm_provider.generate = AsyncMock(
            return_value='{"summary": "Plan con destinos", "daily_plans": []}'
        )
        mock_destination_repo.search_near = AsyncMock(
            return_value=[
                Destination(
                    name="Destino Cercano",
                    city="Ciudad",
                    category="naturaleza",
                    latitude=4.7,
                    longitude=-74.0,
                    distance_km=10.0,
                    source="Test",
                    url="https://example.com",
                )
            ]
        )
        plan = await use_case.execute(location="Bogotá", days=2)
        assert plan.itinerary["summary"] == "Plan con destinos"

    async def test_execute_falls_back_to_vector_search(self, use_case, mock_destination_repo, mock_vector_store, mock_llm_provider):
        mock_llm_provider.generate = AsyncMock(
            return_value='{"summary": "Fallback search", "daily_plans": []}'
        )
        mock_destination_repo.search_near = AsyncMock(return_value=[])
        from travel_planner_co.infrastructure.data.vectorstore.models import ChunkRecord
        mock_vector_store.search = AsyncMock(
            return_value=[
                ChunkRecord(
                    id="chunk-1",
                    destination_id="dest-1",
                    content="Contenido del chunk",
                )
            ]
        )
        mock_destination_repo.get_by_id = AsyncMock(
            return_value=Destination(
                name="Destino Vector",
                city="Ciudad",
                category="naturaleza",
                source="Test",
                url="https://example.com",
            )
        )
        plan = await use_case.execute(location="Bogotá", days=3)
        assert plan.location == "Bogotá"
        mock_destination_repo.get_by_id.assert_awaited_once()

    async def test_execute_no_coordinates(self, use_case, mock_geo_enricher, mock_llm_provider):
        mock_llm_provider.generate = AsyncMock(
            return_value='{"summary": "Sin coordenadas", "daily_plans": []}'
        )
        mock_geo_enricher.geocode_location = AsyncMock(return_value=None)
        plan = await use_case.execute(location="Lugar desconocido", days=1)
        assert plan is not None

    async def test_parse_json_valid(self):
        result = GeneratePlanUseCase._parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_invalid(self):
        result = GeneratePlanUseCase._parse_json("not json")
        assert result is None

    def test_parse_json_extracts_from_text(self):
        result = GeneratePlanUseCase._parse_json(
            "Some text before {\"key\": \"value\"} and after"
        )
        assert result == {"key": "value"}
