from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import get_generate_plan_use_case
from travel_planner_co.api.schemas.chat import (
    GeneratePlanRequest,
    GeneratePlanResponse,
)
from travel_planner_co.application.use_cases.generate_plan import GeneratePlanUseCase

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(
    body: GeneratePlanRequest,
    use_case: GeneratePlanUseCase = Depends(get_generate_plan_use_case),
):
    plan = await use_case.execute(
        location=body.location,
        days=body.days,
        categories=body.categories,
        preferences=body.preferences,
    )
    return GeneratePlanResponse(
        plan_id=str(plan.id),
        location=plan.location,
        days=plan.days,
        categories=body.categories,
        itinerary=plan.itinerary or {},
    )
