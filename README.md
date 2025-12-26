# home-service-member

JARAM member management service built with FastAPI.

## Development Setup

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
├── main.py                      # FastAPI app entry point
├── database.py                  # DB connection setup
├── config.py                    # Environment variables and configuration
├── models/                      # ORM models
├── schemas/                     # Pydantic schemas
├── repositories/                # Database queries
├── services/                    # Business logic
├── routers/                     # API endpoints
└── utils/                       # Utilities
```
