import json

from travel_planner_co.domain.entities.plan import Plan
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository
from travel_planner_co.domain.repositories.plan_repository import PlanRepository
from travel_planner_co.domain.services.embedding_provider import EmbeddingProvider
from travel_planner_co.domain.services.llm_provider import LLMProvider
from travel_planner_co.infrastructure.constants import PLAN_PROMPT
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.services.geo_enricher import GeoEnricher

MIN_SPATIAL_RESULTS = 5


class GeneratePlanUseCase:
    def __init__(
        self,
        llm_provider: LLMProvider,
        destination_repository: DestinationRepository,
        plan_repository: PlanRepository,
        geo_enricher: GeoEnricher,
        embedding_provider: EmbeddingProvider,
        vector_store: PGVectorStore,
    ):
        self.llm_provider = llm_provider
        self.destination_repository = destination_repository
        self.plan_repository = plan_repository
        self.geo_enricher = geo_enricher
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def execute(
        self,
        location: str,
        days: int,
        categories: list[str] | None = None,
        preferences: dict | None = None,
    ) -> Plan:
        coords = await self.geo_enricher.geocode_location(location)

        if coords:
            lat, lng = coords
            near = await self.destination_repository.search_near(
                latitude=lat, longitude=lng, radius_km=100
            )
        else:
            near = []

        if categories:
            near = [d for d in near if d.category and d.category in categories]

        if len(near) < MIN_SPATIAL_RESULTS:
            query_text = f"Viaje a {location}"
            if preferences:
                query_text += f", interés en {json.dumps(preferences, ensure_ascii=False)}"
            if categories:
                query_text += f", categorías: {', '.join(categories)}"
            embedding = await self.embedding_provider.embed(query_text)
            chunks = await self.vector_store.search(embedding, top_k=10)
            seen_ids = {d.id for d in near if d.id}
            for chunk in chunks:
                if chunk.destination_id not in seen_ids:
                    dest = await self.destination_repository.get_by_id(chunk.destination_id)
                    if dest and categories:
                        if dest.category and dest.category in categories:
                            near.append(dest)
                            seen_ids.add(dest.id)
                    elif dest:
                        near.append(dest)
                        seen_ids.add(dest.id)

        dest_text = "\n\n".join(
            f"Nombre: {d.name}\n"
            f"Ubicación: {d.city or 'desconocida'}, {d.department or ''}"
            f"{' — ' + str(round(d.distance_km)) + ' km desde ' + location if d.distance_km is not None else ''}\n"
            f"Coordenadas: {d.latitude}, {d.longitude}\n"
            f"Categoría: {d.category}\n"
            f"Rating: {d.rating}\n"
            f"Días estimados: {d.estimated_days}\n"
            f"Mejor época: {d.best_season}\n"
            f"Descripción: {d.description or ''}"
            for d in near[:15]
        )

        if not dest_text:
            dest_text = "No se encontraron destinos cercanos. Sugiere al usuario explorar otras zonas."

        prefs_text = json.dumps(preferences, ensure_ascii=False) if preferences else "ninguna en particular"
        cats_text = ", ".join(categories) if categories else "todas"
        prompt = PLAN_PROMPT.format(
            location=location,
            days=days,
            preferences=prefs_text,
            categories=cats_text,
            destinations=dest_text,
        )

        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.7,
        )

        itinerary = self._parse_json(response) or {"error": "no se pudo generar el plan", "raw": response}

        plan_prefs = preferences or {}
        if categories:
            plan_prefs["categories"] = categories

        plan = Plan(
            location=location,
            days=days,
            preferences=plan_prefs,
            itinerary=itinerary,
        )
        plan.id = await self.plan_repository.save(plan)
        return plan

    @staticmethod
    def _parse_json(text: str) -> dict | None:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError):
            return None
