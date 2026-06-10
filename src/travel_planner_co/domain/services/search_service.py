from abc import ABC, abstractmethod

from travel_planner_co.infrastructure.data.vectorstore.models import ChunkRecord


class SearchService(ABC):
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[ChunkRecord]:
        ...
