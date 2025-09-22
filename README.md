# Bay Area 511 Transit Integration for Home Assistant

This Home Assistant integration provides real-time transit arrival predictions for Bay Area public transportation stops using the 511.org API.

## Features

- Real-time arrival predictions for bus, train, and light rail stops
- Support for multiple transit agencies (Muni, BART, AC Transit, VTA, etc.)
- Monitor multiple stops simultaneously
- Shows next and subsequent arrival times
- Displays additional information like route, destination, and vehicle status

## Prerequisites

You'll need a free API key from 511.org:
1. Visit https://511.org/open-data/token
2. Register for an account
3. Request an API token

## Installation

### Manual Installation

1. Copy the `custom_components/bay_511` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI (Settings → Devices & Services → Add Integration → Bay Area 511 Transit)

### HACS Installation (Coming Soon)

This integration will be submitted to HACS for easier installation.

## Configuration

1. When adding the integration, enter your 511.org API key
2. Add transit stops by providing:
   - **Agency Code**: The transit agency identifier (e.g., "SF" for Muni, "BA" for BART)
   - **Stop Code**: The specific stop code for your transit stop

### Finding Stop Codes

Stop codes can be found:
- On physical signs at transit stops
- Through the 511.org website
- In transit agency mobile apps
- Via the 511 API operators and stops endpoints

Common agency codes:
- `SF` - San Francisco Muni
- `BA` - BART
- `AC` - AC Transit
- `VT` - VTA (Valley Transportation Authority)
- `GG` - Golden Gate Transit
- `CT` - Caltrain

## Sensors

For each configured stop, the integration creates two sensors:
- **Next Arrival**: Minutes until the next vehicle arrives
- **Subsequent Arrival**: Minutes until the following vehicle

Each sensor includes attributes:
- Line/Route number
- Destination
- Direction
- Expected arrival time
- Aimed (scheduled) arrival time
- Vehicle at stop status
- Stop name and code

## Example Automations

### Notify when bus is approaching
```yaml
automation:
  - alias: "Bus Approaching Notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bay_511_sf_12345_next
        below: 5
    action:
      - service: notify.mobile_app
        data:
          message: "Bus arriving in {{ states('sensor.bay_511_sf_12345_next') }} minutes!"
```

## API Limits

The 511.org API has a default rate limit of 60 requests per hour. The integration updates every 60 seconds by default to stay within these limits.

## Troubleshooting

- **Invalid API Key**: Ensure your API key is correct and active
- **No Data**: Verify the agency code and stop code are correct
- **Rate Limiting**: If you see rate limit errors, consider increasing the update interval

## Development

This integration is based on the Home Assistant integration blueprint and uses the 511.org Transit API.

### Testing

1. Set up the development environment using the provided devcontainer
2. Run Home Assistant with `./scripts/develop`
3. The integration will be available for testing

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/raemond/bay_511/issues)
- Check the [511.org API documentation](https://511.org/open-data/transit)

## Credits

- 511.org for providing the transit data API
- Home Assistant community for the integration blueprint