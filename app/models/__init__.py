"""
Модули моделей базы данных.
"""

from app.models.base import Base, TimestampMixin
from app.models.celestial_body import CelestialBody, BodyType, SpectralClass
from app.models.astronomer import Astronomer
from app.models.observation import Observation
from app.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "CelestialBody",
    "BodyType",
    "SpectralClass",
    "Astronomer",
    "Observation",
    "User"
]
