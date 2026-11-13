from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from exoplanet_app.db import Base
from exoplanet_app.models import HostStar, Measurement, Planet, PlanetarySystem, Publication


def seed_demo_data(db: Session) -> None:
    if db.query(Planet).count() > 0:
        return

    system_names = [
        ("TRAPPIST-1", "TRAPPIST-1"),
        ("Kepler-186", "Kepler-186"),
        ("HD 209458", "HD 209458"),
    ]

    for index, (star_name, system_name) in enumerate(system_names, start=1):
        star = HostStar(
            name=star_name,
            alternate_names=f"Synthetic star {index}",
            spectral_type="M8V" if index == 1 else "G0V",
            effective_temperature_k=2550 if index == 1 else 6092,
            mass_solar=0.09 if index == 1 else 1.18,
            radius_solar=0.12 if index == 1 else 1.19,
            luminosity_solar=0.0005 if index == 1 else 1.4,
            metallicity=0.04,
            distance_pc=39.5 if index == 1 else 159.0,
            apparent_magnitude=18.8 if index == 1 else 7.7,
            notes="Synthetic demonstration data; not NASA catalog data.",
        )
        db.add(star)
        db.flush()

        system = PlanetarySystem(name=system_name, host_star_id=star.id)
        db.add(system)
        db.flush()

        if system_name == "TRAPPIST-1":
            planet_names = [
                ("TRAPPIST-1 b", "Confirmed", "Transit", 2017, 1.51, 0.01154, 1.017, 1.374, 0.4, 400, 0.0),
                ("TRAPPIST-1 c", "Confirmed", "Transit", 2017, 2.42, 0.0158, 1.156, 1.308, 0.6, 341, 0.0),
                ("TRAPPIST-1 d", "Confirmed", "Transit", 2017, 4.05, 0.0223, 0.297, 0.778, 0.3, 282, 0.0),
            ]
        elif system_name == "Kepler-186":
            planet_names = [
                ("Kepler-186 f", "Confirmed", "Transit", 2014, 129.94, 0.432, 1.17, 1.11, 1.17, 202, 0.0),
                ("Kepler-186 d", "Confirmed", "Transit", 2014, 22.18, 0.11, 0.04, 0.12, 0.5, 642, 0.0),
            ]
        else:
            planet_names = [
                ("HD 209458 b", "Confirmed", "Transit", 1999, 3.52, 0.047, 0.69, 1.38, 1.33, 1459, 0.0),
            ]

        for planet_name, status, method, year, period, sma, ecc, mass, radius, density, temp, flux in planet_names:
            planet = Planet(
                name=planet_name,
                system_id=system.id,
                host_star_id=star.id,
                discovery_status=status,
                discovery_method=method,
                discovery_year=year,
                orbital_period_days=period,
                semi_major_axis_au=sma,
                eccentricity=ecc,
                mass_jupiter=mass,
                radius_jupiter=radius,
                density_g_cm3=density,
                equilibrium_temperature_k=temp,
                insolation_flux_earth=flux,
                catalog_source="Synthetic demo dataset",
                notes="Synthetic demonstration data. This is not NASA archive data.",
            )
            db.add(planet)
            db.flush()

            publication = Publication(
                title=f"Synthetic reference for {planet_name}",
                authors="Demo authors",
                publication_year=year,
                doi=None,
                arxiv_id=None,
                url="https://example.com/synthetic-reference",
                abstract="Synthetic measurement provenance for local prototype testing only.",
            )
            db.add(publication)
            db.flush()

            db.add(
                Measurement(
                    planet_id=planet.id,
                    publication_id=publication.id,
                    parameter_name="radius",
                    value=radius,
                    unit="R_jupiter",
                    lower_uncertainty=0.05,
                    upper_uncertainty=0.05,
                    method="Synthetic radius estimate",
                    source_catalog="Synthetic demo dataset",
                    is_preferred=True,
                    is_direct_measurement=True,
                )
            )
            db.add(
                Measurement(
                    planet_id=planet.id,
                    publication_id=publication.id,
                    parameter_name="mass",
                    value=mass,
                    unit="M_jupiter",
                    lower_uncertainty=0.05,
                    upper_uncertainty=0.05,
                    method="Synthetic mass estimate",
                    source_catalog="Synthetic demo dataset",
                    is_preferred=True,
                    is_direct_measurement=True,
                )
            )

    db.commit()
