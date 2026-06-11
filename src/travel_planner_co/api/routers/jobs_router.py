from arq.connections import ArqRedis
from arq.jobs import Job

from fastapi import APIRouter, Depends

from travel_planner_co.api.dependencies import get_redis_pool
from travel_planner_co.api.schemas.destinations import UpdateDestinationRequest
from pydantic import BaseModel


router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobEnqueued(BaseModel):
    job_id: str
    status: str = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None


@router.post("/sync", response_model=JobEnqueued, status_code=202)
async def enqueue_sync(
    redis: ArqRedis = Depends(get_redis_pool),
):
    job = await redis.enqueue_job("sync_all_sources_worker")
    return JobEnqueued(job_id=job.id)


@router.post("/update", response_model=JobEnqueued, status_code=202)
async def enqueue_update(
    body: UpdateDestinationRequest,
    redis: ArqRedis = Depends(get_redis_pool),
):
    job = await redis.enqueue_job("update_destination_worker", url=body.url)
    return JobEnqueued(job_id=job.id)


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    redis: ArqRedis = Depends(get_redis_pool),
):
    job = Job(job_id, redis)
    info = await job.info()

    if info is None:
        return JobStatus(job_id=job_id, status="not_found")

    status = "queued"
    result = None
    error = None

    if info.start_time and not info.finish_time:
        status = "in_progress"
    elif info.finish_time:
        if info.success:
            status = "complete"
            result = info.result
        else:
            status = "failed"
            error = info.error

    return JobStatus(
        job_id=job_id,
        status=status,
        result=result,
        error=error,
    )
