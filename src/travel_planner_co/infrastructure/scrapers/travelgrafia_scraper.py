from .base import Scraper
from ..http.fetch import fetch_html


class Travelgrafia(Scraper):
    NAME = "Travelgrafia"
    SITE_URL = "https://www.travelgrafia.co/"
    CATEGORY_URL = "https://www.travelgrafia.co/blog/category/colombia/"

    def collect_article_urls(self) -> list[str]:
        all_links: set[str] = set()
        for listing_url in self._get_listing_urls():
            soup = fetch_html(self.session, listing_url)
            if not soup:
                continue
            for link in self.extract_links(
                soup, "[data-elementor-type='loop-item'] h2 a"
            ):
                if "/blog/" in link:
                    all_links.add(link)
        return list(all_links)

    def scrape_article(self, url: str) -> dict:
        soup = fetch_html(self.session, url)
        if not soup:
            return {}

        title_el = soup.select_one("h1")
        if not title_el:
            return {}

        container = soup.select_one(".elementor-widget-theme-post-content")
        if not container:
            return {}

        content = self.clean_content(container)
        return {"title": title_el.get_text(" ", strip=True), "content": content}

    def _get_max_page(self) -> int:
        soup = fetch_html(self.session, self.CATEGORY_URL)
        if not soup:
            return 1
        anchor = soup.select_one(".e-load-more-anchor")
        if not anchor:
            return 1
        try:
            return int(anchor.get("data-max-page", 1))
        except Exception:
            return 1

    def _get_listing_urls(self) -> list[str]:
        max_page = self._get_max_page()
        if max_page <= 1:
            return [self.CATEGORY_URL]
        return [
            self.CATEGORY_URL if page == 1 else f"{self.CATEGORY_URL}page/{page}/"
            for page in range(1, max_page + 1)
        ]
