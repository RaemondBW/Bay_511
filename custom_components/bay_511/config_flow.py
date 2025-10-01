"""Config flow for Bay Area 511 Transit."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    Bay511ApiClient,
    Bay511ApiClientAuthenticationError,
    Bay511ApiClientCommunicationError,
    Bay511ApiClientError,
)
from .const import (
    CONF_AGENCY,
    CONF_API_KEY,
    CONF_STOP_CODE,
    CONF_STOPS,
    DOMAIN,
    LOGGER,
)


class Bay511FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Bay Area 511."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._api_key: str | None = None
        self._stops: list[dict[str, str]] = []
        self._operators: list[dict[str, str]] = []

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        if user_input is not None:
            try:
                # Test the API key
                await self._test_api_key(user_input[CONF_API_KEY])
                self._api_key = user_input[CONF_API_KEY]
                # Move to stop configuration
                return await self.async_step_stops()

            except Bay511ApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "invalid_auth"
            except Bay511ApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "cannot_connect"
            except Bay511ApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY,
                        default=(user_input or {}).get(CONF_API_KEY, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def async_step_stops(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Configure stops to monitor."""
        _errors = {}

        if user_input is not None:
            # Add the stop to our list
            stop_entry = {
                CONF_AGENCY: user_input[CONF_AGENCY],
                CONF_STOP_CODE: user_input[CONF_STOP_CODE],
            }

            if user_input.get("add_another"):
                self._stops.append(stop_entry)
                # Show the form again for another stop
                return await self.async_step_stops()
            # Finish configuration
            if stop_entry[CONF_STOP_CODE]:  # Only add if stop code was provided
                self._stops.append(stop_entry)

            if not self._stops:
                _errors["base"] = "no_stops"
            else:
                # Create the config entry
                await self.async_set_unique_id(f"bay_511_{self._api_key[:8]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Bay Area 511 ({len(self._stops)} stops)",
                    data={
                        CONF_API_KEY: self._api_key,
                        CONF_STOPS: self._stops,
                    },
                )

        return self.async_show_form(
            step_id="stops",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AGENCY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_STOP_CODE): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        "add_another", default=False
                    ): selector.BooleanSelector(),
                },
            ),
            errors=_errors,
            description_placeholders={
                "stops_added": str(len(self._stops)),
            },
        )

    async def _test_api_key(self, api_key: str) -> None:
        """Validate API key by fetching operators list."""
        client = Bay511ApiClient(
            api_key=api_key,
            session=async_create_clientsession(self.hass),
        )
        # Try to get operators list to validate the API key
        self._operators = await client.async_get_operators()
