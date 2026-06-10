from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.services.scraper import ScraperService as BaseScraperService
from travel_planner_co.infrastructure.scrapers.base import Scraper


class ScraperService(BaseScraperService):
    def __init__(self, scrapers: list[Scraper]):
        self.scrapers = scrapers

    async def scrape_all(self) -> list[Destination]:
        destinations: list[Destination] = []
        for scraper in self.scrapers:
            urls = scraper.collect_article_urls()
            for url in urls:
                data = scraper.scrape_article(url)
                if data and data.get("title") and data.get("content"):
                    destinations.append(
                        Destination(
                            title=data["title"],
                            content=data["content"],
                            source=scraper.NAME,
                            url=url,
                        )
                    )
        return destinations
