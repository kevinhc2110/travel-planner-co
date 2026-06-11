from pydantic import BaseModel


class GeneratePlanRequest(BaseModel):
    city: str
    days: int
    categories: list[str] | None = None
    preferences: dict | None = None


class GeneratePlanResponse(BaseModel):
    plan_id: str
    city: str
    days: int
    categories: list[str] | None = None
    itinerary: dict
