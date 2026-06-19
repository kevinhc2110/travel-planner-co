from arq.connections import RedisSettings

from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.worker.functions import (
    close_worker_db,
    get_worker_db,
    sync_all_sources_worker,
    update_destination_worker,
)


async def _init_worker(ctx):
    await get_worker_db()


async def _shutdown_worker(ctx):
    await close_worker_db()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [sync_all_sources_worker, update_destination_worker]
    poll_delay = 0.5
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
    keep_result_failed = 3600
    on_startup = _init_worker
    on_shutdown = _shutdown_worker
