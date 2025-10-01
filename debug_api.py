#!/usr/bin/env python3
"""Debug the 511 API response format."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json

import aiohttp


async def main():
    api_key = "774056c2-3a11-40e3-9b64-b3c8bb39b0c8"

    async with aiohttp.ClientSession() as session:
        try:
            # Let's check what the raw API response looks like
            url = "https://api.511.org/transit/StopMonitoring"
            params = {
                "api_key": api_key,
                "agency": "BA",  # BART
                "stopcode": "EMBR",  # Embarcadero
                "format": "json",
            }

            print(f"Making request to: {url}")
            print(f"Parameters: {params}")

            async with aiohttp.ClientSession() as session:
                response = await session.get(url, params=params)
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")

                text = await response.text()

                # Remove BOM if present
                if text.startswith("\ufeff"):
                    text = text[1:]
                    print("Removed BOM from response")

                print(f"Raw response length: {len(text)}")
                print("First 500 characters of response:")
                print(text[:500])

                try:
                    data = json.loads(text)
                    print("\nParsed JSON structure:")
                    print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
