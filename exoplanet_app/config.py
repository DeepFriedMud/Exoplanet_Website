import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    app_name = os.getenv("APP_NAME", "Exoplanet Explorer")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./exoplanets.db")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    use_demo_data = os.getenv("USE_DEMO_DATA", "true").lower() == "true"


settings = Settings()
