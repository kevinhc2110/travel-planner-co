from dataclasses import dataclass
from datetime import datetime


@dataclass
class Destination:
    title: str
    content: str
    source: str
    url: str
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
