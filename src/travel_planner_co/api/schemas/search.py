from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    content: str
    destination_id: str
    metadata: dict | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
