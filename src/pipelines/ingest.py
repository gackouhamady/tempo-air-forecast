# src/pipelines/ingest.py
from __future__ import annotations
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.config import (
    OPENAQ_BASE_URL, OPEN_METEO_BASE_URL, DEFAULT_LAT, DEFAULT_LON,
    RAW_DIR, DATA_WINDOW_DAYS
)
from src.utils.io import save_parquet, today_stamp


# ---------- OpenAQ (fixed: no 'temporal'/'order_by', simple pagination) ----------
def fetch_openaq(lat: float, lon: float, days: int = 7, radius_m: int = 15000) -> pd.DataFrame:
    """
    Fetch NO2/PM2.5 near (lat, lon) over the last `days` from OpenAQ v2.
    Avoid 'temporal'/'order_by' (can trigger 410). We aggregate to hourly locally.
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_m,
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "limit": 10000,
        "parameter": ["pm25", "no2"],
        "page": 1,
    }

    all_rows = []
    try:
        while True:
            r = requests.get(f"{OPENAQ_BASE_URL}/measurements", params=params, timeout=45)
            r.raise_for_status()
            payload = r.json()
            results = payload.get("results", [])
            if not results:
                break
            all_rows.extend(results)

            # naive pagination: if we got a full page, try next page
            if len(results) >= params["limit"]:
                params["page"] += 1
            else:
                break

        if not all_rows:
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)

        # Parse datetime (date may be {"utc": "...", "local": "..."})
        if "date" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["date"].apply(lambda d: d.get("utc") if isinstance(d, dict) else None),
                utc=True,
                errors="coerce",
            )
        elif "date_utc" in df.columns:
            df["datetime"] = pd.to_datetime(df["date_utc"], utc=True, errors="coerce")
        else:
            df["datetime"] = pd.to_datetime(df.get("datetime"), utc=True, errors="coerce")

        keep = [c for c in ["datetime", "parameter", "value", "unit"] if c in df.columns]
        df = df[keep].dropna(subset=["datetime", "parameter", "value"])
        if df.empty:
            return pd.DataFrame()

        # pivot to wide, then resample hourly
        pivot = (
            df.pivot_table(index="datetime", columns="parameter", values="value", aggfunc="mean")
              .rename(columns={"pm2.5": "pm25"})
              .sort_index()
              .resample("1H")
              .mean()
        )
        return pivot
    except Exception as e:
        print(f"[WARN] OpenAQ fetch failed: {e}")
        return pd.DataFrame()


# ---------- Open-Meteo Weather (unchanged) ----------
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


# ---------- Open-Meteo Air Quality (fallback if OpenAQ empty) ----------
def fetch_openmeteo_air(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone,carbon_monoxide,sulphur_dioxide",
        "past_days": days,
        "forecast_days": 2,
        "timezone": "UTC",
    }
    try:
        r = requests.get(url, params=params, timeout=45)
        r.raise_for_status()
        j = r.json()
        hourly = j.get("hourly", {})
        if not hourly:
            return pd.DataFrame()
        df = pd.DataFrame(hourly)
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df = df.set_index("time").sort_index()
        # align names with the rest of the pipeline
        df = df.rename(columns={"pm2_5": "pm25", "nitrogen_dioxide": "no2"})
        return df
    except Exception as e:
        print(f"[WARN] Open-Meteo Air Quality fetch failed: {e}")
        return pd.DataFrame()


def main():
    stamp = today_stamp()

    # weather
    meteo = fetch_openmeteo(DEFAULT_LAT, DEFAULT_LON, DATA_WINDOW_DAYS)
    if not meteo.empty:
        save_parquet(meteo.reset_index(), f"{RAW_DIR}/openmeteo_{stamp}.parquet")
    else:
        print("[WARN] Weather fetch returned empty.")

    # air quality: try OpenAQ first, then fallback to Open-Meteo Air
    aq = fetch_openaq(DEFAULT_LAT, DEFAULT_LON, DATA_WINDOW_DAYS)
    if aq.empty:
        print("[INFO] Falling back to Open-Meteo Air Quality…")
        aq = fetch_openmeteo_air(DEFAULT_LAT, DEFAULT_LON, DATA_WINDOW_DAYS)

    if not aq.empty:
        # unified filename for AQ irrespective of the source
        save_parquet(aq.reset_index(), f"{RAW_DIR}/air_quality_{stamp}.parquet")
    else:
        print("[WARN] Air quality fetch returned empty.")

    print(
        "Ingest OK:",
        aq.shape if isinstance(aq, pd.DataFrame) else None,
        meteo.shape if isinstance(meteo, pd.DataFrame) else None,
    )


if __name__ == "__main__":
    main()
