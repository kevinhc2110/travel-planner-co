from fastapi import Depends
from starlette.requests import HTTPConnection

from hr_assistant.application.use_cases.retrieve_context_use_case import RetrieveContextUseCase

from travel_planner_co.application.use_cases.scrape_destinations import ScrapeDestinationsUseCase
from travel_planner_co.infrastructure.settings import settings
from travel_planner_co.infrastructure.ai.embeddings.gemini_embeddings import GeminiEmbeddings
from travel_planner_co.infrastructure.ai.llm.gemini_provider import GeminiProvider
from travel_planner_co.infrastructure.data.vectorstore.pgvector_store import PGVectorStore
from travel_planner_co.infrastructure.scrapers.colombia_travel_scraper import ColombiaTravel
from travel_planner_co.infrastructure.scrapers.travelgrafia_scraper import Travelgrafia
from travel_planner_co.infrastructure.services.scraper_service import ScraperService


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

def get_retrieve_context_use_case(
    embedding_provider = Depends(get_embedding_provider),
    vector_store = Depends(get_vector_store),
):
    return RetrieveContextUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store
    )

def get_scraper_service() -> ScraperService:
    scrapers = [ColombiaTravel(), Travelgrafia()]
    return ScraperService(scrapers=scrapers)

def get_scrape_destinations_use_case(
    scraper_service: ScraperService = Depends(get_scraper_service),
) -> ScrapeDestinationsUseCase:
    return ScrapeDestinationsUseCase(scraper_service=scraper_service)
