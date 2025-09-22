# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for Bay Area 511 Transit that provides real-time arrival predictions for public transit stops using the 511.org API.

## Architecture

The integration follows Home Assistant's standard custom component structure:

- **Entry Point**: `custom_components/bay_511/__init__.py` - Manages integration setup, creates coordinators for each stop
- **Config Flow**: `custom_components/bay_511/config_flow.py` - Two-step configuration: API key validation, then stop configuration
- **Data Coordinator**: `custom_components/bay_511/coordinator.py` - One coordinator per stop for efficient data fetching
- **API Client**: `custom_components/bay_511/api.py` - Handles 511.org API communication, parses SIRI format responses
- **Sensor Platform**: `custom_components/bay_511/sensor.py` - Creates arrival prediction sensors (next and subsequent)
- **Data Models**: `custom_components/bay_511/data.py` - Type definitions and runtime data structures

Key design decisions:
- One coordinator per stop (rather than global) for independent update cycles
- Two sensors per stop (next and subsequent arrivals) for better automation flexibility
- JSON format preferred over XML for API responses
- 60-second default update interval to stay within API rate limits

## 511 API Details

- Base URL: `https://api.511.org/transit`
- Authentication: API key passed as URL parameter
- Rate limit: 60 requests per hour (default)
- Key endpoints:
  - `/StopMonitoring` - Real-time arrival predictions
  - `/operators` - List of transit agencies
  - `/stops` - Stops for a given operator

## Development Commands

```bash
# Set up development environment
./scripts/setup

# Start Home Assistant for testing
./scripts/develop

# Lint and format code
./scripts/lint

# Manual linting commands
ruff format .
ruff check . --fix
```

## Code Standards

This project uses Ruff for Python linting with strict rules based on Home Assistant core standards:
- Target Python 3.13
- Maximum McCabe complexity of 25
- All Ruff rules enabled except specific formatting conflicts
- Auto-formatting with `ruff format`

## Testing

Run the integration in a local Home Assistant instance using `./scripts/develop`. This creates a config directory and starts Home Assistant with the custom component loaded via PYTHONPATH.

To test the integration:
1. Get a 511.org API key from https://511.org/open-data/token
2. Find transit stop codes from agency websites or physical stop signs
3. Common agency codes: SF (Muni), BA (BART), AC (AC Transit), VT (VTA)

## Common Tasks

### Adding new sensor types
1. Modify `sensor.py` to create additional sensor entities
2. Update the coordinator if new data needs to be fetched
3. Add any new constants to `const.py`

### Modifying API client
1. The API client in `api.py` handles SIRI format responses
2. Response parsing is in `_parse_stop_monitoring` method
3. Add new endpoints as async methods following the existing pattern

### Debugging API issues
1. Enable debug logging for the integration
2. Check coordinator's `_async_update_data` for fetch errors
3. Verify API key and stop codes are correct
4. Monitor rate limit (60 requests/hour default)