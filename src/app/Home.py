import pandas as pd
import requests
import streamlit as st

from src.config import ALERT_AQI_THRESHOLD, DEFAULT_LAT, DEFAULT_LON, PROCESSED_DIR
from src.utils.viz import line_chart

st.set_page_config(page_title="TEMPO Air Forecast", layout="wide")
st.title("🌍 TEMPO Air Forecast — MVP")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    lat = st.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
with col2:
    lon = st.number_input("Longitude", value=DEFAULT_LON, format="%.4f")
with col3:
    horizon = st.slider("Horizon (hours)", 6, 48, 24)

st.caption("Data shown is based on most recent ingestion window around default location (MVP).")

try:
    feats = pd.read_parquet(f"{PROCESSED_DIR}/features.parquet").set_index("time")
    feats.index = pd.to_datetime(feats.index)
except Exception:
    feats = pd.DataFrame()

if not feats.empty:
    cols = [c for c in ["no2", "pm25"] if c in feats.columns]
    if cols:
        st.plotly_chart(
            line_chart(feats.tail(72), cols, title="Recent Air Quality & Features"),
            use_container_width=True,
        )

if st.button("Generate Forecast"):
    resp = requests.post(
        "http://localhost:8000/forecast",
        json={"lat": lat, "lon": lon, "horizon_hours": horizon},
        timeout=15,
    )
    if resp.ok:
        data = resp.json().get("items", [])
        if data:
            dfp = pd.DataFrame(data)
            dfp["time"] = pd.to_datetime(dfp["time"])
            dfp = dfp.set_index("time").sort_index()
            st.plotly_chart(
                line_chart(dfp, ["forecast"], title="Forecast"), use_container_width=True
            )
            if dfp["alert"].any():
                st.error(
                    f"⚠️ Air quality forecast exceeds threshold ({ALERT_AQI_THRESHOLD}). Consider limiting outdoor activities."
                )
            else:
                st.success("✅ Forecast under threshold in the selected horizon.")
        else:
            st.warning("No forecast returned.")
    else:
        st.error(f"API error: {resp.status_code}")
