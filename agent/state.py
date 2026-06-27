from langgraph.graph import MessagesState
from pydantic import BaseModel


class WeatherResponse(BaseModel):
    location: str
    condition: str
    temperature_c: float
    humidity_pct: int
    wind_kmh: float
    summary: str


class AgentState(MessagesState):
    weather_response: WeatherResponse | None = None
