from __future__ import annotations
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from src.config import PROCESSED_DIR, MODELS_DIR
from src.utils.io import save_json
from src.utils.metrics import compute_metrics
import joblib

def train_model():
    df = pd.read_parquet(f"{PROCESSED_DIR}/features.parquet")
    y = df["y_next_24h"]
    X = df.drop(columns=[c for c in df.columns if c in ("y_next_24h")])
    X = X.select_dtypes(include=["number"]).copy()

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(
        n_estimators=200, max_depth=None, n_jobs=-1, random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)

    metrics = compute_metrics(y_val.values, y_pred)
    metrics["R2"] = float(r2_score(y_val.values, y_pred))

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, f"{MODELS_DIR}/model.pkl")
    save_json(metrics, f"{MODELS_DIR}/metrics.json")
    print("Train OK:", metrics)

def main():
    train_model()

if __name__ == "__main__":
    main()
