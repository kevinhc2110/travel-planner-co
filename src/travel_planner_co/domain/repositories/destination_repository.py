from abc import ABC, abstractmethod

from travel_planner_co.domain.entities.destination import Destination


class DestinationRepository(ABC):
    @abstractmethod
    async def save(self, destination: Destination) -> str:
        ...

    @abstractmethod
    async def list_all(self) -> list[Destination]:
        ...
