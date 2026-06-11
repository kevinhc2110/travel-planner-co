from dataclasses import dataclass
from datetime import datetime


@dataclass
class Destination:
    name: str
    description: str | None = None
    full_content: str | None = None
    source: str = ""
    url: str = ""
    city: str | None = None
    department: str | None = None
    country: str = "Colombia"
    category: str | None = None
    rating: float | None = None
    estimated_days: int | None = None
    best_season: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] | None = None
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
