from unittest.mock import AsyncMock

import pytest

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.infrastructure.services.geo_enricher import GeoEnricher


class TestGeoEnricher:
    def test_clean_location_name_removes_prefix(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        assert enricher._clean_location_name("Centro histórico de Cartagena") == "Cartagena"
        assert enricher._clean_location_name("Parque Nacional Natural Tayrona") == "Tayrona"
        assert enricher._clean_location_name("Museo del Oro") == "Oro"

    def test_clean_location_name_splits_y(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        assert enricher._clean_location_name("Bogotá y alrededores") == "Bogotá"

    def test_clean_location_name_no_prefix(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        assert enricher._clean_location_name("Santa Marta") == "Santa Marta"

    def test_parse_json_extracts_braces(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        result = enricher._parse_json('{"city": "Bogotá"}')
        assert result == {"city": "Bogotá"}

    def test_parse_json_no_braces(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        assert enricher._parse_json("texto sin json") is None

    def test_parse_json_nested_braces(self):
        enricher = GeoEnricher.__new__(GeoEnricher)
        result = enricher._parse_json('{"data": {"inner": "value"}}')
        assert result == {"data": {"inner": "value"}}

    async def test_enrich_calls_llm_and_updates_destination(self):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(
            return_value='{"city": "Bogotá", "department": "Cundinamarca", "category": "urbano", "rating": 4.0, "estimated_days": 3, "best_season": "todo el año", "description": "Capital de Colombia", "tags": ["cultura"], "location_name": "Bogotá"}'
        )
        enricher = GeoEnricher(llm_provider=mock_llm)
        dest = Destination(name="Bogotá", source="Test", url="https://example.com")
        result = await enricher.enrich(dest)
        assert result.city == "Bogotá"
        assert result.department == "Cundinamarca"
        assert result.category == "urbano"
        assert result.rating == 4.0
        assert result.estimated_days == 3
        assert result.best_season == "todo el año"

    async def test_enrich_handles_malformed_response(self):
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="Respuesta sin JSON")
        enricher = GeoEnricher(llm_provider=mock_llm)
        dest = Destination(name="Test", source="Test", url="https://example.com")
        result = await enricher.enrich(dest)
        assert result.name == "Test"
        assert result.city is None

    async def test_geocode_location_calls_geocoder(self):
        mock_geocoder = AsyncMock()
        mock_geocoder.geocode = AsyncMock(return_value=(4.7110, -74.0721))
        enricher = GeoEnricher.__new__(GeoEnricher)
        enricher.geocoder = mock_geocoder
        enricher.llm_provider = AsyncMock()
        result = await enricher.geocode_location("Bogotá")
        assert result == (4.7110, -74.0721)
        mock_geocoder.geocode.assert_awaited_once_with("Bogotá")
