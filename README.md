# True Value Cars — AI Sales Assistant (RAG Chat App)

A retrieval-augmented generation (RAG) chat application that simulates an AI sales manager for a used-car showroom. The assistant holds natural, context-aware conversations, remembers session history, and grounds its responses in real inventory data using semantic search — instead of hallucinating car details.

Built to explore the core architecture behind production LLM applications: stateless model calls, externally managed conversational memory, and vector-based retrieval.

## What it does

A user chats with an AI "Sales Manager" persona about buying a used car. The assistant:

- Remembers the ongoing conversation across turns (session-based memory)
- Retrieves relevant cars from a real inventory database based on the user's query
- Responds using actual pricing, mileage, and condition data — not made-up details
- Runs as a fully containerized service (FastAPI + Postgres + Redis)

## Architecture

```
User message
  │
  ▼
Embed query (OpenAI text-embedding-3-small)
  │
  ▼
Vector similarity search (PostgreSQL + pgvector)
  │
  ▼
Build context: persona prompt + retrieved inventory + conversation history (Redis)
  │
  ▼
Chat completion (OpenAI, async)
  │
  ▼
Store new turn in Redis → Return response to user
```

**Key design decisions:**

- **Stateless LLM calls, external memory** — every request reconstructs the full message context from Redis; the model itself holds no state between calls.
- **Retrieval is query-scoped, not stored** — inventory context is fetched fresh on every turn based on the current message, keeping responses grounded in up-to-date data rather than stale cached context.
- **Session-based, auto-expiring memory** — conversations are keyed per user in Redis with a TTL, so idle sessions clean themselves up automatically.

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI (async) |
| LLM | OpenAI (`gpt-4o-mini`) |
| Embeddings | OpenAI (`text-embedding-3-small`) |
| Vector search | PostgreSQL + pgvector |
| Conversation memory | Redis |
| Containerization | Docker, Docker Compose |

## Running locally

**Requirements:** Docker, Docker Compose, an OpenAI API key.

1. Clone the repo and add your environment variables:
   ```bash
   cp .env.sample .env
   # then add your OPENAI_API_KEY
   ```

2. Start the stack:
   ```bash
   docker compose up --build
   ```

3. Set up the database schema and seed sample inventory (one-time):
   ```bash
   python scripts/create_dummy-data.py
   ```

4. Chat with the assistant:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test1", "message": "Do you have any SUVs under 10 lakhs?"}'
   ```

5. Clear a session's memory:
   ```bash
   curl -X DELETE http://localhost:8000/chat/test1
   ```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/chat` | POST | Send a message, get a grounded, context-aware response |
| `/chat/{user_id}` | DELETE | Clear a user's conversation history |

## What I learned building this

This project was a hands-on introduction to applied LLM engineering, moving from a basic API wrapper to a working retrieval-augmented system:

- How LLM APIs are inherently stateless, and how conversational memory is actually just externally managed context reconstruction
- How vector embeddings capture semantic meaning, enabling retrieval that matches intent rather than keywords
- Practical trade-offs in RAG design — e.g., retrieving based on the latest message alone is simple but limited (a known next improvement is retrieving based on recent conversation context, not just the last message)
- Containerizing a multi-service application (API, vector database, cache) for reproducible local development

## Possible next steps

- Multi-turn-aware retrieval (use recent conversation context, not just the latest message, to search inventory)
- Function/tool calling — e.g., letting the model check live availability or book a test drive
- Automated retrieval evaluation against a test query set
- Streaming responses for a more natural chat experience

---

Built by Azhar KS as part of a hands-on transition into Applied AI / LLM engineering.