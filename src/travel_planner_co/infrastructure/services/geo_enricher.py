import json

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.services.llm_provider import LLMProvider
from travel_planner_co.infrastructure.constants import EXTRACTION_PROMPT
from travel_planner_co.infrastructure.services.geocoder import NominatimGeocoder


class GeoEnricher:
    def __init__(self, llm_provider: LLMProvider, geocoder: NominatimGeocoder | None = None):
        self.llm_provider = llm_provider
        self.geocoder = geocoder or NominatimGeocoder()

    async def enrich(self, destination: Destination) -> Destination:
        text = f"Título: {destination.name}\n\n{destination.full_content or ''}"[:8000]
        response = await self.llm_provider.generate(
            prompt=EXTRACTION_PROMPT.format(text=text),
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
                cleaned = self._clean_location_name(location_name)
                broader = cleaned.split(",", 1)[-1].strip() if "," in cleaned else None
                for attempt in (cleaned, broader, data.get("city"), data.get("department"), None):
                    if not attempt:
                        continue
                    try:
                        coords = await self.geocoder.geocode(attempt)
                    except Exception:
                        coords = None
                    if coords:
                        destination.latitude, destination.longitude = coords
                        break
        return destination

    async def geocode_location(self, location: str) -> tuple[float, float] | None:
        return await self.geocoder.geocode(location)

    @staticmethod
    def _clean_location_name(name: str) -> str:
        prefixes = [
            "Centro histórico de ", "Centro Histórico de ",
            "Reserva Natural ", "Parque Nacional Natural ", "Parque Natural ",
            "Parque Nacional ", "Santuario de Fauna y Flora ",
            "Área Natural Protegida ", "Monumento Nacional ",
            "Museo de ", "Museo del ", "Museo de los ", "Museos de ",
            "Mejores ", "Mejor ",
            "Cañón de ", "Cañón del ", "Cañón ",
            "Río ", "Cerro ", "Cascada ", "Laguna de ", "Volcán ",
        ]
        for p in prefixes:
            if name.startswith(p):
                name = name[len(p):]
                break
        if " y " in name:
            name = name.split(" y ")[0]
        return name.strip()

    @staticmethod
    def _parse_json(text: str) -> dict | None:
        try:
            start = text.index("{")
        except ValueError:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        return None
        return None
