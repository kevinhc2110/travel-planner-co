from fastapi import Depends
from redis.asyncio import Redis
from starlette.requests import HTTPConnection

from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository
from travel_planner_co.domain.services.ai_planner_service import AIPlannerService
from travel_planner_co.domain.services.search_service import SearchService
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.ai.embeddings.gemini_embeddings import GeminiEmbeddings
from travel_planner_co.infrastructure.ai.llm.gemini_provider import GeminiProvider
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.data.repositories.destination_repository import (
    DestinationRepository as DestinationRepositoryImpl,
)
from travel_planner_co.infrastructure.scrapers.colombia_travel_scraper import ColombiaTravel
from travel_planner_co.infrastructure.scrapers.travelgrafia_scraper import Travelgrafia
from travel_planner_co.infrastructure.services.ai_planner_service import AIPlannerService as AIPlannerServiceImpl
from travel_planner_co.infrastructure.services.scraper_service import ScraperService
from travel_planner_co.infrastructure.services.search_service import SearchService as SearchServiceImpl
from travel_planner_co.infrastructure.services.text_chunker import SimpleTextChunker

llm_provider = GeminiProvider(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

def get_llm_provider():
    return llm_provider

embedding_provider = GeminiEmbeddings(
    api_key=settings.gemini_api_key,
    model=settings.gemini_embedding_model,
)

def get_embedding_provider():
    return embedding_provider

def get_database(request: HTTPConnection):
    return request.app.state.db

def get_vector_store(db=Depends(get_database)):
    return PGVectorStore(db=db)

def get_destination_repository(db=Depends(get_database)) -> DestinationRepository:
    return DestinationRepositoryImpl(db=db)

def get_text_chunker() -> SimpleTextChunker:
    return SimpleTextChunker()

def get_scraper_service() -> ScraperService:
    scrapers = [ColombiaTravel(), Travelgrafia()]
    return ScraperService(scrapers=scrapers)

def get_search_service(
    embedding_provider=Depends(get_embedding_provider),
    vector_store=Depends(get_vector_store),
) -> SearchService:
    return SearchServiceImpl(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

def get_scrape_destinations_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
) -> SyncAllSourcesUseCase:
    return SyncAllSourcesUseCase(scraper_service=scraper_service)

def get_sync_all_sources_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
    destination_repository: DestinationRepository = Depends(get_destination_repository),
    text_chunker: SimpleTextChunker = Depends(get_text_chunker),
    embedding_provider=Depends(get_embedding_provider),
    vector_store=Depends(get_vector_store),
) -> SyncAllSourcesUseCase:
    return SyncAllSourcesUseCase(
        scraper_service=scraper_service,
        destination_repository=destination_repository,
        text_chunker=text_chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

def get_update_destination_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
    destination_repository: DestinationRepository = Depends(get_destination_repository),
    text_chunker: SimpleTextChunker = Depends(get_text_chunker),
    embedding_provider=Depends(get_embedding_provider),
    vector_store=Depends(get_vector_store),
) -> UpdateDestinationUseCase:
    return UpdateDestinationUseCase(
        scraper_service=scraper_service,
        destination_repository=destination_repository,
        text_chunker=text_chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

def get_ai_planner_service(
    llm_provider=Depends(get_llm_provider),
    search_service: SearchService = Depends(get_search_service),
) -> AIPlannerService:
    return AIPlannerServiceImpl(
        llm_provider=llm_provider,
        search_service=search_service,
    )

def get_redis_pool(request: HTTPConnection) -> Redis:
    return request.app.state.redis
