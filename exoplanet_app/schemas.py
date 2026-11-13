from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class MeasurementOut(BaseModel):
    parameter_name: str
    value: Optional[float] = None
    unit: Optional[str] = None
    lower_uncertainty: Optional[float] = None
    upper_uncertainty: Optional[float] = None
    method: Optional[str] = None
    source_catalog: Optional[str] = None
    is_preferred: bool = False
    is_direct_measurement: bool = True


class PlanetSummary(BaseModel):
    id: int
    name: str
    system_name: Optional[str] = None
    host_star_name: Optional[str] = None
    discovery_status: str
    discovery_method: Optional[str] = None
    discovery_year: Optional[int] = None
    orbital_period_days: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    mass_jupiter: Optional[float] = None
    radius_jupiter: Optional[float] = None
    equilibrium_temperature_k: Optional[float] = None


class PlanetDetail(BaseModel):
    id: int
    name: str
    system_name: Optional[str] = None
    host_star_name: Optional[str] = None
    discovery_status: str
    discovery_method: Optional[str] = None
    discovery_year: Optional[int] = None
    orbital_period_days: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    eccentricity: Optional[float] = None
    mass_jupiter: Optional[float] = None
    radius_jupiter: Optional[float] = None
    density_g_cm3: Optional[float] = None
    equilibrium_temperature_k: Optional[float] = None
    insolation_flux_earth: Optional[float] = None
    inclination_deg: Optional[float] = None
    notes: Optional[str] = None
    measurements: List[MeasurementOut] = Field(default_factory=list)


class CatalogStats(BaseModel):
    total_planets: int
    total_hosts: int
    multi_planet_systems: int
    confirmed_planets: int
    candidate_planets: int
    discovery_methods: dict[str, int]
    synthetic_data: bool
