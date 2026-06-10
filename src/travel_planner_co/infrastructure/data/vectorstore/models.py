from dataclasses import dataclass


@dataclass
class ChunkRecord:
    id: str
    document_id: str
    content: str
    metadata: dict | None = None