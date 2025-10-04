from __future__ import annotations
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.config import (
    OPENAQ_BASE_URL, OPEN_METEO_BASE_URL, DEFAULT_LAT, DEFAULT_LON,
    RAW_DIR, DATA_WINDOW_DAYS
)
from src.utils.io import save_parquet, today_stamp

def fetch_openaq(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": 15000,
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "limit": 10000,
        "parameter": ["pm25","no2"],
        "temporal": "hour",
        "order_by": "datetime"
    }
    r = requests.get(f"{OPENAQ_BASE_URL}/measurements", params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get("results", [])
    if not data:
        return pd.DataFrame(columns=["datetime","parameter","value","unit"])
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["date"].apply(lambda d: d.get("utc")))
    df = df[["datetime","parameter","value","unit"]]
    pivot = df.pivot_table(index="datetime", columns="parameter", values="value", aggfunc="mean").sort_index()
    pivot.index = pivot.index.tz_convert("UTC")
    return pivot

def fetch_openmeteo(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m",
        "past_days": days,
        "forecast_days": 2,
        "timezone": "UTC",
    }
    r = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    hourly = j.get("hourly", {})
    if not hourly:
        return pd.DataFrame()
    df = pd.DataFrame(hourly)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.set_index("time").sort_index()
    return df

def main():
    aq = fetch_openaq(DEFAULT_LAT, DEFAULT_LON, DATA_WINDOW_DAYS)
    meteo = fetch_openmeteo(DEFAULT_LAT, DEFAULT_LON, DATA_WINDOW_DAYS)
    stamp = today_stamp()
    if not aq.empty:
        save_parquet(aq.reset_index(), f"{RAW_DIR}/openaq_{stamp}.parquet")
    if not meteo.empty:
        save_parquet(meteo.reset_index(), f"{RAW_DIR}/openmeteo_{stamp}.parquet")
    print("Ingest OK:", aq.shape, meteo.shape)

if __name__ == "__main__":
    main()
