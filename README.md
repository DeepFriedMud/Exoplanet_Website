# Exoplanet Explorer

A modern exoplanet discovery and analysis application built with FastAPI, SQLAlchemy, SQLite, and Jinja templates.

## Features

- Home dashboard with catalog statistics
- Planet explorer with filtering, sorting, and pagination
- Individual planet profiles with measurement provenance
- Synthetic demo data clearly marked for local development
- NASA Exoplanet Archive TAP ingestion scaffold
- Automated tests

## Local development

1. Create and activate a virtual environment:
   - Windows PowerShell:
     `python -m venv .venv`
     `.\.venv\Scripts\Activate.ps1`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy environment settings:
   `copy .env.example .env`
4. Start the app:
   `uvicorn exoplanet_app.main:app --reload`
5. Open:
   `http://localhost:8000`

## Project notes

- The app uses SQLite for local development and is designed for future PostgreSQL migration.
- Synthetic development data is inserted when the database is empty and is clearly labeled.
- Real NASA Exoplanet Archive data can be ingested via the TAP helper in `exoplanet_app/ingest.py`.

## Testing

Run:
`pytest`

## Environment variables

See `.env.example`.
