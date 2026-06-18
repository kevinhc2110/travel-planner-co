# Travel Planner CO

Intelligent travel planner for Colombia powered by AI. Scrapes Colombian tourism sources, extracts destinations, enriches them with geolocation, and generates personalized travel plans using Gemini.

## Architecture

```text
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│    FastAPI   │────▶│  PostgreSQL  │
│  (React/TS)  │     │   (uvicorn)  │     │  + pgvector  │
└─────────────┘     └──────┬───────┘     │  + PostGIS   │
                           │              └──────────────┘
                           │              ┌──────────────┐
                           ├─────────────▶│    Redis      │
                           │              │   (arq queue) │
                           │              └──────┬───────┘
                           │                     │
                           │              ┌──────▼───────┐
                           │              │   Worker     │
                           └──────────────│  (arq/async) │
                                          └──────────────┘
```

- **FastAPI** — REST API with dependency injection
- **PostgreSQL 17** — pgvector (3072d embeddings) + PostGIS (spatial queries)
- **Redis** — task queue using arq for async scraping
- **Gemini** — LLM for data extraction and plan generation; embedding model
- **Web scrapers** — `colombia.travel`, `travelgrafia.co`
- **Frontend** — React + TypeScript + Vite (SPA)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.24
- A [Gemini API key](https://aistudio.google.com/apikey)

## Quick start

### 1. Clone and configure

```bash
git clone <repo-url>
cd travel-planner-co
cp .env.example .env
```

Edit `.env` and set your Gemini API key:

```env
gemini_api_key=AIzaSy...
```

### 2. Start all services

```bash
docker compose up --build
```

This starts 5 containers:

| Service    | Port | Description                        |
| ---------- | ---- | ---------------------------------- |
| `db`       | 5432 | PostgreSQL 17 + pgvector + PostGIS |
| `redis`    | 6379 | Redis task queue                   |
| `app`      | 8000 | FastAPI server                     |
| `worker`   | —    | Async arq worker                   |
| `frontend` | 5173 | React + Vite SPA                   |

### 3. Open in browser

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend**: [http://localhost:5173](http://localhost:5173)

### 4. Sync destinations

```bash
curl -X POST http://localhost:8000/destinations/sync
```

## Environment variables

| Variable                 | Description           | Default                                             |
| ------------------------ | --------------------- | --------------------------------------------------- |
| `gemini_api_key`         | Google Gemini API key | (required)                                          |
| `gemini_model`           | LLM model name        | `gemini-3.1-flash-lite`                             |
| `gemini_embedding_model` | Embedding model name  | `gemini-embedding-2`                                |
| `postgres_dsn`           | PostgreSQL DSN        | `postgresql://user:password@db:5432/travel_planner` |
| `postgres_user`          | PostgreSQL user       | `user`                                              |
| `postgres_password`      | PostgreSQL password   | `password`                                          |
| `postgres_db`            | Database name         | `travel_planner`                                    |
| `redis_url`              | Redis connection URL  | `redis://redis:6379/0`                              |

## Useful commands

```bash
# Tail logs for a specific service
docker compose logs -f app

# Manual sync (with limit)
curl -X POST http://localhost:8000/destinations/sync?max_urls=5

# Generate a travel plan
curl -X POST http://localhost:8000/planner/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"location": "Santa Marta", "days": 3, "categories": ["beach", "nature"]}'

# Search nearby destinations
curl -X POST http://localhost:8000/destinations/near \
  -H "Content-Type: application/json" \
  -d '{"latitude": 4.711, "longitude": -74.072, "radius_km": 100}'

# List all destinations
curl http://localhost:8000/destinations
```

## Development

### Running tests

```bash
# With Docker
docker compose run --rm app poetry install --with dev
docker compose run --rm app python -m pytest tests/ -v

# Locally (requires Python ≥3.13 + Poetry ≥2.0)
poetry install --with dev
poetry run pytest tests/ -v
```

### Project structure

```text
src/travel_planner_co/
├── main.py                        # FastAPI entry point
├── api/                           # Presentation layer
│   ├── dependencies.py            # Dependency injection wiring
│   ├── routers/                   # REST endpoints
│   └── schemas/                   # Pydantic models
├── application/use_cases/         # Use cases (orchestration)
├── domain/                        # Domain layer
│   ├── entities/                  # Domain entities (dataclasses)
│   ├── repositories/              # Ports (interfaces)
│   └── services/                  # Service interfaces
└── infrastructure/                # Concrete implementations
    ├── ai/                        # LLM + embeddings (Gemini)
    ├── data/                      # PostgreSQL, pgvector, repos
    ├── http/                      # HTTP client (rate limiting)
    ├── scrapers/                  # Site-specific scrapers
    ├── services/                  # Services (scraper, chunker, geocoder)
    └── worker/                    # Async tasks (arq)
```

### Adding a scraper

1. Create a class extending `Scraper` in `infrastructure/scrapers/`
2. Implement `collect_article_urls()` and `scrape_article(url)`
3. Add it to the list in `api/dependencies.py:get_scraper_service()`

## License

MIT
