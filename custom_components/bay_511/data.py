"""Custom types for Bay Area 511 Transit integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import Bay511ApiClient
    from .coordinator import Bay511DataUpdateCoordinator


type Bay511ConfigEntry = ConfigEntry[Bay511Data]


@dataclass
class Bay511Data:
    """Data for the Bay Area 511 integration."""

    client: Bay511ApiClient
    coordinators: dict[str, Bay511DataUpdateCoordinator]  # One coordinator per stop
    integration: Integration