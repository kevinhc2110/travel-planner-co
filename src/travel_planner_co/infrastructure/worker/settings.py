from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.worker.functions import (
    sync_all_sources_worker,
    update_destination_worker,
)


class WorkerSettings:
    redis_settings = settings.redis_url
    functions = [sync_all_sources_worker, update_destination_worker]
    poll_delay = 0.5
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
    keep_result_failed = 3600
