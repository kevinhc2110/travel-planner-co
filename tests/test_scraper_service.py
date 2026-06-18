from unittest.mock import AsyncMock, MagicMock

import pytest

from travel_planner_co.infrastructure.services.scraper_service import ScraperService, _make_item_url


class TestMakeItemUrl:
    def test_generates_slug_from_name(self):
        url = _make_item_url("https://example.com", "Parque Tayrona", 0)
        assert "parque-tayrona" in url
        assert url.startswith("https://example.com#")

    def test_fallback_with_index(self):
        url = _make_item_url("https://example.com", "", 3)
        assert url == "https://example.com#item-3"

    def test_handles_special_characters(self):
        url = _make_item_url("https://example.com", "¡Caño Cristales!", 0)
        assert url == "https://example.com#ca-o-cristales"


class TestScraperService:
    async def test_discover_urls_aggregates_from_all_scrapers(self):
        mock_scraper1 = MagicMock()
        mock_scraper1.collect_article_urls.return_value = ["url1", "url2"]
        mock_scraper2 = MagicMock()
        mock_scraper2.collect_article_urls.return_value = ["url3"]

        service = ScraperService(scrapers=[mock_scraper1, mock_scraper2])
        result = await service.discover_urls()
        assert result == ["url1", "url2", "url3"]

    async def test_scrape_all_aggregates_from_all_scrapers(self):
        mock_scraper = MagicMock()
        mock_scraper.NAME = "Test"
        mock_scraper.collect_article_urls.return_value = ["http://example.com"]
        mock_scraper.scrape_article.return_value = {
            "title": "Destino Test",
            "content": "Contenido del destino",
        }

        service = ScraperService(scrapers=[mock_scraper])
        result = await service.scrape_all()
        assert len(result) == 1
        assert result[0].name == "Destino Test"
        assert result[0].source == "Test"

    async def test_scrape_all_skips_articles_without_content(self):
        mock_scraper = MagicMock()
        mock_scraper.NAME = "Test"
        mock_scraper.collect_article_urls.return_value = ["http://example.com"]
        mock_scraper.scrape_article.return_value = {}

        service = ScraperService(scrapers=[mock_scraper])
        result = await service.scrape_all()
        assert len(result) == 0

    async def test_scrape_url_finds_matching_scraper(self):
        mock_scraper = MagicMock()
        mock_scraper.NAME = "Test"
        mock_scraper.scrape_article.return_value = {
            "title": "Artículo",
            "content": "Contenido",
        }

        service = ScraperService(scrapers=[mock_scraper])
        result = await service.scrape_url("http://example.com")
        assert len(result) == 1
        assert result[0].name == "Artículo"

    async def test_scrape_url_returns_empty_when_no_scraper_succeeds(self):
        mock_scraper = MagicMock()
        mock_scraper.scrape_article.side_effect = Exception("Error")
        mock_scraper2 = MagicMock()
        mock_scraper2.scrape_article.return_value = {}

        service = ScraperService(scrapers=[mock_scraper, mock_scraper2])
        result = await service.scrape_url("http://example.com")
        assert result == []

    async def test_discover_urls_empty_when_no_scrapers(self):
        service = ScraperService(scrapers=[])
        result = await service.discover_urls()
        assert result == []
