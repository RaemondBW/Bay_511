"""
Custom integration to integrate Bay Area 511 Transit with Home Assistant.

For more details about this integration, please refer to
https://github.com/raemond/bay_511
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import Bay511ApiClient
from .const import (
    CONF_AGENCY,
    CONF_API_KEY,
    CONF_STOP_CODE,
    CONF_STOPS,
    DEFAULT_UPDATE_INTERVAL,
)
from .const import DOMAIN as DOMAIN
from .const import LOGGER as LOGGER
from .coordinator import Bay511DataUpdateCoordinator
from .data import Bay511Data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import Bay511ConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Bay511ConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    # Create API client
    client = Bay511ApiClient(
        api_key=entry.data[CONF_API_KEY],
        session=async_get_clientsession(hass),
    )

    # Create coordinators for each stop
    coordinators = {}
    for stop in entry.data[CONF_STOPS]:
        stop_key = f"{stop[CONF_AGENCY]}_{stop[CONF_STOP_CODE]}"
        coordinator = Bay511DataUpdateCoordinator(
            hass=hass,
            client=client,
            agency=stop[CONF_AGENCY],
            stop_code=stop[CONF_STOP_CODE],
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        coordinators[stop_key] = coordinator

        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()

    # Store runtime data
    entry.runtime_data = Bay511Data(
        client=client,
        coordinators=coordinators,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: Bay511ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: Bay511ConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

