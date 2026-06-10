from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from travel_planner_co.api.routers.destinations_router import router as destinations_router
from travel_planner_co.api.routers.jobs_router import router as jobs_router
from travel_planner_co.api.routers.planner_router import router as planner_router
from travel_planner_co.api.routers.search_router import router as search_router
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.data.postgres import PostgresDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()
    app.state.db = db

    redis = Redis.from_url(settings.redis_url)
    app.state.redis = redis

    yield

    await redis.close()
    await db.disconnect()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

app.include_router(destinations_router)
app.include_router(jobs_router)
app.include_router(planner_router)
app.include_router(search_router)
