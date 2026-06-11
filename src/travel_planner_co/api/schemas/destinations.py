from datetime import datetime

from pydantic import BaseModel


class DestinationResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    source: str
    url: str
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
    created_at: datetime
    updated_at: datetime | None = None


class DestinationListResponse(BaseModel):
    destinations: list[DestinationResponse]
    total: int


class SyncResponse(BaseModel):
    status: str
    count: int


class UpdateDestinationRequest(BaseModel):
    url: str


class UpdateDestinationResponse(BaseModel):
    status: str
    title: str


class NearSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50


class NearSearchResponse(BaseModel):
    destinations: list[DestinationResponse]
    total: int
