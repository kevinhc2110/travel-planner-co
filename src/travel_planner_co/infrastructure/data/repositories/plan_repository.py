import json

from travel_planner_co.domain.entities.plan import Plan
from travel_planner_co.domain.repositories.plan_repository import PlanRepository as BasePlanRepository


class PlanRepository(BasePlanRepository):
    def __init__(self, db):
        self.db = db

    async def save(self, plan: Plan) -> str:
        row = await self.db.fetch(
            """
            INSERT INTO plans (location, days, preferences, itinerary)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            plan.location,
            plan.days,
            json.dumps(plan.preferences) if plan.preferences else None,
            json.dumps(plan.itinerary) if plan.itinerary else None,
        )
        return str(row[0]["id"])
