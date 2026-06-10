from abc import ABC, abstractmethod


class AIPlannerService(ABC):
    @abstractmethod
    async def chat(
        self,
        query: str,
        conversation_id: str | None = None,
    ) -> str:
        ...
