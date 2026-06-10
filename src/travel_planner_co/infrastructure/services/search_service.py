from travel_planner_co.domain.services.search_service import SearchService as BaseSearchService
from travel_planner_co.infrastructure.ai.embeddings.base import EmbeddingProvider
from travel_planner_co.infrastructure.data.vectorstore.models import ChunkRecord
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore


class SearchService(BaseSearchService):
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: PGVectorStore,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def search(self, query: str, top_k: int = 5) -> list[ChunkRecord]:
        embedding = await self.embedding_provider.embed(query)
        return await self.vector_store.search(embedding, top_k)
