from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.core.database import cur

class CheckAvailabilityInput(BaseModel):
    car_id: int = Field(description="The unique integer ID of the car to check availability for.")

class CheckAvailabilityTool(BaseTool):
    name = "check_availability"
    description = "Checks if a car is available in the inventory using its car ID."
    args_schema = CheckAvailabilityInput

    async def run(self, car_id: int) -> dict:
        if not cur:
            return {"available": False, "error": "Database cursor unavailable."}
        cur.execute("SELECT make, model, year, price, condition FROM cars WHERE id = %s", (car_id,))
        row = cur.fetchone()
        if row:
            make, model, year, price, condition = row
            return {
                "available": True,
                "car": f"{year} {make} {model}",
                "price": float(price),
                "condition": condition
            }
        return {"available": False}
