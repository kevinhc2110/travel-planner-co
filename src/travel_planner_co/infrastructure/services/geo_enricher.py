import json

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.infrastructure.ai.llm.base import LLMProvider
from travel_planner_co.infrastructure.constants import EXTRACTION_PROMPT
from travel_planner_co.infrastructure.services.geocoder import NominatimGeocoder


class GeoEnricher:
    def __init__(self, llm_provider: LLMProvider, geocoder: NominatimGeocoder | None = None):
        self.llm_provider = llm_provider
        self.geocoder = geocoder or NominatimGeocoder()

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
                destination.description = data.get("description") or destination.description
                destination.tags = data.get("tags") or destination.tags

                location_name = data.get("location_name")
                if location_name and not (destination.latitude and destination.longitude):
                    coords = await self.geocoder.geocode(location_name)
                    if coords:
                        destination.latitude, destination.longitude = coords
        except Exception:
            pass
        return destination

    async def geocode_location(self, location: str) -> tuple[float, float] | None:
        return await self.geocoder.geocode(location)

    @staticmethod
    def _parse_json(text: str) -> dict | None:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError):
            return None
