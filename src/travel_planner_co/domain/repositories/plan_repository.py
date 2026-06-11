from abc import ABC, abstractmethod

from travel_planner_co.domain.entities.plan import Plan


class PlanRepository(ABC):
    @abstractmethod
    async def save(self, plan: Plan) -> str:
        ...
