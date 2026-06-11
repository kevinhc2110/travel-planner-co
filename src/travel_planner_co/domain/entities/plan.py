from dataclasses import dataclass
from datetime import datetime


@dataclass
class Plan:
    city: str
    days: int
    preferences: dict | None = None
    itinerary: dict | None = None
    id: str | None = None
    created_at: datetime | None = None
