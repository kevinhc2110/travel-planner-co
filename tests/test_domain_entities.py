from datetime import datetime

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.entities.plan import Plan
from travel_planner_co.domain.entities.chunk import Chunk


class TestDestination:
    def test_create_destination(self):
        dest = Destination(name="Cartagena", source="Test", url="https://example.com")
        assert dest.name == "Cartagena"
        assert dest.country == "Colombia"
        assert dest.source == "Test"
        assert dest.url == "https://example.com"

    def test_destination_with_all_fields(self, sample_destination):
        assert sample_destination.id is not None
        assert sample_destination.rating == 4.5
        assert sample_destination.latitude == 11.3100
        assert sample_destination.tags == ["playa", "naturaleza", "senderismo"]

    def test_destination_defaults(self):
        dest = Destination(name="Test")
        assert dest.description is None
        assert dest.country == "Colombia"
        assert dest.rating is None
        assert dest.tags is None


class TestPlan:
    def test_create_plan(self):
        plan = Plan(location="Medellín", days=5)
        assert plan.location == "Medellín"
        assert plan.days == 5
        assert plan.preferences is None
        assert plan.itinerary is None

    def test_plan_with_itinerary(self, sample_plan):
        assert sample_plan.itinerary is not None
        assert sample_plan.itinerary["summary"] == "Plan cultural por Bogotá"
        assert len(sample_plan.itinerary["daily_plans"]) == 1

    def test_plan_defaults(self):
        plan = Plan(location="Cali", days=2)
        assert plan.id is None
        assert plan.created_at is None


class TestChunk:
    def test_create_chunk(self):
        chunk = Chunk(content="test content", destination_id="abc-123")
        assert chunk.content == "test content"
        assert chunk.destination_id == "abc-123"

    def test_chunk_with_embedding(self, sample_chunk):
        assert sample_chunk.embedding == [0.1, 0.2, 0.3]
        assert sample_chunk.metadata == {"source": "Travelgrafia", "name": "Parque Tayrona"}
