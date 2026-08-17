import os
import asyncio
import psycopg2
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI()

DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "mysecretpassword"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cur = conn.cursor()

async def get_embedding(text: str):
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

async def retrieve_cars(query: str, top_k: int = 2):
    query_embedding = await get_embedding(query)

    # <-> is pgvector's L2 distance operator; smaller = more similar
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
    return rows

async def main():
    test_queries = [
        "cheap SUV under 10 lakhs",
        "I want a diesel family car with good mileage",
        "budget-friendly first car"
    ]
    
    test_queries = ["reliable sedan with spacious interior"]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = await retrieve_cars(query)
        for r in results:
            make, model, year, price, mileage, condition, description, distance = r
            print(f"  [{distance:.4f}] {year} {make} {model} - ₹{price} - {condition}")

if __name__ == "__main__":
    asyncio.run(main())