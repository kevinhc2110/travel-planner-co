from unittest.mock import AsyncMock

import pytest

from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.domain.entities.destination import Destination


class TestUpdateDestinationUseCase:
    @pytest.fixture
    def use_case(self, mock_scraper_service, mock_destination_repo, mock_text_chunker, mock_embedding_provider, mock_vector_store, mock_geo_enricher):
        return UpdateDestinationUseCase(
            scraper_service=mock_scraper_service,
            destination_repository=mock_destination_repo,
            text_chunker=mock_text_chunker,
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
            geo_enricher=mock_geo_enricher,
        )

    async def test_execute_returns_name(self, use_case):
        result = await use_case.execute(url="https://example.com/test")
        assert result == "Destino Test"

    async def test_execute_returns_none_when_scrape_fails(self, use_case, mock_scraper_service):
        mock_scraper_service.scrape_url = AsyncMock(return_value=[])
        result = await use_case.execute(url="https://example.com/bad")
        assert result is None

    async def test_execute_updates_existing_destination(self, use_case, mock_destination_repo):
        existing = Destination(
            id="existing-id",
            name="Existing",
            source="Test",
            url="https://example.com/test",
        )
        mock_destination_repo.get_by_url = AsyncMock(return_value=existing)

        result = await use_case.execute(url="https://example.com/test")
        assert result == "Destino Test"
        mock_destination_repo.update.assert_awaited_once()
        mock_destination_repo.delete_chunks.assert_awaited_once_with("existing-id")

    async def test_execute_saves_new_destination(self, use_case, mock_destination_repo):
        mock_destination_repo.get_by_url = AsyncMock(return_value=None)
        result = await use_case.execute(url="https://example.com/test")
        assert result == "Destino Test"
        mock_destination_repo.save.assert_awaited_once()
        mock_destination_repo.update.assert_not_called()

    async def test_execute_generates_embeddings_and_stores(self, use_case, mock_vector_store):
        await use_case.execute(url="https://example.com/test")
        assert mock_vector_store.add.await_count >= 1
