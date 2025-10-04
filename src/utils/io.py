from __future__ import annotations
import json
import os
from datetime import datetime
import pandas as pd

def save_parquet(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)

def load_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)

def save_json(obj: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def today_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d")

def exists(path: str) -> bool:
    return os.path.exists(path)
