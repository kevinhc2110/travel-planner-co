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
            INSERT INTO documents (filename)
            VALUES ($1)
            RETURNING id
            """,
            f"{destination.source} - {destination.title}",
        )
        return row[0]["id"]

    async def list_all(self) -> list[Destination]:
        rows = await self.db.fetch(
            """
            SELECT id, filename, created_at
            FROM documents
            ORDER BY created_at DESC
            """
        )
        return [
            Destination(
                title=row["filename"],
                content="",
                source="",
                url="",
            )
            for row in rows
        ]
