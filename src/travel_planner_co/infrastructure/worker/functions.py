from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.ai.embeddings.gemini_embeddings import GeminiEmbeddings
from travel_planner_co.infrastructure.ai.llm.gemini_provider import GeminiProvider
from travel_planner_co.infrastructure.data.postgres import PostgresDatabase
from travel_planner_co.infrastructure.data.repositories.destination_repository import (
    DestinationRepository,
)
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.scrapers.colombia_travel_scraper import ColombiaTravel
from travel_planner_co.infrastructure.scrapers.travelgrafia_scraper import Travelgrafia
from travel_planner_co.infrastructure.services.geo_enricher import GeoEnricher
from travel_planner_co.infrastructure.services.scraper_service import ScraperService
from travel_planner_co.infrastructure.services.text_chunker import SimpleTextChunker

_db_pool: PostgresDatabase | None = None


async def get_worker_db() -> PostgresDatabase:
    global _db_pool
    if _db_pool is None:
        _db_pool = PostgresDatabase(dsn=settings.postgres_dsn)
        await _db_pool.connect()
    return _db_pool


async def close_worker_db() -> None:
    global _db_pool
    if _db_pool is not None:
        await _db_pool.disconnect()
        _db_pool = None


def _bootstrap_use_cases(db: PostgresDatabase):
    llm_provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )
    scraper_service = ScraperService(scrapers=[ColombiaTravel(), Travelgrafia()])
    repo = DestinationRepository(db=db)
    chunker = SimpleTextChunker()
    embedding_provider = GeminiEmbeddings(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    vector_store = PGVectorStore(db=db)
    geo_enricher = GeoEnricher(llm_provider=llm_provider)

    sync_uc = SyncAllSourcesUseCase(
        scraper_service=scraper_service,
        destination_repository=repo,
        text_chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        geo_enricher=geo_enricher,
    )
    update_uc = UpdateDestinationUseCase(
        scraper_service=scraper_service,
        destination_repository=repo,
        text_chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        geo_enricher=geo_enricher,
    )
    return sync_uc, update_uc


async def sync_all_sources_worker(ctx):
    db = await get_worker_db()
    sync_uc, _ = _bootstrap_use_cases(db)
    count = await sync_uc.execute()
    return {"count": count}


async def update_destination_worker(ctx, url: str):
    db = await get_worker_db()
    _, update_uc = _bootstrap_use_cases(db)
    title = await update_uc.execute(url=url)
    return {"title": title}
