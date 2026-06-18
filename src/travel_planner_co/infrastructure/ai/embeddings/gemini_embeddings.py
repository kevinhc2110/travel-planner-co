import anyio
from google import genai

from travel_planner_co.domain.services.embedding_provider import EmbeddingProvider


class GeminiEmbeddings(
    EmbeddingProvider
):

    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    async def embed(self, text: str) -> list[float]:
        response = await anyio.to_thread.run_sync(
            lambda: self.client.models.embed_content(
                model=self.model,
                contents=text,
            )
        )

        return response.embeddings[0].values
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = await anyio.to_thread.run_sync(
            lambda: self.client.models.embed_content(
                model=self.model,
                contents=texts,
            )
        )

        return [e.values for e in response.embeddings]