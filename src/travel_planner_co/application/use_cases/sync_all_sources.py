from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository
from travel_planner_co.domain.services.scraper import ScraperService
from travel_planner_co.domain.services.text_chunker import TextChunker
from travel_planner_co.infrastructure.ai.embeddings.base import EmbeddingProvider
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.services.geo_enricher import GeoEnricher


class SyncAllSourcesUseCase:
    def __init__(
        self,
        scraper_service: ScraperService,
        destination_repository: DestinationRepository,
        text_chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: PGVectorStore,
        geo_enricher: GeoEnricher,
    ):
        self.scraper_service = scraper_service
        self.destination_repository = destination_repository
        self.text_chunker = text_chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.geo_enricher = geo_enricher

    async def execute(self) -> int:
        all_urls = await self.scraper_service.discover_urls()

        existing_urls: set[str] = set()
        for url in all_urls:
            existing = await self.destination_repository.get_by_url(url)
            if existing:
                existing_urls.add(url)

        new_urls = [u for u in all_urls if u not in existing_urls]

        if not new_urls:
            return 0

        count = 0
        for url in new_urls:
            raw_list = await self.scraper_service.scrape_url(url)
            if not raw_list:
                continue

            for raw in raw_list:
                dest = Destination(
                    name=raw.name,
                    full_content=raw.full_content,
                    source=raw.source,
                    url=raw.url,
                )
                dest = await self.geo_enricher.enrich(dest)
                dest_id = await self.destination_repository.save(dest)

                chunks = self.text_chunker.chunk(dest.full_content or "")
                if chunks:
                    embeddings = await self.embedding_provider.embed_batch(chunks)
                    for chunk_text, embedding in zip(chunks, embeddings):
                        await self.vector_store.add(
                            destination_id=dest_id,
                            content=chunk_text,
                            embedding=embedding,
                            metadata={
                                "source": dest.source,
                                "name": dest.name,
                                "url": dest.url,
                                "city": dest.city,
                                "category": dest.category,
                            },
                        )
                count += 1

        return count
