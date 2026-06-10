from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class Scraper(ABC):
    NAME: str = ""
    SITE_URL: str = ""

    def __init__(self, session: requests.Session | None = None):
        self.session = session or self._default_session()

    @abstractmethod
    def collect_article_urls(self) -> list[str]:
        ...

    @abstractmethod
    def scrape_article(self, url: str) -> dict:
        ...

    @staticmethod
    def clean_content(container: BeautifulSoup) -> str:
        for tag in container.select(
            "a, figure, img, picture, source, figcaption, iframe"
        ):
            tag.decompose()
        blocks = []
        for element in container.select("h2, h3, h4, p, li"):
            text = element.get_text(" ", strip=True)
            if len(text) >= 3:
                blocks.append(text)
        return "\n\n".join(blocks)

    @staticmethod
    def extract_links(
        soup: BeautifulSoup, selector: str, prefix: str = ""
    ) -> list[str]:
        links: set[str] = set()
        for item in soup.select(selector):
            href = item.get("href", "").strip()
            if href:
                links.add(prefix + href)
        return list(links)

    @staticmethod
    def _default_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        })
        return session
