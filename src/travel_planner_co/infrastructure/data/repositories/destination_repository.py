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
            INSERT INTO destinations (title, content, source, url)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            destination.title,
            destination.content,
            destination.source,
            destination.url,
        )
        return str(row[0]["id"])

    async def update(self, destination: Destination) -> None:
        await self.db.execute(
            """
            UPDATE destinations
            SET title = $1, content = $2, source = $3, updated_at = $4
            WHERE id = $5
            """,
            destination.title,
            destination.content,
            destination.source,
            datetime.now(timezone.utc),
            destination.id,
        )

    async def get_by_id(self, id: str) -> Destination | None:
        rows = await self.db.fetch(
            """
            SELECT id, title, content, source, url, created_at, updated_at
            FROM destinations
            WHERE id = $1
            """,
            id,
        )
        if not rows:
            return None
        r = rows[0]
        return Destination(
            id=str(r["id"]),
            title=r["title"],
            content=r["content"],
            source=r["source"],
            url=r["url"],
            created_at=r["created_at"],
            updated_at=r.get("updated_at"),
        )

    async def get_by_url(self, url: str) -> Destination | None:
        rows = await self.db.fetch(
            """
            SELECT id, title, content, source, url, created_at, updated_at
            FROM destinations
            WHERE url = $1
            """,
            url,
        )
        if not rows:
            return None
        r = rows[0]
        return Destination(
            id=str(r["id"]),
            title=r["title"],
            content=r["content"],
            source=r["source"],
            url=r["url"],
            created_at=r["created_at"],
            updated_at=r.get("updated_at"),
        )

    async def list_all(self) -> list[Destination]:
        rows = await self.db.fetch(
            """
            SELECT id, title, content, source, url, created_at, updated_at
            FROM destinations
            ORDER BY created_at DESC
            """
        )
        return [
            Destination(
                id=str(r["id"]),
                title=r["title"],
                content=r["content"],
                source=r["source"],
                url=r["url"],
                created_at=r["created_at"],
                updated_at=r.get("updated_at"),
            )
            for r in rows
        ]

    async def delete_chunks(self, destination_id: str) -> None:
        await self.db.execute(
            """
            DELETE FROM chunks WHERE destination_id = $1
            """,
            destination_id,
        )
