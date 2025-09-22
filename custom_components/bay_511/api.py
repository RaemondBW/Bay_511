"""Bay Area 511 API Client."""

from __future__ import annotations

import socket
from typing import Any
from datetime import datetime
import xml.etree.ElementTree as ET

import aiohttp
import async_timeout

from .const import API_BASE_URL, LOGGER


class Bay511ApiClientError(Exception):
    """Exception to indicate a general API error."""


class Bay511ApiClientCommunicationError(Bay511ApiClientError):
    """Exception to indicate a communication error."""


class Bay511ApiClientAuthenticationError(Bay511ApiClientError):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid API key"
        raise Bay511ApiClientAuthenticationError(msg)
    response.raise_for_status()


class Bay511ApiClient:
    """Bay Area 511 API Client."""

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize Bay Area 511 API Client."""
        self._api_key = api_key
        self._session = session

    async def async_get_stop_monitoring(
        self, agency: str, stop_code: str
    ) -> dict[str, Any]:
        """Get stop monitoring data for a specific stop."""
        params = {
            "api_key": self._api_key,
            "agency": agency,
            "stopcode": stop_code,
            "format": "json",
        }

        data = await self._api_wrapper(
            method="get",
            url=f"{API_BASE_URL}/StopMonitoring",
            params=params,
        )

        return self._parse_stop_monitoring(data)

    async def async_get_operators(self) -> list[dict[str, str]]:
        """Get list of transit operators."""
        params = {
            "api_key": self._api_key,
            "format": "json",
        }

        return await self._api_wrapper(
            method="get",
            url=f"{API_BASE_URL}/operators",
            params=params,
        )

    async def async_get_stops_for_operator(self, operator_id: str) -> list[dict[str, Any]]:
        """Get stops for a specific operator."""
        params = {
            "api_key": self._api_key,
            "operator_id": operator_id,
            "format": "json",
        }

        return await self._api_wrapper(
            method="get",
            url=f"{API_BASE_URL}/stops",
            params=params,
        )

    def _parse_stop_monitoring(self, data: dict) -> dict[str, Any]:
        """Parse stop monitoring response into a more usable format."""
        result = {
            "stop_name": None,
            "stop_code": None,
            "arrivals": [],
        }

        try:
            # Navigate through the nested JSON structure
            service_delivery = data.get("ServiceDelivery", {})
            stop_monitoring = service_delivery.get("StopMonitoringDelivery", {})

            if stop_monitoring and "MonitoredStopVisit" in stop_monitoring:
                visits = stop_monitoring["MonitoredStopVisit"]

                # Handle both single visit and list of visits
                if not isinstance(visits, list):
                    visits = [visits]

                for visit in visits:
                    monitored_vehicle = visit.get("MonitoredVehicleJourney", {})

                    # Extract stop info (same for all visits)
                    if result["stop_name"] is None:
                        result["stop_name"] = monitored_vehicle.get("MonitoredCall", {}).get("StopPointName")
                        result["stop_code"] = monitored_vehicle.get("MonitoredCall", {}).get("StopPointRef")

                    # Extract arrival info
                    arrival_info = {
                        "line_ref": monitored_vehicle.get("LineRef"),
                        "direction": monitored_vehicle.get("DirectionRef"),
                        "destination": monitored_vehicle.get("DestinationName"),
                        "aimed_arrival_time": monitored_vehicle.get("MonitoredCall", {}).get("AimedArrivalTime"),
                        "expected_arrival_time": monitored_vehicle.get("MonitoredCall", {}).get("ExpectedArrivalTime"),
                        "vehicle_at_stop": monitored_vehicle.get("MonitoredCall", {}).get("VehicleAtStop", False),
                    }

                    # Calculate minutes until arrival
                    if arrival_info["expected_arrival_time"]:
                        try:
                            expected = datetime.fromisoformat(arrival_info["expected_arrival_time"].replace("Z", "+00:00"))
                            now = datetime.now(expected.tzinfo)
                            minutes_away = int((expected - now).total_seconds() / 60)
                            arrival_info["minutes_away"] = max(0, minutes_away)  # Don't show negative times
                        except Exception as e:
                            LOGGER.debug("Could not calculate minutes away: %s", e)
                            arrival_info["minutes_away"] = None
                    else:
                        arrival_info["minutes_away"] = None

                    result["arrivals"].append(arrival_info)

        except Exception as e:
            LOGGER.error("Error parsing stop monitoring data: %s", e)

        return result

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )
                _verify_response_or_raise(response)

                # Get text response to handle BOM
                text = await response.text()

                # Remove BOM if present
                if text.startswith('\ufeff'):
                    text = text[1:]

                # Parse JSON manually
                import json
                return json.loads(text)

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise Bay511ApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise Bay511ApiClientCommunicationError(msg) from exception
        except json.JSONDecodeError as exception:
            msg = f"Invalid JSON response from API - {exception}"
            raise Bay511ApiClientError(msg) from exception
        except Exception as exception:
            msg = f"Something really wrong happened! - {exception}"
            raise Bay511ApiClientError(msg) from exception