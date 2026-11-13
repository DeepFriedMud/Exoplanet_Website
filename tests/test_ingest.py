from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from exoplanet_app.db import Base
from exoplanet_app.ingest import CATALOG_SOURCE, import_archive_rows
from exoplanet_app.models import CatalogImportRun, HostStar, Measurement, Planet


SAMPLE_ROW = {
    "pl_name": "Test-1 b",
    "hostname": "Test-1",
    "discoverymethod": "Transit",
    "disc_year": 2024,
    "pl_orbper": 3.5,
    "pl_orbpererr1": 0.2,
    "pl_orbpererr2": -0.1,
    "pl_bmasse": 317.82838,
    "pl_bmasseerr1": 31.782838,
    "pl_bmasseerr2": -15.891419,
    "pl_rade": 11.2089,
    "pl_radeerr1": 1.12089,
    "pl_radeerr2": -0.560445,
    "pl_eqt": 900,
    "st_teff": 5800,
    "st_mass": 1.0,
    "st_rad": 1.0,
    "sy_dist": 20.0,
    "sy_vmag": 10.2,
    "pl_bmassprov": "Msin(i)",
    "pl_refname": "https://example.org/reference",
    "rowupdate": "2026-01-02",
    "default_flag": 1,
}


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_archive_import_upserts_planet_star_and_system_and_is_idempotent():
    db = make_session()
    try:
        first = import_archive_rows(db, [SAMPLE_ROW], retrieved_at=datetime(2026, 1, 3))
        second = import_archive_rows(db, [SAMPLE_ROW], retrieved_at=datetime(2026, 1, 4))

        assert first == {"fetched": 1, "inserted": 1, "updated": 0, "skipped": 0}
        assert second == {"fetched": 1, "inserted": 0, "updated": 1, "skipped": 0}
        assert db.query(Planet).count() == 1
        assert db.query(HostStar).count() == 1
        assert db.query(CatalogImportRun).count() == 2

        planet = db.query(Planet).one()
        assert planet.discovery_status == "Confirmed"
        assert planet.mass_jupiter == 1.0
        assert planet.radius_jupiter == 1.0
        assert planet.system.name == "Test-1"

        mass = db.query(Measurement).filter_by(planet_id=planet.id, parameter_name="mass").one()
        assert mass.source_catalog == CATALOG_SOURCE
        assert mass.value == 1.0
        assert mass.lower_uncertainty == 0.05
        assert mass.upper_uncertainty == 0.1
        assert mass.is_preferred is True
        assert mass.is_direct_measurement is False
        assert "Msin(i)" in mass.notes
    finally:
        db.close()


def test_archive_import_preserves_other_sources_but_prefers_nasa_value():
    db = make_session()
    try:
        db.add(Planet(name="Test-1 b", discovery_status="Confirmed"))
        db.flush()
        planet = db.query(Planet).one()
        db.add(
            Measurement(
                planet_id=planet.id,
                parameter_name="radius",
                value=2.0,
                unit="R_jupiter",
                source_catalog="Other publication",
                is_preferred=True,
            )
        )
        db.commit()

        import_archive_rows(db, [SAMPLE_ROW])

        measurements = db.query(Measurement).filter_by(planet_id=planet.id, parameter_name="radius").all()
        assert len(measurements) == 2
        assert next(m for m in measurements if m.source_catalog == "Other publication").is_preferred is False
        assert next(m for m in measurements if m.source_catalog == CATALOG_SOURCE).is_preferred is True
    finally:
        db.close()


def test_import_skips_rows_without_planet_name_and_does_not_clear_missing_values():
    db = make_session()
    try:
        import_archive_rows(db, [SAMPLE_ROW])
        existing = dict(SAMPLE_ROW)
        existing["pl_radj"] = None
        existing["pl_rade"] = None
        existing["pl_eqt"] = None
        result = import_archive_rows(db, [{"hostname": "No planet name"}, existing])

        assert result["skipped"] == 1
        assert db.query(Planet).one().radius_jupiter == 1.0
        assert db.query(Planet).one().equilibrium_temperature_k == 900
    finally:
        db.close()
