import re

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.services.scraper import ScraperService as BaseScraperService
from travel_planner_co.infrastructure.scrapers.base import Scraper
from travel_planner_co.infrastructure.scrapers.list_splitter import split_list_article


def _make_item_url(base_url: str, item_name: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", item_name.lower()).strip("-")[:40]
    return f"{base_url}#{slug}" if slug else f"{base_url}#item-{index}"


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
                    items = split_list_article(data["title"], data["content"])
                    for i, item in enumerate(items):
                        destinations.append(
                            Destination(
                                name=item["title"],
                                full_content=item["content"],
                                source=scraper.NAME,
                                url=_make_item_url(url, item["title"], i),
                            )
                        )
        return destinations

    async def scrape_url(self, url: str) -> list[Destination]:
        for scraper in self.scrapers:
            try:
                data = scraper.scrape_article(url)
                if data and data.get("title") and data.get("content"):
                    items = split_list_article(data["title"], data["content"])
                    return [
                        Destination(
                            name=item["title"],
                            full_content=item["content"],
                            source=scraper.NAME,
                            url=_make_item_url(url, item["title"], i),
                        )
                        for i, item in enumerate(items)
                    ]
            except Exception:
                pass
        return []
