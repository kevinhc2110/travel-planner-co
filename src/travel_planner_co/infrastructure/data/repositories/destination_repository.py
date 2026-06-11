from datetime import datetime, timezone

from travel_planner_co.domain.entities.destination import Destination
from travel_planner_co.domain.repositories.destination_repository import (
    DestinationRepository as BaseDestinationRepository,
)


class DestinationRepository(BaseDestinationRepository):
    def __init__(self, db):
        self.db = db

    async def save(self, destination: Destination) -> str:
        row = await self.db.fetch(
            """
            INSERT INTO destinations (
                name, description, full_content, source, url,
                city, department, country, category, rating,
                estimated_days, best_season, location, tags
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                    ST_SetSRID(ST_MakePoint($13, $14), 4326)::geography, $15)
            RETURNING id
            """,
            destination.name,
            destination.description,
            destination.full_content,
            destination.source,
            destination.url,
            destination.city,
            destination.department,
            destination.country,
            destination.category,
            destination.rating,
            destination.estimated_days,
            destination.best_season,
            destination.longitude,
            destination.latitude,
            destination.tags,
        )
        return str(row[0]["id"])

    async def update(self, destination: Destination) -> None:
        await self.db.execute(
            """
            UPDATE destinations
            SET name = $1, description = $2, full_content = $3, source = $4,
                city = $5, department = $6, country = $7, category = $8,
                rating = $9, estimated_days = $10, best_season = $11,
                location = ST_SetSRID(ST_MakePoint($12, $13), 4326)::geography,
                tags = $14, updated_at = $15
            WHERE id = $16
            """,
            destination.name,
            destination.description,
            destination.full_content,
            destination.source,
            destination.city,
            destination.department,
            destination.country,
            destination.category,
            destination.rating,
            destination.estimated_days,
            destination.best_season,
            destination.longitude,
            destination.latitude,
            destination.tags,
            datetime.now(timezone.utc),
            destination.id,
        )

    def _row_to_destination(self, r) -> Destination:
        loc = r.get("location")
        lon = lat = None
        if loc:
            if hasattr(loc, 'x'):
                lon = loc.x
                lat = loc.y
            elif isinstance(loc, (list, tuple)):
                lon, lat = loc
        return Destination(
            id=str(r["id"]),
            name=r["name"],
            description=r.get("description"),
            full_content=r.get("full_content"),
            source=r["source"],
            url=r["url"],
            city=r.get("city"),
            department=r.get("department"),
            country=r.get("country", "Colombia"),
            category=r.get("category"),
            rating=(
                float(r["rating"]) if r.get("rating") is not None else None
            ),
            estimated_days=r.get("estimated_days"),
            best_season=r.get("best_season"),
            latitude=lat,
            longitude=lon,
            tags=r.get("tags"),
            created_at=r["created_at"],
            updated_at=r.get("updated_at"),
        )

    async def get_by_id(self, id: str) -> Destination | None:
        rows = await self.db.fetch(
            """
            SELECT id, name, description, full_content, source, url,
                   city, department, country, category, rating,
                   estimated_days, best_season,
                   ST_AsGeoJSON(location)::json->'coordinates' as location,
                   tags, created_at, updated_at
            FROM destinations
            WHERE id = $1
            """,
            id,
        )
        if not rows:
            return None
        return self._row_to_destination(rows[0])

    async def get_by_url(self, url: str) -> Destination | None:
        rows = await self.db.fetch(
            """
            SELECT id, name, description, full_content, source, url,
                   city, department, country, category, rating,
                   estimated_days, best_season,
                   ST_AsGeoJSON(location)::json->'coordinates' as location,
                   tags, created_at, updated_at
            FROM destinations
            WHERE url = $1
            """,
            url,
        )
        if not rows:
            return None
        return self._row_to_destination(rows[0])

    async def list_all(self) -> list[Destination]:
        rows = await self.db.fetch(
            """
            SELECT id, name, description, full_content, source, url,
                   city, department, country, category, rating,
                   estimated_days, best_season,
                   ST_AsGeoJSON(location)::json->'coordinates' as location,
                   tags, created_at, updated_at
            FROM destinations
            ORDER BY created_at DESC
            """
        )
        return [self._row_to_destination(r) for r in rows]

    async def search_near(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[Destination]:
        rows = await self.db.fetch(
            """
            SELECT id, name, description, full_content, source, url,
                   city, department, country, category, rating,
                   estimated_days, best_season,
                   ST_AsGeoJSON(location)::json->'coordinates' as location,
                   tags, created_at, updated_at,
                   ST_Distance(
                       location,
                       ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                   ) / 1000 AS distance_km
            FROM destinations
            WHERE ST_DWithin(
                location,
                ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                $3 * 1000
            )
            ORDER BY distance_km
            """,
            longitude,
            latitude,
            radius_km,
        )
        return [self._row_to_destination(r) for r in rows]

    async def delete_chunks(self, destination_id: str) -> None:
        await self.db.execute(
            """
            DELETE FROM chunks WHERE destination_id = $1
            """,
            destination_id,
        )
