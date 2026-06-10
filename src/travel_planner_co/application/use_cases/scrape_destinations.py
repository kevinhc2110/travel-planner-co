from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.services.scraper import ScraperService


class ScrapeDestinationsUseCase:
    def __init__(self, scraper_service: ScraperService):
        self.scraper_service = scraper_service

    async def execute(self) -> list[Destination]:
        return await self.scraper_service.scrape_all()
