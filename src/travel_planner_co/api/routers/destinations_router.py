from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import (
    get_destination_repository,
    get_sync_all_sources_use_case,
    get_update_destination_use_case,
)
from travel_planner_co.api.schemas.destinations import (
    DestinationListResponse,
    DestinationResponse,
    NearSearchRequest,
    NearSearchResponse,
    SyncResponse,
    UpdateDestinationRequest,
    UpdateDestinationResponse,
)
from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.get("", response_model=DestinationListResponse)
async def list_destinations(
    repo: DestinationRepository = Depends(get_destination_repository),
):
    destinations = await repo.list_all()
    return DestinationListResponse(
        destinations=[_to_response(d) for d in destinations],
        total=len(destinations),
    )


@router.post("/sync", response_model=SyncResponse)
async def sync_all_sources(
    max_urls: int | None = None,
    use_case: SyncAllSourcesUseCase = Depends(get_sync_all_sources_use_case),
):
    count = await use_case.execute(max_urls=max_urls)
    return SyncResponse(status="ok", count=count)


@router.post("/update", response_model=UpdateDestinationResponse)
async def update_destination(
    body: UpdateDestinationRequest,
    use_case: UpdateDestinationUseCase = Depends(get_update_destination_use_case),
):
    title = await use_case.execute(url=body.url)
    if title is None:
        return UpdateDestinationResponse(status="not_found", title="")
    return UpdateDestinationResponse(status="ok", title=title)


@router.post("/near", response_model=NearSearchResponse)
async def search_near(
    body: NearSearchRequest,
    repo: DestinationRepository = Depends(get_destination_repository),
):
    destinations = await repo.search_near(
        latitude=body.latitude,
        longitude=body.longitude,
        radius_km=body.radius_km,
    )
    return NearSearchResponse(
        destinations=[_to_response(d) for d in destinations],
        total=len(destinations),
    )


def _to_response(d) -> DestinationResponse:
    return DestinationResponse(
        id=str(d.id),
        name=d.name,
        description=d.description,
        source=d.source,
        url=d.url,
        city=d.city,
        department=d.department,
        country=d.country,
        category=d.category,
        rating=d.rating,
        estimated_days=d.estimated_days,
        best_season=d.best_season,
        latitude=d.latitude,
        longitude=d.longitude,
        tags=d.tags,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )
