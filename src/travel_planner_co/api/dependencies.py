from arq.connections import ArqRedis

from fastapi import Depends
from starlette.requests import HTTPConnection

from travel_planner_co.application.use_cases.generate_plan import GeneratePlanUseCase
from travel_planner_co.application.use_cases.sync_all_sources import SyncAllSourcesUseCase
from travel_planner_co.application.use_cases.update_destination import UpdateDestinationUseCase
from travel_planner_co.domain.repositories.destination_repository import DestinationRepository
from travel_planner_co.domain.repositories.plan_repository import PlanRepository
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.ai.embeddings.gemini_embeddings import GeminiEmbeddings
from travel_planner_co.infrastructure.ai.llm.gemini_provider import GeminiProvider
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.data.repositories.destination_repository import (
    DestinationRepository as DestinationRepositoryImpl,
)
from travel_planner_co.infrastructure.data.repositories.plan_repository import (
    PlanRepository as PlanRepositoryImpl,
)
from travel_planner_co.infrastructure.scrapers.colombia_travel_scraper import ColombiaTravel
from travel_planner_co.infrastructure.scrapers.travelgrafia_scraper import Travelgrafia
from travel_planner_co.infrastructure.services.geo_enricher import GeoEnricher
from travel_planner_co.infrastructure.services.scraper_service import ScraperService
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

def get_plan_repository(db=Depends(get_database)) -> PlanRepository:
    return PlanRepositoryImpl(db=db)

def get_text_chunker() -> SimpleTextChunker:
    return SimpleTextChunker()

def get_scraper_service() -> ScraperService:
    scrapers = [Travelgrafia()]
    return ScraperService(scrapers=scrapers)

def get_geo_enricher(llm_provider=Depends(get_llm_provider)) -> GeoEnricher:
    return GeoEnricher(llm_provider=llm_provider)

def get_sync_all_sources_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
    destination_repository: DestinationRepository = Depends(get_destination_repository),
    text_chunker: SimpleTextChunker = Depends(get_text_chunker),
    embedding_provider=Depends(get_embedding_provider),
    vector_store=Depends(get_vector_store),
    geo_enricher: GeoEnricher = Depends(get_geo_enricher),
) -> SyncAllSourcesUseCase:
    return SyncAllSourcesUseCase(
        scraper_service=scraper_service,
        destination_repository=destination_repository,
        text_chunker=text_chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        geo_enricher=geo_enricher,
    )

def get_update_destination_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
    destination_repository: DestinationRepository = Depends(get_destination_repository),
    text_chunker: SimpleTextChunker = Depends(get_text_chunker),
    embedding_provider=Depends(get_embedding_provider),
    vector_store=Depends(get_vector_store),
    geo_enricher: GeoEnricher = Depends(get_geo_enricher),
) -> UpdateDestinationUseCase:
    return UpdateDestinationUseCase(
        scraper_service=scraper_service,
        destination_repository=destination_repository,
        text_chunker=text_chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        geo_enricher=geo_enricher,
    )

def get_generate_plan_use_case(
    llm_provider=Depends(get_llm_provider),
    destination_repository: DestinationRepository = Depends(get_destination_repository),
    plan_repository: PlanRepository = Depends(get_plan_repository),
    geo_enricher: GeoEnricher = Depends(get_geo_enricher),
) -> GeneratePlanUseCase:
    return GeneratePlanUseCase(
        llm_provider=llm_provider,
        destination_repository=destination_repository,
        plan_repository=plan_repository,
        geo_enricher=geo_enricher,
    )

def get_redis_pool(request: HTTPConnection) -> ArqRedis:
    return request.app.state.redis
