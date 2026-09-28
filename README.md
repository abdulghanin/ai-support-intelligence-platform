# AI Support Intelligence Platform

A customer support AI project built step by step with Python, FastAPI, PostgreSQL, and Qdrant.

## Current Features

- `POST /chat`: normalize and save a customer message, classify its intent, retrieve a relevant document, and return an answer with its source.
- `POST /documents`: add a support document to Qdrant.
- `GET /search`: search support documents using multilingual embeddings.
- `POST /feedback`: save a 1–5 rating for an existing message.
- `GET /health`: check that the API process is running.

## Current Architecture

```text
Customer message
  -> FastAPI
  -> Rule-based intent classification
  -> PostgreSQL message storage
  -> Multilingual embedding model
  -> Qdrant document retrieval
  -> Answer provider
  -> Answer with source
```

The default `demo` answer provider returns text from the retrieved document. The LLM provider interface includes OpenAI, Gemini, and Anthropic adapters, but live provider calls have not yet been verified.

## Requirements

- Python 3.14 for the current development environment
- `uv`
- Docker and Docker Compose

## Local Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create a local `.env` file. Use your own PostgreSQL password:

   ```text
   POSTGRES_PASSWORD=YOUR_LOCAL_PASSWORD
   DATABASE_URL=postgresql+psycopg://support:YOUR_LOCAL_PASSWORD@127.0.0.1:5432/support_db
   LLM_PROVIDER=demo
   ```

   Do not commit `.env` or API keys.

3. Start PostgreSQL and Qdrant:

   ```bash
   docker compose up -d
   docker compose ps
   ```

4. Start the API:

   ```bash
   PYTHONPATH=src uv run --env-file .env uvicorn support_intelligence.api:app --host 127.0.0.1 --port 8000
   ```

5. Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

The multilingual embedding model is downloaded on first use and may take some time.

## Example Requests

Add a document:

```bash
curl -X POST http://127.0.0.1:8000/documents \
  -H 'Content-Type: application/json' \
  -d '{"text":"Customers can track an order from their account page.","source":"order-help"}'
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"How can I track my order?"}'
```

Run the current tests:

```bash
PYTHONPATH=src uv run --env-file .env python -m unittest discover -s tests -v
```

## Current Limitations

- Intent classification uses keyword rules; an ML model is planned.
- The `demo` provider returns retrieved text rather than generating a new answer.
- Retrieval scores and the answer threshold have not been calibrated on an evaluation dataset.
- Database tables are created at startup; migrations are not implemented yet.
- The current tests cover basic setup only, not the API or retrieval pipeline.
- Authentication, rate limiting, monitoring, CI/CD, and cloud deployment are not implemented yet.