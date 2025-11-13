import requests, json, os
import openmeteo_requests
import requests_cache
from retry_requests import retry

CACHE_FILE = "weather_cache.json"

def get_weather(city: str) -> float | None:
    try:
        return get_temperature(get_coords_nominatim(city))
    except Exception:
        # If offline, load cached weather
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return cached.get(city, None)
        return None

def get_temperature(location: dict | None) -> float | None:
    if location is None:
        return None

    latitude = location["latitude"]
    longitude = location["longitude"]
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session) # pyright: ignore[reportArgumentType]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "forecast_days": 1,
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    temperature = round(response.Current().Variables(0).Value(), 2) # pyright: ignore[reportOptionalMemberAccess]

    # Cache city weather
    city_weather = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            city_weather = json.load(f)
    city_weather[location.get("city", "unknown")] = temperature
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(city_weather, f)

    return temperature

def get_coords_nominatim(city: str) -> dict[str, float] | None:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1, "addressdetails": 0}
    headers = {"User-Agent": "desktop_assistant/1.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    first = data[0]
    coords = {"latitude": float(first["lat"]), "longitude": float(first["lon"]), "city": city}
    return coords
