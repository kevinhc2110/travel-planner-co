from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    document_id: str
    embedding: list[float] | None = None
    metadata: dict | None = None
