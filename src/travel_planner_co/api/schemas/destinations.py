from datetime import datetime

from pydantic import BaseModel


class DestinationResponse(BaseModel):
    id: str
    title: str
    source: str
    url: str
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
