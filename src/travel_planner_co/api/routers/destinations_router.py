from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import (
    get_destination_repository,
    get_sync_all_sources_use_case,
    get_update_destination_use_case,
)
from travel_planner_co.api.schemas.destinations import (
    DestinationListResponse,
    DestinationResponse,
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
        destinations=[
            DestinationResponse(
                id=str(d.id),
                title=d.title,
                source=d.source,
                url=d.url,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in destinations
        ],
        total=len(destinations),
    )


@router.post("/sync", response_model=SyncResponse)
async def sync_all_sources(
    use_case: SyncAllSourcesUseCase = Depends(get_sync_all_sources_use_case),
):
    count = await use_case.execute()
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
