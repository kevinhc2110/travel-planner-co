from dataclasses import dataclass


@dataclass
class ChunkRecord:
    id: str
    destination_id: str
    content: str
    metadata: dict | None = None