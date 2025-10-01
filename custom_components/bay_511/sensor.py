"""Sensor platform for Bay Area 511 Transit."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_AGENCY, CONF_STOP_CODE, CONF_STOPS, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import Bay511DataUpdateCoordinator
    from .data import Bay511ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: Bay511ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    entities = []

    for stop in entry.data[CONF_STOPS]:
        stop_key = f"{stop[CONF_AGENCY]}_{stop[CONF_STOP_CODE]}"
        coordinator = entry.runtime_data.coordinators[stop_key]

        # Create next arrival sensor
        entities.append(
            Bay511ArrivalSensor(
                coordinator=coordinator,
                agency=stop[CONF_AGENCY],
                stop_code=stop[CONF_STOP_CODE],
                arrival_index=0,  # First/next arrival
                description="next",
            )
        )

        # Create subsequent arrival sensor
        entities.append(
            Bay511ArrivalSensor(
                coordinator=coordinator,
                agency=stop[CONF_AGENCY],
                stop_code=stop[CONF_STOP_CODE],
                arrival_index=1,  # Second arrival
                description="subsequent",
            )
        )

    async_add_entities(entities)


class Bay511ArrivalSensor(CoordinatorEntity, SensorEntity):
    """Bay Area 511 Arrival Sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Bay511DataUpdateCoordinator,
        agency: str,
        stop_code: str,
        arrival_index: int,
        description: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._agency = agency
        self._stop_code = stop_code
        self._arrival_index = arrival_index
        self._description = description

        # Set unique ID
        self._attr_unique_id = f"{DOMAIN}_{agency}_{stop_code}_{description}_arrival"

        # Set entity ID
        self.entity_id = f"sensor.bay_511_{agency}_{stop_code}_{description}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        stop_name = self.coordinator.data.get("stop_name", f"Stop {self._stop_code}")
        return f"{stop_name} - {self._description.capitalize()} Arrival"

    @property
    def native_value(self) -> int | None:
        """Return minutes until arrival."""
        arrivals = self.coordinator.data.get("arrivals", [])
        if len(arrivals) > self._arrival_index:
            return arrivals[self._arrival_index].get("minutes_away")
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "min"

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:bus-clock"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        arrivals = self.coordinator.data.get("arrivals", [])

        if len(arrivals) > self._arrival_index:
            arrival = arrivals[self._arrival_index]
            return {
                "line": arrival.get("line_ref"),
                "destination": arrival.get("destination"),
                "direction": arrival.get("direction"),
                "expected_time": arrival.get("expected_arrival_time"),
                "aimed_time": arrival.get("aimed_arrival_time"),
                "vehicle_at_stop": arrival.get("vehicle_at_stop", False),
                "stop_name": self.coordinator.data.get("stop_name"),
                "stop_code": self._stop_code,
                "agency": self._agency,
            }

        return {
            "stop_name": self.coordinator.data.get("stop_name"),
            "stop_code": self._stop_code,
            "agency": self._agency,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None
