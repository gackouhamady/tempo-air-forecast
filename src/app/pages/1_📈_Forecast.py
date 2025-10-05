import pandas as pd
import streamlit as st

from src.config import PROCESSED_DIR
from src.utils.viz import line_chart

st.title("📈 Forecast details")
try:
    feats = pd.read_parquet(f"{PROCESSED_DIR}/features.parquet").set_index("time")
    feats.index = pd.to_datetime(feats.index)
    cols = [c for c in ["no2", "pm25"] if c in feats.columns]
    if cols:
        st.plotly_chart(
            line_chart(feats.tail(168), cols, title="Last 7 days"), use_container_width=True
        )
    else:
        st.info("No pollutant columns available yet.")
except Exception as e:
    st.warning(f"Data not ready: {e}")
