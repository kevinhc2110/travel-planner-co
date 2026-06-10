from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository
from travel_planner_co.domain.services.scraper import ScraperService
from travel_planner_co.domain.services.text_chunker import TextChunker
from travel_planner_co.infrastructure.ai.embeddings.base import EmbeddingProvider
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore


class SyncAllSourcesUseCase:
    def __init__(
        self,
        scraper_service: ScraperService,
        destination_repository: DestinationRepository,
        text_chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: PGVectorStore,
    ):
        self.scraper_service = scraper_service
        self.destination_repository = destination_repository
        self.text_chunker = text_chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def execute(self) -> int:
        destinations: list[Destination] = await self.scraper_service.scrape_all()

        count = 0
        for dest in destinations:
            existing = await self.destination_repository.get_by_url(dest.url)
            if existing:
                dest.id = existing.id
                await self.destination_repository.update(dest)
                await self.destination_repository.delete_chunks(str(existing.id))
                dest_id = str(existing.id)
            else:
                dest_id = await self.destination_repository.save(dest)

            chunks = self.text_chunker.chunk(dest.content)
            if chunks:
                embeddings = await self.embedding_provider.embed_batch(chunks)
                for chunk_text, embedding in zip(chunks, embeddings, strict=True):
                    await self.vector_store.add(
                        destination_id=dest_id,
                        content=chunk_text,
                        embedding=embedding,
                        metadata={"source": dest.source, "title": dest.title, "url": dest.url},
                    )
            count += 1

        return count
