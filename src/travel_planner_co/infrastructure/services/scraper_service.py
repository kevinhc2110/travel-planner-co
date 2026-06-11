import logging

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.services.scraper import ScraperService as BaseScraperService
from travel_planner_co.infrastructure.scrapers.base import Scraper

logger = logging.getLogger(__name__)


class ScraperService(BaseScraperService):
    def __init__(self, scrapers: list[Scraper]):
        self.scrapers = scrapers

    async def discover_urls(self) -> list[str]:
        all_urls: list[str] = []
        for scraper in self.scrapers:
            urls = scraper.collect_article_urls()
            all_urls.extend(urls)
        return all_urls

    async def scrape_all(self) -> list[Destination]:
        destinations: list[Destination] = []
        for scraper in self.scrapers:
            urls = scraper.collect_article_urls()
            for url in urls:
                data = scraper.scrape_article(url)
                if data and data.get("title") and data.get("content"):
                    destinations.append(
                        Destination(
                            name=data["title"],
                            full_content=data["content"],
                            source=scraper.NAME,
                            url=url,
                        )
                    )
        return destinations

    async def scrape_url(self, url: str) -> list[Destination]:
        for scraper in self.scrapers:
            try:
                data = scraper.scrape_article(url)
                if data and data.get("title") and data.get("content"):
                    return [
                        Destination(
                            name=data["title"],
                            full_content=data["content"],
                            source=scraper.NAME,
                            url=url,
                        )
                    ]
            except Exception:
                logger.warning("Scraper %s failed for URL %s", scraper.NAME, url)
        return []
