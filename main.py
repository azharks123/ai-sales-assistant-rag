import os
import json
import redis
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL=os.getenv("DEFAULT_MODEL")
MAX_TOKEN=int(os.getenv("MAX_TOKEN"))
TEMPERATURE=float(os.getenv("TEMPERATURE"))

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASS=os.getenv("DB_PASS")

REDIS_HOST=os.getenv("REDIS_HOST")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cur = conn.cursor()

app = FastAPI()
client = AsyncOpenAI()
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

SESSION_TTL = 1800

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a Sales Manager from a second-sale car showroom(True value cars). you trying connecting a customer via call for the special sale offer"
}

class ChatReponse(BaseModel):
    user_id: str
    message: str

class ChatPayload(BaseModel):
    user_id: str
    message: str

@app.get("/")
def root():
    return {"message": "Hello World"}

async def get_embedding(text: str):
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

async def retrieve_cars(query: str, top_k: int = 3):
    query_embedding = await get_embedding(query)
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
    return cur.fetchall()

def format_car_context(rows):
    if not rows:
        return "No matching cars found in inventory."
    lines = ["Relevant cars currently in inventory:"]
    for r in rows:
        make, model, year, price, mileage, condition, description, distance = r
        lines.append(f"- {year} {make} {model}, ₹{price}, {mileage} km, {condition} condition: {description}")
    return "\n".join(lines)

@app.post("/chat", response_model=ChatReponse)
async def ai_chat(payload: ChatPayload):
    redis_key = f"chat_session:{payload.user_id}"
    try:
        # Retrieve relevant inventory based on the user's message
        car_rows = await retrieve_cars(payload.message)
        car_context = format_car_context(car_rows)

        context_message = {
            "role": "system",
            "content": f"Use the following inventory data to answer the customer, if relevant:\n\n{car_context}"
        }

        messages = [SYSTEM_PROMPT, context_message]

        raw_history = redis_client.lrange(redis_key, 0, -1)
        if raw_history:
            messages.extend(json.loads(msg) for msg in raw_history)

        new_user_message = {"role": "user", "content": payload.message}
        messages.append(new_user_message)

        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKEN,
        )

        ai_response_content = response.choices[0].message.content
        new_assistant_message = {"role": "assistant", "content": ai_response_content}

        redis_client.rpush(redis_key, json.dumps(new_user_message))
        redis_client.rpush(redis_key, json.dumps(new_assistant_message))
        redis_client.expire(redis_key, SESSION_TTL)

        return ChatReponse(user_id=payload.user_id, message=ai_response_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/{user_id}")
async def clear_chat_memory(user_id: str):
    redis_key = f"chat_session:{user_id}"
    redis_client.delete(redis_key)
    return {"message": f"Chat memory cleared for user {user_id}."}