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

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cur.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    make VARCHAR(255),
    model VARCHAR(255),
    year INT,
    price NUMERIC,
    mileage_km INT,
    condition VARCHAR(50),
    description TEXT,
    embedding vector(1536)
);
""")
conn.commit()

SAMPLE_CARS = [
    {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "year": 2019,
        "price": 550000,
        "mileage_km": 42000,
        "condition": "Good",
        "description": "2019 Maruti Suzuki Swift, petrol, 42000 km driven, good condition, single owner, ideal first car with great fuel efficiency.",
    },
    {
        "make": "Hyundai",
        "model": "Creta",
        "year": 2021,
        "price": 1250000,
        "mileage_km": 28000,
        "condition": "Excellent",
        "description": "2021 Hyundai Creta SUV, diesel, 28000 km, excellent condition, top variant with sunroof, well-maintained family SUV.",
    },
    {
        "make": "Tata",
        "model": "Nexon",
        "year": 2020,
        "price": 850000,
        "mileage_km": 35000,
        "condition": "Good",
        "description": "2020 Tata Nexon compact SUV, petrol, 35000 km driven, good condition, 5-star safety rating, budget-friendly SUV under 10 lakhs.",
    },
    {
        "make": "Honda",
        "model": "City",
        "year": 2018,
        "price": 700000,
        "mileage_km": 55000,
        "condition": "Fair",
        "description": "2018 Honda City sedan, petrol, 55000 km, fair condition, reliable sedan with spacious interior, needs minor servicing.",
    },
    {
        "make": "Mahindra",
        "model": "XUV700",
        "year": 2022,
        "price": 1800000,
        "mileage_km": 15000,
        "condition": "Excellent",
        "description": "2022 Mahindra XUV700 diesel, 15000 km, excellent condition, premium 7-seater SUV, almost like new, top-of-the-line features.",
    },
]


async def get_embedding(text: str):
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=text
    )
    return response.data[0].embedding


async def main():
    for car in SAMPLE_CARS:
        embedding = await get_embedding(car["description"])
        cur.execute(
            """
            INSERT INTO cars (make, model, year, price, mileage_km, condition, description, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                car["make"],
                car["model"],
                car["year"],
                car["price"],
                car["mileage_km"],
                car["condition"],
                car["description"],
                embedding,
            ),
        )
        print(f"Inserted: {car['make']} {car['model']}")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
