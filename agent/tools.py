import httpx
from langchain_core.tools import tool

WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "icy fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight showers", 81: "moderate showers", 82: "violent showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with heavy hail",
}

MOCK_DATA = (
    "Weather data unavailable — showing mock data: "
    "Clear sky, 22°C, humidity 55%, wind 10 km/h."
)


@tool
def get_weather(location: str) -> str:
    """Get current weather conditions for a given location."""
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1},
            timeout=5,
        ).json()

        if not geo.get("results"):
            return f"Could not find location '{location}'. {MOCK_DATA}"

        result = geo["results"][0]
        lat, lon = result["latitude"], result["longitude"]
        place = result.get("name", location)
        country = result.get("country", "")

        weather = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m,weathercode,relative_humidity_2m",
            },
            timeout=5,
        ).json()

        c = weather["current"]
        condition = WEATHER_CODES.get(c["weathercode"], "unknown conditions")
        return (
            f"Weather in {place}, {country}: {condition}, "
            f"{c['temperature_2m']}°C, "
            f"humidity {c['relative_humidity_2m']}%, "
            f"wind {c['wind_speed_10m']} km/h."
        )
    except Exception:
        return MOCK_DATA
