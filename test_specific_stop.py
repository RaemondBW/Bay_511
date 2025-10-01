#!/usr/bin/env python3
"""Test a specific stop with your API key."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import aiohttp

from custom_components.bay_511.api import Bay511ApiClient


async def main():
    api_key = "774056c2-3a11-40e3-9b64-b3c8bb39b0c8"

    async with aiohttp.ClientSession() as session:
        client = Bay511ApiClient(api_key=api_key, session=session)

        try:
            # Test with a known BART station (Embarcadero)
            print("Testing BART Embarcadero station (BA, EMBR)...")
            data = await client.async_get_stop_monitoring("BA", "EMBR")
            print(f"Stop: {data.get('stop_name', 'Unknown')}")
            arrivals = data.get("arrivals", [])

            if arrivals:
                print(f"Found {len(arrivals)} arrivals:")
                for i, arrival in enumerate(arrivals[:3], 1):
                    mins = arrival.get("minutes_away", "Unknown")
                    line = arrival.get("line_ref", "Unknown")
                    dest = arrival.get("destination", "Unknown")
                    print(f"  {i}. Line {line} to {dest}: {mins} minutes")
            else:
                print("No arrivals found")
                print("Raw data structure:")
                print(data)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
