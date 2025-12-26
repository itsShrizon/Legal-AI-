# Bangla Legal AI (Documind)

A Production-grade RAG system for Question Answering on Bangla Legal Documents, built with FastAPI, PostgreSQL, Qdrant, and Local LLMs (Qwen/LlamaCPP).

## Features
- **GraphRAG**: Combines Vector Search with Graph-based Citation Analysis.
- **Local AI**: Runs custom `.pkl` embeddings and `.gguf` LLMs locally.
- **Full Stack**: User Auth, Chat History, Admin Ingestion.
- **Production Ready**: Dockerized, Metrics, Logging, Alembic Migrations.

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Models placed in `models/` directory:
    - `models/embedding_model.pkl`
    - `models/qwen-3.gguf`

## Setup

1. **Clone & Environment**
   ```bash
   cp .env.example .env
   # Update DATABASE_URL in .env with your Supabase Connection String
   # Format: postgresql://[user]:[password]@[host]:[port]/[postgres]?sslmode=require
   ```

2. **Start Infrastructure**
   ```bash
   docker-compose up -d --build
   ```

3. **Run Migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

## Usage

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Ingestion (Admin)
POST `/api/v1/admin/ingest` with a `.jsonl` file containing chunks.

## Testing
```bash
pytest
```
