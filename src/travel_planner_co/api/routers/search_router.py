from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import get_search_service
from travel_planner_co.api.schemas.search import SearchRequest, SearchResponse, SearchResult
from travel_planner_co.domain.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
):
    results = await search_service.search(query=body.query, top_k=body.top_k)
    return SearchResponse(
        results=[
            SearchResult(
                id=r.id,
                content=r.content,
                destination_id=r.destination_id,
                metadata=r.metadata,
            )
            for r in results
        ]
    )
