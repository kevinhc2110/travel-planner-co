from abc import ABC, abstractmethod

from travel_planner_co.domain.entities.destination import Destination


class DestinationRepository(ABC):
    @abstractmethod
    async def save(self, destination: Destination) -> str:
        ...

    @abstractmethod
    async def update(self, destination: Destination) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, id: str) -> Destination | None:
        ...

    @abstractmethod
    async def get_by_url(self, url: str) -> Destination | None:
        ...

    @abstractmethod
    async def list_all(self) -> list[Destination]:
        ...

    @abstractmethod
    async def search_near(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[Destination]:
        ...

    @abstractmethod
    async def delete_chunks(self, destination_id: str) -> None:
        ...
