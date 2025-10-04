from pydantic import BaseModel

class ForecastRequest(BaseModel):
    lat: float
    lon: float
    horizon_hours: int = 24
