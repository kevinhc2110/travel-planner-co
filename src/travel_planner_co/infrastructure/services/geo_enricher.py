import json
import logging

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.infrastructure.ai.llm.base import LLMProvider

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
Del siguiente texto sobre un destino turístico en Colombia, extrae la información estructurada en JSON. 
Solo responde con el JSON, sin explicaciones.

Campos:
- "city": ciudad principal mencionada (en español, null si no se menciona)
- "department": departamento colombiano (null si no se menciona)
- "category": tipo de destino ("naturaleza", "cultura", "gastronomía", "aventura", "playa", "historia", "compras", "ecoturismo", "religioso", "urbano", null)
- "rating": calificación estimada de 1.0 a 5.0 basada en el tono del artículo (null si no se puede determinar)
- "estimated_days": número de días recomendados para visitar (entero, null si no se puede inferir)
- "best_season": mejor época para visitar en español (null si no se menciona)
- "latitude": latitud aproximada de la ciudad principal (número, null si no se puede determinar)
- "longitude": longitud aproximada (número, null si no se puede determinar)
- "description": resumen atractivo del destino en 1-2 oraciones (extraído del texto)
- "tags": lista de etiquetas relevantes relacionadas al destino (array de strings)

Texto:
{text}
"""


class GeoEnricher:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def enrich(self, destination: Destination) -> Destination:
        text = f"Título: {destination.name}\n\n{destination.full_content or ''}"
        try:
            response = await self.llm_provider.generate(
                prompt=EXTRACTION_PROMPT.format(text=text[:8000]),
                temperature=0.1,
            )
            data = self._parse_json(response)
            if data:
                destination.city = data.get("city") or destination.city
                destination.department = data.get("department") or destination.department
                destination.category = data.get("category") or destination.category
                destination.rating = data.get("rating") or destination.rating
                destination.estimated_days = data.get("estimated_days") or destination.estimated_days
                destination.best_season = data.get("best_season") or destination.best_season
                destination.latitude = data.get("latitude") or destination.latitude
                destination.longitude = data.get("longitude") or destination.longitude
                destination.description = data.get("description") or destination.description
                destination.tags = data.get("tags") or destination.tags
        except Exception:
            logger.exception("GeoEnricher failed for %s", destination.name)
        return destination

    async def geocode_city(self, city: str) -> tuple[float, float] | None:
        prompt = f"""Responde solo con JSON: la latitud y longitud aproximada de {city}, Colombia.
Formato: {{"latitude": número, "longitude": número}}"""
        try:
            response = await self.llm_provider.generate(prompt=prompt, temperature=0.1)
            data = self._parse_json(response)
            if data and data.get("latitude") and data.get("longitude"):
                return float(data["latitude"]), float(data["longitude"])
        except Exception:
            logger.warning("Geocoding failed for %s", city)
        return None

    @staticmethod
    def _parse_json(text: str) -> dict | None:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError):
            logger.warning("Could not parse Gemini response as JSON")
            return None
