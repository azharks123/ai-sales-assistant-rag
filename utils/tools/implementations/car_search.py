from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from utils.tools.base import BaseTool
from utils.helper import cur

client = AsyncOpenAI()

class CarSearchInput(BaseModel):
    query: str = Field(description="Search query describing the car features, budget, or specifications.")
    top_k: int = Field(default=3, description="Number of matching cars to return (default 3).")

class CarSearchTool(BaseTool):
    name = "search_cars"
    description = (
        "Searches for matching cars in inventory based on explicit queries. "
        "Do NOT call for general car recommendation or budget preference queries; answer those directly."
    )
    args_schema = CarSearchInput

    async def run(self, query: str, top_k: int = 3) -> list:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        cur.execute(
            """
            SELECT make, model, year, price, mileage_km, condition, description,
                   embedding <-> %s::vector AS distance
            FROM cars
            ORDER BY distance ASC
            LIMIT %s
            """,
            (query_embedding, top_k)
        )
        rows = cur.fetchall()
        
        results = []
        for r in rows:
            make, model, year, price, mileage, condition, description, distance = r
            results.append({
                "car": f"{year} {make} {model}",
                "price": float(price),
                "mileage_km": mileage,
                "condition": condition,
                "description": description
            })
        return results
