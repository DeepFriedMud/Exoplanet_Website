"""Import confirmed composite parameters from the NASA Exoplanet Archive TAP service.

Run from the repository root with ``python -m exoplanet_app.ingest --limit 100``.
The default is a bounded sample; pass ``--all`` to request the full current table.
"""

from __future__ import annotations

import argparse
import math
from datetime import datetime
from typing import Any, Iterable

import requests
from sqlalchemy.orm import Session

from exoplanet_app.db import Base, SessionLocal, engine
from exoplanet_app.models import CatalogImportRun, HostStar, Measurement, Planet, PlanetarySystem

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
CATALOG_SOURCE = "NASA Exoplanet Archive: pscomppars"
EARTH_MASSES_PER_JUPITER = 317.82838
EARTH_RADII_PER_JUPITER = 11.2089
REQUEST_TIMEOUT_SECONDS = 60
MAX_LIMIT = 100_000

# NASA Archive uncertainties use err1 for the upper error and err2 for the lower
# error (usually negative). Keep the signs normalized in Measurement.
PLANET_PARAMETERS = {
    "orbital_period": ("pl_orbper", "pl_orbpererr1", "pl_orbpererr2", "day"),
    "semi_major_axis": ("pl_orbsmax", "pl_orbsmaxerr1", "pl_orbsmaxerr2", "AU"),
    "eccentricity": ("pl_orbeccen", "pl_orbeccenerr1", "pl_orbeccenerr2", "dimensionless"),
    "mass": ("pl_bmassj", "pl_bmassjerr1", "pl_bmassjerr2", "M_jupiter"),
    "radius": ("pl_radj", "pl_radjerr1", "pl_radjerr2", "R_jupiter"),
    "density": ("pl_dens", "pl_denserr1", "pl_denserr2", "g/cm^3"),
    "equilibrium_temperature": ("pl_eqt", "pl_eqterr1", "pl_eqterr2", "K"),
    "insolation_flux": ("pl_insol", "pl_insolerr1", "pl_insolerr2", "F_earth"),
    "inclination": ("pl_orbincl", "pl_orbinclerr1", "pl_orbinclerr2", "degree"),
    "argument_of_periastron": ("pl_orblper", "pl_orblpererr1", "pl_orblpererr2", "degree"),
}

PLANET_COLUMN_FIELDS = {
    "pl_orbper": ("orbital_period_days", "day"),
    "pl_orbsmax": ("semi_major_axis_au", "AU"),
    "pl_orbeccen": ("eccentricity", "dimensionless"),
    "pl_bmassj": ("mass_jupiter", "M_jupiter"),
    "pl_radj": ("radius_jupiter", "R_jupiter"),
    "pl_dens": ("density_g_cm3", "g/cm^3"),
    "pl_eqt": ("equilibrium_temperature_k", "K"),
    "pl_insol": ("insolation_flux_earth", "F_earth"),
    "pl_orbincl": ("inclination_deg", "degree"),
    "pl_orblper": ("argument_of_periastron_deg", "degree"),
}

TAP_COLUMNS = (
    "pl_name, hostname, discoverymethod, disc_year, pl_orbper, pl_orbpererr1, pl_orbpererr2, "
    "pl_orbsmax, pl_orbsmaxerr1, pl_orbsmaxerr2, pl_orbeccen, pl_orbeccenerr1, pl_orbeccenerr2, "
    "pl_bmassj, pl_bmassjerr1, pl_bmassjerr2, pl_bmasse, pl_bmasseerr1, pl_bmasseerr2, "
    "pl_radj, pl_radjerr1, pl_radjerr2, pl_rade, pl_radeerr1, pl_radeerr2, "
    "pl_dens, pl_denserr1, pl_denserr2, pl_eqt, pl_eqterr1, pl_eqterr2, "
    "pl_insol, pl_insolerr1, pl_insolerr2, pl_orbincl, pl_orbinclerr1, pl_orbinclerr2, "
    "pl_orblper, pl_orblpererr1, pl_orblpererr2, pl_bmassprov, pl_refname, rowupdate, "
    "st_spectype, st_teff, st_mass, st_rad, st_met, st_age, sy_dist, sy_vmag, sy_pnum, default_flag"
)


def build_tap_query(limit: int | None = 1000) -> str:
    """Return a bounded ADQL query for the Archive's confirmed composite catalog."""
    if limit is not None and (isinstance(limit, bool) or limit < 1 or limit > MAX_LIMIT):
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}, or None for all rows")
    query = (
        f"SELECT {TAP_COLUMNS} FROM pscomppars "
        "WHERE default_flag = 1 AND pl_name IS NOT NULL ORDER BY pl_name"
    )
    return f"{query} TOP {limit}" if False else (
        f"SELECT TOP {limit} {TAP_COLUMNS} FROM pscomppars "
        "WHERE default_flag = 1 AND pl_name IS NOT NULL ORDER BY pl_name"
        if limit is not None
        else query
    )


def fetch_nasa_exoplanet_archive(
    limit: int | None = 1000,
    *,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Fetch JSON rows from NASA's synchronous TAP endpoint.

    ``pscomppars`` contains confirmed planets with a selected composite parameter set;
    it is not the candidates table. An omitted limit requests all matching rows.
    """
    client = session or requests
    response = client.get(
        NASA_TAP_URL,
        params={"query": build_tap_query(limit), "format": "json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    raise ValueError("NASA TAP response was not a JSON row list")


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _integer(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value).strip()
    return result if result and result.lower() not in {"nan", "null", "none"} else None


def _parameter_values(row: dict[str, Any]) -> dict[str, tuple[float, float | None, float | None, str]]:
    """Normalize archive property values and asymmetric uncertainties to app units."""
    values: dict[str, tuple[float, float | None, float | None, str]] = {}
    for name, (value_key, upper_key, lower_key, unit) in PLANET_PARAMETERS.items():
        raw_value = _number(row.get(value_key))
        scale = 1.0

        # Convert Earth-unit fallback columns to the Jupiter units used by Planet.
        if name == "mass" and raw_value is None:
            raw_value = _number(row.get("pl_bmasse"))
            value_key, upper_key, lower_key = "pl_bmasse", "pl_bmasseerr1", "pl_bmasseerr2"
            scale = 1.0 / EARTH_MASSES_PER_JUPITER
        elif name == "radius" and raw_value is None:
            raw_value = _number(row.get("pl_rade"))
            value_key, upper_key, lower_key = "pl_rade", "pl_radeerr1", "pl_radeerr2"
            scale = 1.0 / EARTH_RADII_PER_JUPITER

        if raw_value is None:
            continue
        upper = _number(row.get(upper_key))
        lower = _number(row.get(lower_key))
        values[name] = (
            raw_value * scale,
            abs(lower) * scale if lower is not None else None,
            abs(upper) * scale if upper is not None else None,
            unit,
        )
    return values


def _set_if_present(target: Any, attribute: str, value: Any) -> None:
    # Catalog updates can omit values. Preserve a previously known value rather than
    # replacing it with NULL on a later partial response.
    if value is not None:
        setattr(target, attribute, value)


def import_archive_rows(
    db: Session,
    rows: Iterable[dict[str, Any]],
    *,
    retrieved_at: datetime | None = None,
) -> dict[str, int]:
    """Idempotently upsert rows and representative catalog measurements.

    Updates existing NASA-sourced representative values but preserves other
    publications' measurements as non-preferred provenance records.
    """
    rows = list(rows)
    retrieved_at = retrieved_at or datetime.utcnow()
    counts = {"fetched": len(rows), "inserted": 0, "updated": 0, "skipped": 0}
    touched: list[tuple[Planet, dict[str, Any], dict[str, tuple[float, float | None, float | None, str]]]] = []

    try:
        for row in rows:
            name = _text(row.get("pl_name"))
            if not name:
                counts["skipped"] += 1
                continue

            hostname = _text(row.get("hostname"))
            star = None
            system = None
            if hostname:
                star = db.query(HostStar).filter(HostStar.name == hostname).one_or_none()
                if star is None:
                    star = HostStar(name=hostname)
                    db.add(star)
                    db.flush()

                for column, attribute in (
                    ("st_spectype", "spectral_type"),
                    ("st_teff", "effective_temperature_k"),
                    ("st_mass", "mass_solar"),
                    ("st_rad", "radius_solar"),
                    ("st_met", "metallicity"),
                    ("st_age", "age_gy"),
                    ("sy_dist", "distance_pc"),
                    ("sy_vmag", "apparent_magnitude"),
                ):
                    value = _text(row.get(column)) if column == "st_spectype" else _number(row.get(column))
                    _set_if_present(star, attribute, value)

                system = db.query(PlanetarySystem).filter(PlanetarySystem.name == hostname).one_or_none()
                if system is None:
                    system = PlanetarySystem(name=hostname, host_star=star)
                    db.add(system)
                    db.flush()
                elif system.host_star_id != star.id:
                    system.host_star = star

            planet = db.query(Planet).filter(Planet.name == name).one_or_none()
            is_new = planet is None
            if planet is None:
                planet = Planet(name=name, discovery_status="Confirmed")
                db.add(planet)
                counts["inserted"] += 1
            else:
                counts["updated"] += 1

            planet.discovery_status = "Confirmed"
            planet.catalog_source = CATALOG_SOURCE
            _set_if_present(planet, "host_star", star)
            _set_if_present(planet, "system", system)
            _set_if_present(planet, "discovery_method", _text(row.get("discoverymethod")))
            _set_if_present(planet, "discovery_year", _integer(row.get("disc_year")))

            param_values = _parameter_values(row)
            # The catalog's mass in Earth masses is a fallback when its Jupiter-mass
            # value is absent. Populate the current-value field with the same unit.
            if "mass" in param_values:
                planet.mass_jupiter = param_values["mass"][0]
            if "radius" in param_values:
                planet.radius_jupiter = param_values["radius"][0]
            for column, (attribute, _unit) in PLANET_COLUMN_FIELDS.items():
                if column in {"pl_bmassj", "pl_radj"}:
                    continue
                value = _number(row.get(column))
                if value is not None:
                    setattr(planet, attribute, value)

            # Keep archive publication references and row-update timestamps attached
            # to each value as provenance; no bibliographic metadata is inferred.
            touched.append((planet, row, param_values))

        db.flush()
        planet_ids = {planet.id for planet, _, _ in touched}
        known_parameters = {parameter for parameter, _ in PLANET_PARAMETERS.items()}
        existing_measurements = (
            db.query(Measurement)
            .filter(
                Measurement.planet_id.in_(planet_ids),
                Measurement.parameter_name.in_(known_parameters),
            )
            .all()
            if planet_ids
            else []
        )
        measurement_map = {
            (measurement.planet_id, measurement.parameter_name, measurement.source_catalog): measurement
            for measurement in existing_measurements
        }
        preferred_map: dict[tuple[int, str], list[Measurement]] = {}
        for measurement in existing_measurements:
            if measurement.is_preferred:
                preferred_map.setdefault((measurement.planet_id, measurement.parameter_name), []).append(measurement)

        for planet, row, param_values in touched:
            row_reference = _text(row.get("pl_refname"))
            row_updated = _text(row.get("rowupdate"))
            mass_provenance = _text(row.get("pl_bmassprov"))
            for parameter, (value, lower, upper, unit) in param_values.items():
                for prior in preferred_map.get((planet.id, parameter), []):
                    if prior.source_catalog != CATALOG_SOURCE:
                        prior.is_preferred = False

                key = (planet.id, parameter, CATALOG_SOURCE)
                measurement = measurement_map.get(key)
                if measurement is None:
                    measurement = Measurement(
                        planet_id=planet.id,
                        parameter_name=parameter,
                        source_catalog=CATALOG_SOURCE,
                    )
                    db.add(measurement)
                    measurement_map[key] = measurement
                measurement.value = value
                measurement.unit = unit
                measurement.lower_uncertainty = lower
                measurement.upper_uncertainty = upper
                measurement.method = "NASA Exoplanet Archive composite parameters"
                measurement.measured_at = retrieved_at
                measurement.is_preferred = True
                # Composite catalog parameters may be derived from multiple methods;
                # do not label them as direct observations.
                measurement.is_direct_measurement = False
                notes = [f"Archive table: pscomppars; retrieved: {retrieved_at.isoformat()}Z"]
                if row_reference:
                    notes.append(f"Archive reference: {row_reference}")
                if row_updated:
                    notes.append(f"Archive row updated: {row_updated}")
                if parameter == "mass" and mass_provenance:
                    notes.append(f"Archive mass provenance: {mass_provenance}")
                measurement.notes = "; ".join(notes)

        run = CatalogImportRun(
            source=CATALOG_SOURCE,
            retrieved_at=retrieved_at,
            completed_at=datetime.utcnow(),
            records_fetched=counts["fetched"],
            records_inserted=counts["inserted"],
            records_updated=counts["updated"],
            records_skipped=counts["skipped"],
            status="completed",
        )
        db.add(run)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return counts


def run_import(*, limit: int | None = 1000) -> dict[str, int]:
    """Create missing tables, download Archive rows, then import them transactionally."""
    Base.metadata.create_all(bind=engine)
    rows = fetch_nasa_exoplanet_archive(limit=limit)
    db = SessionLocal()
    try:
        return import_archive_rows(db, rows)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import confirmed planets from NASA Exoplanet Archive TAP.")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--limit", type=int, default=1000, help=f"maximum rows to import (1-{MAX_LIMIT}; default: 1000)")
    selection.add_argument("--all", action="store_true", help="import all rows in pscomppars with default_flag=1")
    args = parser.parse_args()
    limit = None if args.all else args.limit
    try:
        result = run_import(limit=limit)
    except (requests.RequestException, ValueError) as error:
        parser.error(f"NASA Archive import failed: {error}")
    print(
        "NASA Exoplanet Archive import complete: "
        f"{result['inserted']} inserted, {result['updated']} updated, "
        f"{result['skipped']} skipped ({result['fetched']} rows fetched)."
    )


if __name__ == "__main__":
    main()
