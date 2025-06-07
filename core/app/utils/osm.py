import aiohttp


async def reverse_geocoding_by_coords(lat: float, lon: float) -> dict:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "accept-language": "ru"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
