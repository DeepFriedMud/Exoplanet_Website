# Exoplanet Explorer

A modern exoplanet discovery and analysis application built with FastAPI, SQLAlchemy, SQLite, and Jinja templates.

## Features

- Home dashboard with catalog statistics
- Planet explorer with filtering, sorting, and pagination
- Individual planet profiles with measurement provenance
- Synthetic demo data clearly marked for local development
- NASA Exoplanet Archive TAP ingestion for the confirmed composite-parameters catalog
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

## Import current NASA Exoplanet Archive catalog data

The importer queries the NASA Exoplanet Archive TAP synchronous endpoint and `pscomppars` table. That table contains confirmed planets with the Archive's selected composite parameter values; this importer does not import candidate objects.

From the repository root, with the virtual environment active:

```powershell
# Start with a manageable live sample (100 confirmed planets).
python -m exoplanet_app.ingest --limit 100

# Import all rows selected by default_flag=1.
python -m exoplanet_app.ingest --all
```

The default command imports at most 1,000 rows. The importer:

- creates missing tables without deleting or resetting the existing database;
- upserts planets, host stars, and systems by their Archive names;
- preserves existing values when an incoming row has a missing field;
- converts Earth-mass/Earth-radius fallbacks to the app's Jupiter units;
- stores representative values and asymmetric uncertainties as provenance measurements;
- keeps NASA measurements separate from other source measurements, and marks the latest NASA catalog value as preferred;
- records the successful retrieval time and row counts in `catalog_import_runs`.

For a real catalog view, set `USE_DEMO_DATA=false` in `.env` before starting the website. Existing synthetic demo rows are not deleted by the importer; they are only replaced for matching planet names where NASA catalog values are available. Back up your SQLite database before a full import.

NASA Archive attribution and TAP documentation: <https://exoplanetarchive.ipac.caltech.edu/docs/API_queries.html>. Parameter definitions: <https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html>.

## Testing

Run:
`pytest`

## Environment variables

See `.env.example`.
