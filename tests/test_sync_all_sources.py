from unittest.mock import AsyncMock

import pytest

from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.domain.entities.destination import Destination


class TestSyncAllSourcesUseCase:
    @pytest.fixture
    def use_case(self, mock_scraper_service, mock_destination_repo, mock_text_chunker, mock_embedding_provider, mock_vector_store, mock_geo_enricher):
        return SyncAllSourcesUseCase(
            scraper_service=mock_scraper_service,
            destination_repository=mock_destination_repo,
            text_chunker=mock_text_chunker,
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
            geo_enricher=mock_geo_enricher,
        )

    async def test_execute_returns_count(self, use_case):
        count = await use_case.execute()
        assert count == 1

    async def test_execute_zero_urls(self, use_case, mock_scraper_service):
        mock_scraper_service.discover_urls = AsyncMock(return_value=[])
        count = await use_case.execute()
        assert count == 0

    async def test_execute_respects_max_urls(self, use_case, mock_scraper_service):
        mock_scraper_service.discover_urls = AsyncMock(
            return_value=["url1", "url2", "url3"]
        )
        count = await use_case.execute(max_urls=1)
        assert count <= 1

    async def test_execute_skips_existing_urls(self, use_case, mock_destination_repo):
        mock_destination_repo.get_by_url = AsyncMock(
            side_effect=lambda url: (
                Destination(name="Existing", source="Test", url=url)
                if url == "https://example.com/test"
                else None
            )
        )
        mock_destination_repo.find_similar = AsyncMock(return_value=None)
        count = await use_case.execute()
        assert count == 0

    async def test_execute_skips_similar_destinations(self, use_case, mock_destination_repo, mock_geo_enricher):
        mock_geo_enricher.enrich = AsyncMock(
            side_effect=lambda d: Destination(
                name=d.name, full_content=d.full_content, source=d.source, url=d.url,
                latitude=4.0, longitude=-74.0,
            )
        )
        mock_destination_repo.find_similar = AsyncMock(return_value=Destination(name="Similar", source="Test", url="similar"))
        count = await use_case.execute()
        assert count == 0

    async def test_execute_handles_scrape_failure(self, use_case, mock_scraper_service):
        mock_scraper_service.scrape_url = AsyncMock(return_value=[])
        count = await use_case.execute()
        assert count == 0

    async def test_execute_calls_vector_store_for_each_chunk(self, use_case, mock_vector_store, mock_destination_repo):
        count = await use_case.execute()
        if count > 0:
            mock_vector_store.add.assert_called()
