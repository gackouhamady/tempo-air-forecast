from __future__ import annotations

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import ForecastRequest
from src.config import ALERT_AQI_THRESHOLD, MODELS_DIR, PROCESSED_DIR

app = FastAPI(title="TEMPO Air Forecast API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/forecast")
def forecast(req: ForecastRequest):
    df = pd.read_parquet(f"{PROCESSED_DIR}/features.parquet").set_index("time")
    X = df.select_dtypes(include=["number"]).drop(
        columns=[c for c in df.columns if c == "y_next_24h"], errors="ignore"
    )
    model = joblib.load(f"{MODELS_DIR}/model.pkl")
    preds = model.predict(X)
    horizon = min(req.horizon_hours, 48)
    out = pd.DataFrame({"time": X.index, "y_pred": preds}).tail(horizon)
    out["alert"] = (out["y_pred"] >= ALERT_AQI_THRESHOLD).astype(int)
    return {
        "horizon": horizon,
        "items": [
            {"time": pd.to_datetime(t).isoformat(), "forecast": float(v), "alert": int(a)}
            for t, v, a in zip(out["time"], out["y_pred"], out["alert"])
        ],
    }
