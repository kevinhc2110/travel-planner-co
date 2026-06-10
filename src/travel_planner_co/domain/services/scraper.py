from abc import ABC, abstractmethod

from travel_planner_co.domain.entities.destination import Destination


class ScraperService(ABC):
    @abstractmethod
    async def scrape_all(self) -> list[Destination]:
        ...

    @abstractmethod
    async def scrape_url(self, url: str) -> list[Destination]:
        ...
