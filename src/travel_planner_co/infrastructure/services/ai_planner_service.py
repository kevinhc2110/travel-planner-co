from travel_planner_co.domain.services.ai_planner_service import AIPlannerService as BaseAIPlannerService
from travel_planner_co.domain.services.search_service import SearchService
from travel_planner_co.infrastructure.ai.llm.base import LLMProvider
from travel_planner_co.infrastructure.constants import TRAVEL_PLANNER_CO_SYSTEM_PROMPT


class AIPlannerService(BaseAIPlannerService):
    def __init__(
        self,
        llm_provider: LLMProvider,
        search_service: SearchService,
    ):
        self.llm_provider = llm_provider
        self.search_service = search_service

    async def chat(
        self,
        query: str,
        conversation_id: str | None = None,
    ) -> str:
        context_chunks = await self.search_service.search(query, top_k=5)

        context = "\n\n".join(
            f"[{c.metadata.get('source', 'Desconocido') if c.metadata else 'Desconocido'}] {c.content}"
            for c in context_chunks
        )

        prompt = f"""Contexto de destinos turísticos:
{context}

Consulta del usuario: {query}

Basado en el contexto proporcionado, responde de manera útil y precisa sobre el destino solicitado."""

        response = await self.llm_provider.generate(
            prompt=prompt,
            system_instruction=TRAVEL_PLANNER_CO_SYSTEM_PROMPT,
        )

        return response
