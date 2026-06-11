import asyncio
import time

import httpx


class NominatimGeocoder:
    def __init__(self, user_agent: str = "TravelPlannerCo/1.0"):
        self.user_agent = user_agent
        self._last_request = 0.0

    async def geocode(
        self, location: str, country: str = "Colombia"
    ) -> tuple[float, float] | None:
        now = time.monotonic()
        since_last = now - self._last_request
        if since_last < 1.0:
            await asyncio.sleep(1.0 - since_last)

        query = f"{location}, {country}" if country else location
        url = "https://nominatim.openstreetmap.org/search"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": self.user_agent},
                timeout=10,
            )
            self._last_request = time.monotonic()
            resp.raise_for_status()
            data = resp.json()
            if data:
                try:
                    return float(data[0]["lat"]), float(data[0]["lon"])
                except (KeyError, ValueError, TypeError, IndexError):
                    pass
        return None
