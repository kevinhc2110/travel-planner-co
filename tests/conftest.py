from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.entities.plan import Plan
from travel_planner_co.domain.entities.chunk import Chunk


@pytest.fixture
def sample_destination():
    return Destination(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Parque Tayrona",
        description="Hermoso parque natural en la costa Caribe",
        full_content="Parque Tayrona es uno de los destinos más populares de Colombia...",
        source="Travelgrafia",
        url="https://travelgrafia.co/parque-tayrona",
        city="Santa Marta",
        department="Magdalena",
        country="Colombia",
        category="naturaleza",
        rating=4.5,
        estimated_days=3,
        best_season="diciembre a marzo",
        latitude=11.3100,
        longitude=-74.0800,
        tags=["playa", "naturaleza", "senderismo"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_plan():
    return Plan(
        id="660e8400-e29b-41d4-a716-446655440001",
        location="Bogotá",
        days=3,
        preferences={"intereses": "cultura"},
        itinerary={
            "summary": "Plan cultural por Bogotá",
            "daily_plans": [
                {
                    "day": 1,
                    "title": "Centro histórico",
                    "activities": [
                        {
                            "time": "09:00",
                            "activity": "Visita al Museo del Oro",
                            "destination": "Museo del Oro",
                            "duration_hours": 3,
                            "notes": "Llegar temprano",
                        }
                    ],
                }
            ],
        },
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_chunk():
    return Chunk(
        content="Parque Tayrona es un destino increíble...",
        destination_id="550e8400-e29b-41d4-a716-446655440000",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "Travelgrafia", "name": "Parque Tayrona"},
    )


@pytest.fixture
def mock_llm_provider():
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value='{"test": "response"}')
    mock.stream_generate = AsyncMock()
    return mock


@pytest.fixture
def mock_embedding_provider():
    mock = AsyncMock()
    mock.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    mock.embed_batch = AsyncMock(
        return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    )
    return mock


@pytest.fixture
def mock_destination_repo():
    mock = AsyncMock()
    mock.save = AsyncMock(return_value="550e8400-e29b-41d4-a716-446655440000")
    mock.update = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_by_url = AsyncMock(return_value=None)
    mock.list_all = AsyncMock(return_value=[])
    mock.search_near = AsyncMock(return_value=[])
    mock.find_similar = AsyncMock(return_value=None)
    mock.delete_chunks = AsyncMock()
    return mock


@pytest.fixture
def mock_plan_repo():
    mock = AsyncMock()
    mock.save = AsyncMock(return_value="660e8400-e29b-41d4-a716-446655440001")
    return mock


@pytest.fixture
def mock_vector_store():
    mock = AsyncMock()
    mock.add = AsyncMock()
    mock.search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_geo_enricher():
    mock = AsyncMock()
    mock.enrich = AsyncMock(
        side_effect=lambda dest: dest
    )
    mock.geocode_location = AsyncMock(return_value=(4.7110, -74.0721))
    return mock


@pytest.fixture
def mock_scraper_service():
    mock = AsyncMock()
    mock.discover_urls = AsyncMock(
        return_value=["https://example.com/articulo-1"]
    )
    mock.scrape_all = AsyncMock(
        return_value=[
            Destination(name="Destino 1", full_content="Contenido 1", source="Test", url="https://example.com/1"),
        ]
    )
    mock.scrape_url = AsyncMock(
        return_value=[
            Destination(name="Destino Test", full_content="Contenido de prueba", source="Test", url="https://example.com/test"),
        ]
    )
    return mock


@pytest.fixture
def mock_text_chunker():
    mock = MagicMock()
    mock.chunk = MagicMock(
        return_value=["Chunk 1 de contenido", "Chunk 2 de contenido"]
    )
    return mock


@pytest.fixture
def mock_database():
    mock = AsyncMock()
    mock.execute = AsyncMock()
    mock.fetch = AsyncMock(return_value=[])
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    return mock
