# travel-planner-co

## Package vs imports mismatch

The package is `travel_planner_co` (under `src/`), but **all internal imports** reference `hr_assistant.*` instead. The codebase was partially renamed and is currently broken. Any new code must either fix imports to use `travel_planner_co` or reconcile the package name.

## Entrypoint

`uvicorn travel_planner_co.main:app` (Dockerfile incorrectly uses `hr_assistant.main:app`)

## Architecture

- **FastAPI** app with Gemini LLM + embeddings, asyncpg/pgvector, and web scrapers for Colombian travel sites
- **Stack**: Python ≥3.13, Poetry ≥2.0, FastAPI, asyncpg, pgvector, google-genai, BeautifulSoup
- **DB**: PostgreSQL 17 with pgvector (vector dim 3072), schema in `db/init.sql`
- **Config**: pydantic-settings reads `.env` via `Settings` class in `infrastructure/settings.py`
- **Dependencies**: wired in `api/dependencies.py` (singleton llm/embedding providers, request-scoped DB via `app.state.db`)

## Repository pattern

- `domain/repositories/` — abstract interfaces (ports)
- `infrastructure/data/` — concrete implementations (adapters), including databases, vectorstore, and repositories

## Infrastructure layout

```text
infrastructure/
  ai/              — LLM + embeddings (Gemini)
  data/            — database, vectorstore, repository implementations
  settings.py      — Settings (pydantic-settings, reads .env)
  http/            — shared HTTP utilities (fetch_html, rate limiting)
  scrapers/        — site-specific scrapers
  services/        — concrete service implementations (ScraperService)
```

## Dev commands

```bash
poetry install                          # install deps (no lockfile committed)
uvicorn travel_planner_co.main:app --reload  # dev server
docker compose up --build               # full stack (db + app)
```

## Known issues (must fix before running)

- `main.py` imports routers from `hr_assistant.api.routers.*` and `RetrieveContextUseCase` from `hr_assistant.application.*` — will crash at runtime. `api/dependencies.py` mixes both `hr_assistant.*` and `travel_planner_co.*` imports (transitional).
- `demo/` directory referenced in Dockerfile does not exist (frontend build stage will fail)
- No tests exist (`tests/` is empty), no test framework configured
- Placeholder directories: `api/routers/`, `api/schemas/` are empty

## Scrapers

Located in `infrastructure/scrapers/`. Each scraper extends `Scraper` (ABC) and implements:

Shared HTTP utility `fetch_html` lives in `infrastructure/http/fetch.py` (rate limiting, Cloudflare detection, error handling).

- `collect_article_urls() -> list[str]` — orchestrates URL discovery
- `scrape_article(url) -> dict` — extracts title + content from a single page

Shared helpers on `Scraper`:

- `clean_content(container)` — strips `a/figure/img/picture/source/figcaption/iframe`, extracts text from `h2,h3,h4,p,li`, joins with double newline
- `extract_links(soup, selector, prefix)` — deduplicated link extraction from CSS selector

The concrete `ScraperService` (in `infrastructure/services/`) iterates all scrapers, calls `collect_article_urls` + `scrape_article`, and returns `list[Destination]`. Wired via `get_scraper_service()` / `get_scrape_destinations_use_case()` in `api/dependencies.py`.

## Docker

- `docker-compose.yml` runs pgvector:pg17 + app on port 8000
- `.env` is required (contains API keys — do not commit)
- Container mounts `.` to `/app` for hot reload
