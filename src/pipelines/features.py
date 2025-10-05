# src/pipelines/features.py
from __future__ import annotations

import glob

import pandas as pd

# Import config safely (works with or without FEATURES_PATH in config)
import src.config as cfg

RAW_DIR = cfg.RAW_DIR
PROCESSED_DIR = cfg.PROCESSED_DIR
# default output path if FEATURES_PATH not present in config
FEATURES_PATH = getattr(cfg, "FEATURES_PATH", str(PROCESSED_DIR / "features.parquet"))


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def latest(path_pattern: str) -> str | None:
    """Return the latest file path matching the pattern (or None)."""
    files = sorted(glob.glob(path_pattern))
    return files[-1] if files else None


def _safe_to_datetime(series, utc: bool = True):
    return pd.to_datetime(series, utc=utc, errors="coerce")


def _resample_hourly_mean(df: pd.DataFrame, ts_col: str, tz_aware: bool = True) -> pd.DataFrame:
    """Set index to ts_col and resample hourly mean."""
    out = df.copy()
    out[ts_col] = _safe_to_datetime(out[ts_col], utc=tz_aware)
    out = out.set_index(ts_col).sort_index()
    # Use "1h" (lowercase) to avoid FutureWarning
    out = out.resample("1h").mean()
    return out


# ---------------------------------------------------------------------
# Features builder
# ---------------------------------------------------------------------
def build_features(
    target_priority: list[str] = ("no2", "pm25"),
    horizon_hours: int = 24,
    impute_limit: int = 3,
) -> str | None:
    """
    Build the features dataset from:
      - Air quality unified: data/raw/air_quality_*.parquet
      - Weather (Open-Meteo): data/raw/openmeteo_*.parquet

    Steps:
      1) load latest raw dumps
      2) align hourly timestamps
      3) join
      4) create lags & rolling stats
      5) create target at t + horizon_hours (column 'y_next_24h')
      6) dropna & save
    """

    # 1) Locate latest files
    aq_path = latest(f"{RAW_DIR}/air_quality_*.parquet")
    meteo_path = latest(f"{RAW_DIR}/openmeteo_*.parquet")

    if not aq_path and not meteo_path:
        print("[WARN] No raw files found in data/raw/. Run: python -m src.pipelines.ingest first.")
        return None

    # 2) Load
    aq = pd.read_parquet(aq_path) if aq_path else pd.DataFrame()
    meteo = pd.read_parquet(meteo_path) if meteo_path else pd.DataFrame()

    # 3) Normalize time columns & resample hourly
    # AQ may come from OpenAQ (col 'datetime') or Open-Meteo Air (col 'time')
    if not aq.empty:
        if "datetime" in aq.columns:
            aq = _resample_hourly_mean(aq.rename(columns={"datetime": "time"}), "time")
        elif "time" in aq.columns:
            aq = _resample_hourly_mean(aq, "time")
        else:
            print("[WARN] AQ missing recognizable time column; skipping AQ.")
            aq = pd.DataFrame()

        # Harmonize names (just in case)
        aq = aq.rename(columns={"pm2.5": "pm25"})
    else:
        print("[INFO] AQ is empty (no file or empty fetch).")

    if not meteo.empty:
        if "time" in meteo.columns:
            meteo = _resample_hourly_mean(meteo, "time")
        else:
            print("[WARN] Weather missing 'time' column; skipping weather.")
            meteo = pd.DataFrame()
    else:
        print("[INFO] Weather is empty (no file or empty fetch).")

    # 4) Join: use weather as temporal spine when available
    if meteo.empty and aq.empty:
        print("[ERROR] Nothing to merge (AQ and weather both empty).")
        return None

    if meteo.empty:
        df = aq.copy()
    elif aq.empty:
        df = meteo.copy()
    else:
        df = meteo.join(aq, how="left")

    # 5) Light imputation for small gaps
    df = df.sort_index()
    df = df.interpolate(limit=impute_limit).ffill().bfill()

    # 6) Create lags/rolling for pollutants if present
    pollutants = [c for c in ["no2", "pm25"] if c in df.columns]
    for col in pollutants:
        for h in (1, 3, 6):
            df[f"{col}_lag{h}"] = df[col].shift(h)
        df[f"{col}_roll6_mean"] = df[col].rolling(6).mean()
        df[f"{col}_roll6_std"] = df[col].rolling(6).std()

    # 7) Target t + horizon_hours; we write explicit name y_next_24h for compatibility
    target: str | None = None
    for cand in target_priority:
        if cand in df.columns:
            target = cand
            break

    if target:
        target_col = f"y_next_{horizon_hours}h"
        df[target_col] = df[target].shift(-horizon_hours)
    else:
        print("[WARN] No target column ('no2' or 'pm25') found. Target stays None.")
        target_col = None

    # 8) Clean and save
    df_out = df.dropna().reset_index().rename(columns={"index": "time"})
    df_out.to_parquet(FEATURES_PATH, index=False)

    print(
        f"Features OK: {df_out.shape}, "
        f"target={target!r}, horizon={horizon_hours}h, "
        f"saved -> {FEATURES_PATH}"
    )
    return target


def main():
    build_features()


if __name__ == "__main__":
    main()
