# True Value Cars — AI Sales Assistant (RAG Chat App)

A retrieval-augmented generation (RAG) chat application that simulates an AI sales manager for a used-car showroom. The assistant holds natural, context-aware conversations, remembers session history, and grounds its responses in real inventory data using semantic search — instead of hallucinating car details.

Built to explore the core architecture behind production LLM applications: stateless model calls, externally managed conversational memory, and vector-based retrieval.

## What it does

A user chats with an AI "Sales Manager" persona about buying a used car. The assistant:

- Remembers the ongoing conversation across turns (session-based memory)
- Dynamically uses **Tool Calling (Function Calling)** to retrieve relevant cars via semantic search or check live availability for specific vehicles
- Responds using actual pricing, mileage, and condition data — not made-up details
- Built on a modular, production-ready **FastAPI Layered Architecture**
- Runs as a fully containerized service (FastAPI + Postgres + Redis)

## Architecture

Our application uses a clean **Layered Architecture** (`core`, `api`, `services`, `tools`) and augments the LLM with dynamic tool calling capabilities.

```text
User message
  │
  ▼
Load conversation history (Redis) & inject Persona System Prompt
  │
  ▼
Chat completion (OpenAI, async) with injected Tool Schema (search_cars, check_availability)
  │
  ├──► [If model decides to call tool]
  │    └──► Execute Tool (e.g., Vector Search via PostgreSQL / pgvector)
  │    └──► Append tool result to context & trigger second Chat completion
  │
  ▼
Store new turn in Redis → Return response to user
```

**Key design decisions:**

- **Layered Structure** — clean separation of concerns using routers, service classes, schemas, and a central tool registry.
- **Dynamic Tool Calling** — instead of hardcoded RAG, the LLM makes autonomous decisions to invoke tools (`search_cars` for semantic search, `check_availability` for specific stock lookups). 
- **Stateless LLM calls, external memory** — every request reconstructs the full message context from Redis; the model itself holds no state between calls.
- **Session-based, auto-expiring memory** — conversations are keyed per user in Redis with a TTL, so idle sessions clean themselves up automatically.
- **Automated Evaluations** — dedicated eval scripts testing retrieval and tool-calling accuracy.

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
- Additional Tool Integrations — e.g., letting the model book a test drive or schedule an appointment
- Comprehensive CI/CD integration for the evaluation test sets
- Streaming responses for a more natural chat experience

---

Built by Azhar KS as part of a hands-on transition into Applied AI / LLM engineering.