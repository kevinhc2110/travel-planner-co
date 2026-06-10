from abc import ABC, abstractmethod


class VectorStore(ABC):

    @abstractmethod
    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float]
    ):
        pass

    @abstractmethod
    async def search(
        self,
        embedding: list[float],
        top_k: int = 3
    ):
        pass