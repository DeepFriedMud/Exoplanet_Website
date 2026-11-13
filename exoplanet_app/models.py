from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from exoplanet_app.db import Base


class HostStar(Base):
    __tablename__ = "host_stars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    alternate_names: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    spectral_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    effective_temperature_k: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mass_solar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radius_solar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    luminosity_solar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metallicity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    age_gy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_pc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    apparent_magnitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    systems: Mapped[list["PlanetarySystem"]] = relationship(back_populates="host_star")
    planets: Mapped[list["Planet"]] = relationship(back_populates="host_star")


class PlanetarySystem(Base):
    __tablename__ = "planetary_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    host_star_id: Mapped[int] = mapped_column(ForeignKey("host_stars.id"), nullable=False)
    architecture_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    host_star: Mapped[HostStar] = relationship(back_populates="systems")
    planets: Mapped[list["Planet"]] = relationship(back_populates="system")


class Planet(Base):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    system_id: Mapped[Optional[int]] = mapped_column(ForeignKey("planetary_systems.id"), nullable=True)
    host_star_id: Mapped[Optional[int]] = mapped_column(ForeignKey("host_stars.id"), nullable=True)
    discovery_status: Mapped[str] = mapped_column(String(50), default="Confirmed")
    discovery_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    discovery_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    orbital_period_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    semi_major_axis_au: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eccentricity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mass_jupiter: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radius_jupiter: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    density_g_cm3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    equilibrium_temperature_k: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    insolation_flux_earth: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inclination_deg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    argument_of_periastron_deg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    catalog_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    system: Mapped[Optional[PlanetarySystem]] = relationship(back_populates="planets")
    host_star: Mapped[Optional[HostStar]] = relationship(back_populates="planets")
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="planet")


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    arxiv_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    measurements: Mapped[list["Measurement"]] = relationship(back_populates="publication")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), index=True)
    publication_id: Mapped[Optional[int]] = mapped_column(ForeignKey("publications.id"), nullable=True)
    parameter_name: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lower_uncertainty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_uncertainty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    source_catalog: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    measured_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_direct_measurement: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    planet: Mapped[Planet] = relationship(back_populates="measurements")
    publication: Mapped[Optional[Publication]] = relationship(back_populates="measurements")
