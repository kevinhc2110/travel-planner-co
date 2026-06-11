import json

from travel_planner_co.infrastructure.data.vectorstore.models import ChunkRecord


class PGVectorStore:
    def __init__(self, db):
        self.db = db

    async def add(
        self,
        destination_id: str,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:

        await self.db.execute(
            """
            INSERT INTO chunks (
                destination_id,
                content,
                embedding,
                metadata
            )
            VALUES ($1, $2, $3, $4)
            """,
            destination_id,
            content,
            embedding,
            json.dumps(metadata) if metadata else None
        )

    async def search(
        self,
        embedding: list[float],
        top_k: int = 5
    ) -> list[ChunkRecord]:

        rows = await self.db.fetch(
            """
            SELECT
                id,
                destination_id,
                content,
                metadata,
                embedding <-> $1 AS score
            FROM chunks
            ORDER BY score
            LIMIT $2;
            """,
            embedding,
            top_k
        )

        return [
            ChunkRecord(
                id=str(r["id"]),
                destination_id=str(r["destination_id"]),
                content=r["content"],
                metadata=json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"],
            )
            for r in rows
        ]

