import logging

from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.ai.embeddings.gemini_embeddings import GeminiEmbeddings
from travel_planner_co.infrastructure.data.postgres import PostgresDatabase
from travel_planner_co.infrastructure.data.repositories.destination_repository import (
    DestinationRepository,
)
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.scrapers.colombia_travel_scraper import ColombiaTravel
from travel_planner_co.infrastructure.scrapers.travelgrafia_scraper import Travelgrafia
from travel_planner_co.infrastructure.services.scraper_service import ScraperService
from travel_planner_co.infrastructure.services.text_chunker import SimpleTextChunker

logger = logging.getLogger(__name__)


def _bootstrap_use_cases(db: PostgresDatabase):
    scraper_service = ScraperService(scrapers=[ColombiaTravel(), Travelgrafia()])
    repo = DestinationRepository(db=db)
    chunker = SimpleTextChunker()
    embedding_provider = GeminiEmbeddings(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    vector_store = PGVectorStore(db=db)

    sync_uc = SyncAllSourcesUseCase(
        scraper_service=scraper_service,
        destination_repository=repo,
        text_chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    update_uc = UpdateDestinationUseCase(
        scraper_service=scraper_service,
        destination_repository=repo,
        text_chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    return sync_uc, update_uc


async def sync_all_sources_worker(ctx):
    logger.info("Worker: starting sync_all_sources")
    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()
    try:
        sync_uc, _ = _bootstrap_use_cases(db)
        count = await sync_uc.execute()
        logger.info("Worker: sync_all_sources completed, %d destinations", count)
        return {"count": count}
    except Exception:
        logger.exception("Worker: sync_all_sources failed")
        raise
    finally:
        await db.disconnect()


async def update_destination_worker(ctx, url: str):
    logger.info("Worker: starting update_destination for %s", url)
    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()
    try:
        _, update_uc = _bootstrap_use_cases(db)
        title = await update_uc.execute(url=url)
        logger.info("Worker: update_destination completed for %s", title)
        return {"title": title}
    except Exception:
        logger.exception("Worker: update_destination failed for %s", url)
        raise
    finally:
        await db.disconnect()
