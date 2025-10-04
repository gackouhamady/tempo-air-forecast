from __future__ import annotations
import glob
import pandas as pd
from src.config import RAW_DIR, PROCESSED_DIR
from src.utils.io import save_parquet

def latest(path_pattern: str) -> str | None:
    files = sorted(glob.glob(path_pattern))
    return files[-1] if files else None

def build_features():
    aq_path = latest(f"{RAW_DIR}/openaq_*.parquet")
    meteo_path = latest(f"{RAW_DIR}/openmeteo_*.parquet")

    aq = pd.read_parquet(aq_path) if aq_path else pd.DataFrame()
    meteo = pd.read_parquet(meteo_path) if meteo_path else pd.DataFrame()

    if not aq.empty:
        aq["datetime"] = pd.to_datetime(aq["datetime"], utc=True)
        aq = aq.set_index("datetime").sort_index()
    if not meteo.empty:
        meteo["time"] = pd.to_datetime(meteo["time"], utc=True)
        meteo = meteo.set_index("time").sort_index()

    df = meteo.copy()
    if not aq.empty:
        df = df.join(aq[[c for c in ["no2","pm25"] if c in aq.columns]], how="left")
    df = df.resample("1H").mean().interpolate(limit=3)

    for col in [c for c in ["no2","pm25"] if c in df.columns]:
        for h in (1,3,6):
            df[f"{col}_lag{h}"] = df[col].shift(h)
        df[f"{col}_roll6_mean"] = df[col].rolling(6).mean()
        df[f"{col}_roll6_std"] = df[col].rolling(6).std()

    target = "no2" if "no2" in df.columns else ("pm25" if "pm25" in df.columns else None)
    if target:
        df["y_next_24h"] = df[target].shift(-24)

    df = df.dropna().copy()
    save_parquet(df.reset_index().rename(columns={"index":"time"}), f"{PROCESSED_DIR}/features.parquet")
    print("Features OK:", df.shape, "target:", target)
    return target

def main():
    build_features()

if __name__ == "__main__":
    main()
