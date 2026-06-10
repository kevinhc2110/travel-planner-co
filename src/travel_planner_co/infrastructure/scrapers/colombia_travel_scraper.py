from .base import Scraper
from ..http.fetch import fetch_html


class ColombiaTravel(Scraper):
    NAME = "Colombia Travel"
    SITE_URL = "https://www.colombia.travel"
    CATEGORY_URL = "https://colombia.travel/es/donde-ir/"

    def collect_article_urls(self) -> list[str]:
        region_urls = self._get_region_urls()
        if not region_urls:
            return []
        city_urls = self._get_city_urls(region_urls)
        if not city_urls:
            return []
        return self._get_article_urls(city_urls)

    def scrape_article(self, url: str) -> dict:
        soup = fetch_html(self.session, url)
        if not soup:
            return {}

        title_el = soup.select_one(".off-canvas-content field-content h1")
        if not title_el:
            return {}

        container = soup.select_one(".off-canvas-content field-item")
        if not container:
            return {}

        content = self.clean_content(container)
        return {"title": title_el.get_text(" ", strip=True), "content": content}

    def _get_region_urls(self) -> list[str]:
        soup = fetch_html(self.session, self.CATEGORY_URL)
        if not soup:
            return []
        return self.extract_links(soup, ".views-view-grid .verMas a", self.SITE_URL)

    def _get_city_urls(self, urls: list[str]) -> list[str]:
        all_links: set[str] = set()
        for url in urls:
            soup = fetch_html(self.session, url)
            if not soup:
                continue
            for link in self.extract_links(soup, ".content-list a", self.SITE_URL):
                all_links.add(link)
        return list(all_links)

    def _get_article_urls(self, urls: list[str]) -> list[str]:
        all_links: set[str] = set()
        for url in urls:
            soup = fetch_html(self.session, url)
            if not soup:
                continue
            links = self.extract_links(soup, ".destinos-home a", self.SITE_URL)
            if links:
                all_links.add(links[0])
        return list(all_links)
