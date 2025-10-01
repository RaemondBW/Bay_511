"""DataUpdateCoordinator for Bay Area 511 Transit."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    Bay511ApiClientAuthenticationError,
    Bay511ApiClientError,
)
from .const import LOGGER

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from .api import Bay511ApiClient


class Bay511DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the 511 API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Bay511ApiClient,
        agency: str,
        stop_code: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"Bay 511 Stop {stop_code}",
            update_interval=update_interval,
        )
        self.client = client
        self.agency = agency
        self.stop_code = stop_code

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.client.async_get_stop_monitoring(
                self.agency, self.stop_code
            )
        except Bay511ApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except Bay511ApiClientError as exception:
            raise UpdateFailed(exception) from exception

