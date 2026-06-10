from abc import ABC, abstractmethod


class TextChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, max_chunk_size: int = 1000) -> list[str]:
        ...
