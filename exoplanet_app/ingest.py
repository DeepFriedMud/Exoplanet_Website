from __future__ import annotations

from typing import Any

import requests

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def fetch_nasa_exoplanet_archive(limit: int = 50) -> list[dict[str, Any]]:
    """Fetch a small sample of archive data. This is a safe ingestion scaffold for future real catalog loads.

    The query requests only a few recommended columns from the NASA Exoplanet Archive TAP service.
    """
    query = (
        "SELECT pl_name, hostname, discoverymethod, disc_year, pl_radj, pl_massj,"
        " pl_dens, teq, fsai, sy_pnum, rowupdate"
        " FROM pscomppars"
        " WHERE default_flag = 1"
        f" LIMIT {limit}"
    )
    response = requests.get(
        NASA_TAP_URL,
        params={"QUERY": query, "FORMAT": "json"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return []
