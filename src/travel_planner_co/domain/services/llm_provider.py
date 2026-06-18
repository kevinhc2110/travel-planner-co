from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class LLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        ...

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:
        ...
