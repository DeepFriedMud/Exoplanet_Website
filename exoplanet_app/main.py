from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from exoplanet_app.config import BASE_DIR, settings
from exoplanet_app.db import SessionLocal, engine, get_db
from exoplanet_app.models import HostStar, Planet, PlanetarySystem
from exoplanet_app.seed import seed_demo_data

app = FastAPI(
    title="Exoplanet Explorer",
    description="Interactive scientific exploration of exoplanets and planetary systems.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "exoplanet_app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "exoplanet_app" / "templates"))


@app.on_event("startup")
def startup_event() -> None:
    from exoplanet_app.db import Base

    Base.metadata.create_all(bind=engine)
    if settings.use_demo_data:
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    stats = get_catalog_stats(db)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "stats": stats, "synthetic_data": settings.use_demo_data},
    )


@app.get("/explorer", response_class=HTMLResponse)
def explorer_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("explorer.html", {"request": request})


@app.get("/planet/{planet_id}", response_class=HTMLResponse)
def planet_detail_page(request: Request, planet_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    planet = db.query(Planet).filter(Planet.id == planet_id).first()
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    measurements = [
        {
            "parameter_name": measurement.parameter_name,
            "value": measurement.value,
            "unit": measurement.unit,
            "lower_uncertainty": measurement.lower_uncertainty,
            "upper_uncertainty": measurement.upper_uncertainty,
            "method": measurement.method,
            "source_catalog": measurement.source_catalog,
            "is_preferred": measurement.is_preferred,
            "is_direct_measurement": measurement.is_direct_measurement,
        }
        for measurement in planet.measurements
    ]

    planet_payload = {
        "id": planet.id,
        "name": planet.name,
        "system_name": planet.system.name if planet.system else None,
        "host_star_name": planet.host_star.name if planet.host_star else None,
        "discovery_status": planet.discovery_status,
        "discovery_method": planet.discovery_method,
        "discovery_year": planet.discovery_year,
        "orbital_period_days": planet.orbital_period_days,
        "semi_major_axis_au": planet.semi_major_axis_au,
        "eccentricity": planet.eccentricity,
        "mass_jupiter": planet.mass_jupiter,
        "radius_jupiter": planet.radius_jupiter,
        "density_g_cm3": planet.density_g_cm3,
        "equilibrium_temperature_k": planet.equilibrium_temperature_k,
        "insolation_flux_earth": planet.insolation_flux_earth,
        "inclination_deg": planet.inclination_deg,
        "notes": planet.notes,
        "measurements": measurements,
    }

    return templates.TemplateResponse("planet_detail.html", {"request": request, "planet": planet_payload})


@app.get("/api/stats")
def catalog_stats(db: Session = Depends(get_db)):
    return get_catalog_stats(db)


@app.get("/api/exoplanets")
def list_planets(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, description="Search by planet or host star name"),
    discovery_method: Optional[str] = None,
    radius_min: Optional[float] = None,
    radius_max: Optional[float] = None,
    mass_min: Optional[float] = None,
    mass_max: Optional[float] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
):
    query = db.query(Planet).join(HostStar, Planet.host_star_id == HostStar.id, isouter=True)

    if q:
        query = query.filter(or_(Planet.name.ilike(f"%{q}%"), HostStar.name.ilike(f"%{q}%")))
    if discovery_method:
        query = query.filter(Planet.discovery_method == discovery_method)
    if radius_min is not None:
        query = query.filter(Planet.radius_jupiter >= radius_min)
    if radius_max is not None:
        query = query.filter(Planet.radius_jupiter <= radius_max)
    if mass_min is not None:
        query = query.filter(Planet.mass_jupiter >= mass_min)
    if mass_max is not None:
        query = query.filter(Planet.mass_jupiter <= mass_max)
    if year_min is not None:
        query = query.filter(Planet.discovery_year >= year_min)
    if year_max is not None:
        query = query.filter(Planet.discovery_year <= year_max)

    total = query.count()
    items = (
        query.order_by(Planet.discovery_year.desc().nullslast(), Planet.name.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "items": [
            {
                "id": planet.id,
                "name": planet.name,
                "host_star_name": planet.host_star.name if planet.host_star else None,
                "system_name": planet.system.name if planet.system else None,
                "discovery_status": planet.discovery_status,
                "discovery_method": planet.discovery_method,
                "discovery_year": planet.discovery_year,
                "orbital_period_days": planet.orbital_period_days,
                "semi_major_axis_au": planet.semi_major_axis_au,
                "mass_jupiter": planet.mass_jupiter,
                "radius_jupiter": planet.radius_jupiter,
                "equilibrium_temperature_k": planet.equilibrium_temperature_k,
            }
            for planet in items
        ],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max((total + per_page - 1) // per_page, 1),
    }


@app.get("/api/planet/{planet_id}")
def get_planet(planet_id: int, db: Session = Depends(get_db)):
    planet = db.query(Planet).filter(Planet.id == planet_id).first()
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    return {
        "id": planet.id,
        "name": planet.name,
        "system_name": planet.system.name if planet.system else None,
        "host_star_name": planet.host_star.name if planet.host_star else None,
        "discovery_status": planet.discovery_status,
        "discovery_method": planet.discovery_method,
        "discovery_year": planet.discovery_year,
        "orbital_period_days": planet.orbital_period_days,
        "semi_major_axis_au": planet.semi_major_axis_au,
        "eccentricity": planet.eccentricity,
        "mass_jupiter": planet.mass_jupiter,
        "radius_jupiter": planet.radius_jupiter,
        "density_g_cm3": planet.density_g_cm3,
        "equilibrium_temperature_k": planet.equilibrium_temperature_k,
        "insolation_flux_earth": planet.insolation_flux_earth,
        "inclination_deg": planet.inclination_deg,
        "notes": planet.notes,
        "measurements": [
            {
                "parameter_name": measurement.parameter_name,
                "value": measurement.value,
                "unit": measurement.unit,
                "lower_uncertainty": measurement.lower_uncertainty,
                "upper_uncertainty": measurement.upper_uncertainty,
                "method": measurement.method,
                "source_catalog": measurement.source_catalog,
                "is_preferred": measurement.is_preferred,
                "is_direct_measurement": measurement.is_direct_measurement,
            }
            for measurement in planet.measurements
        ],
    }


def get_catalog_stats(db: Session):
    total_planets = db.query(func.count(Planet.id)).scalar() or 0
    total_hosts = db.query(func.count(HostStar.id)).scalar() or 0

    system_counts = (
        db.query(Planet.system_id, func.count(Planet.id).label("count"))
        .filter(Planet.system_id.isnot(None))
        .group_by(Planet.system_id)
        .all()
    )
    multi_planet_systems = sum(1 for _, count in system_counts if count > 1)

    confirmed = db.query(func.count(Planet.id)).filter(Planet.discovery_status == "Confirmed").scalar() or 0
    candidate = db.query(func.count(Planet.id)).filter(Planet.discovery_status == "Candidate").scalar() or 0
    methods = (
        db.query(Planet.discovery_method, func.count(Planet.id))
        .filter(Planet.discovery_method.isnot(None))
        .group_by(Planet.discovery_method)
        .all()
    )

    return {
        "total_planets": total_planets,
        "total_hosts": total_hosts,
        "multi_planet_systems": multi_planet_systems,
        "confirmed_planets": confirmed,
        "candidate_planets": candidate,
        "discovery_methods": {method: count for method, count in methods},
        "synthetic_data": settings.use_demo_data,
    }


__all__ = ["app"]
