import json

from travel_planner_co.infrastructure.data.vectorstore.models import ChunkRecord


class PGVectorStore:
    def __init__(self, db):
        self.db = db

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:

        await self.db.execute(
            """
            INSERT INTO chunks (
                document_id,
                content,
                embedding,
                metadata
            )
            VALUES ($1, $2, $3, $4)
            """,
            document_id,
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
                document_id,
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
                id=r["id"],
                document_id=r["document_id"],
                content=r["content"],
                metadata=r["metadata"],
            )
            for r in rows
        ]

