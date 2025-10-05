# src/pipelines/train.py
from __future__ import annotations

import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

import src.config as cfg
from src.utils.io import save_json
from src.utils.metrics import compute_metrics

PROCESSED_DIR = cfg.PROCESSED_DIR
MODELS_DIR = cfg.MODELS_DIR
FEATURES_PATH = getattr(cfg, "FEATURES_PATH", str(PROCESSED_DIR / "features.parquet"))


def train_model():
    # Load features
    df = pd.read_parquet(FEATURES_PATH)

    # Prefer new explicit name 'y_next_24h'; otherwise fallback to 'y_next_h'
    target_col_candidates = ["y_next_24h", "y_next_h"]
    target_col = next((c for c in target_col_candidates if c in df.columns), None)
    if target_col is None:
        raise KeyError(
            f"No target column found. Expected one of: {target_col_candidates}. "
            f"Make sure features were built with horizon 24h or adjust train.py accordingly."
        )

    y = df[target_col]
    # Drop only the target col; keep all numeric features
    X = df.drop(columns=[target_col], errors="ignore")
    X = X.select_dtypes(include=["number"]).copy()

    # Time-aware split (no shuffle)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(n_estimators=200, max_depth=None, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)

    metrics = compute_metrics(y_val.values, y_pred)
    metrics["R2"] = float(r2_score(y_val.values, y_pred))
    metrics["target_col"] = target_col
    metrics["n_train"] = int(X_train.shape[0])
    metrics["n_val"] = int(X_val.shape[0])

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, str(MODELS_DIR / "model.pkl"))
    save_json(metrics, str(MODELS_DIR / "metrics.json"))
    print("Train OK:", metrics)


def main():
    train_model()


if __name__ == "__main__":
    main()
