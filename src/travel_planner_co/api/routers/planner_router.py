from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import get_ai_planner_service
from travel_planner_co.api.schemas.chat import ChatRequest, ChatResponse
from travel_planner_co.domain.services.ai_planner_service import AIPlannerService

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    planner: AIPlannerService = Depends(get_ai_planner_service),
):
    response = await planner.chat(
        query=body.query,
        conversation_id=body.conversation_id,
    )
    return ChatResponse(
        response=response,
        conversation_id=body.conversation_id or "",
    )
