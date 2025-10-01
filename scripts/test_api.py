#!/usr/bin/env python3
"""
Test script for the Bay Area 511 API client.
This can be used to verify your API key and test stop predictions.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiohttp

from custom_components.bay_511.api import Bay511ApiClient


async def main():
    print("Bay Area 511 API Test Script")
    print("=" * 40)

    # Get API key from user
    api_key = input("Enter your 511 API key: ").strip()

    if not api_key:
        print("Error: API key is required")
        return

    async with aiohttp.ClientSession() as session:
        client = Bay511ApiClient(api_key=api_key, session=session)

        try:
            # Test 1: Get operators list
            print("\n1. Testing API key by fetching operators...")
            operators = await client.async_get_operators()
            print(f"   ✓ Found {len(operators)} operators")

            # Show first few operators
            print("\n   Sample operators:")
            for op in operators[:5]:
                if isinstance(op, dict):
                    print(f"   - {op.get('Id', 'Unknown')}: {op.get('Name', 'Unknown')}")

            # Test 2: Get stop predictions
            print("\n2. Testing stop predictions (optional)")
            print("   Common agency codes: SF (Muni), BA (BART), AC (AC Transit)")

            test_stop = input("\n   Enter agency code (or press Enter to skip): ").strip()
            if test_stop:
                stop_code = input("   Enter stop code: ").strip()

                if stop_code:
                    print(f"\n   Fetching predictions for {test_stop} stop {stop_code}...")
                    data = await client.async_get_stop_monitoring(test_stop, stop_code)

                    print(f"   Stop: {data.get('stop_name', 'Unknown')}")
                    arrivals = data.get("arrivals", [])

                    if arrivals:
                        print(f"   Found {len(arrivals)} arrivals:")
                        for i, arrival in enumerate(arrivals[:3], 1):
                            mins = arrival.get("minutes_away", "Unknown")
                            line = arrival.get("line_ref", "Unknown")
                            dest = arrival.get("destination", "Unknown")
                            print(f"   {i}. Line {line} to {dest}: {mins} minutes")
                    else:
                        print("   No arrivals found")

            print("\n✓ API key is valid and working!")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\nPlease check:")
            print("1. Your API key is correct")
            print("2. The agency and stop codes are valid")

if __name__ == "__main__":
    asyncio.run(main())
