from __future__ import annotations

import joblib
import pandas as pd

from src.config import MODELS_DIR, PROCESSED_DIR


def batch_predict():
    df = pd.read_parquet(f"{PROCESSED_DIR}/features.parquet").select_dtypes(include=["number"])
    X = df.drop(columns=[c for c in df.columns if c == "y_next_24h"], errors="ignore")
    model = joblib.load(f"{MODELS_DIR}/model.pkl")
    preds = model.predict(X)
    out = df.copy()
    out["y_pred"] = preds
    print("Predict OK:", out.tail(5)[["y_pred"]])


def main():
    batch_predict()


if __name__ == "__main__":
    main()
