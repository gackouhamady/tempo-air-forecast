import streamlit as st

def alert_banner(alert_any: bool, threshold: int):
    if alert_any:
        st.error(f"⚠️ Air quality forecast exceeds threshold ({threshold}). Consider limiting outdoor activities.")
    else:
        st.success("✅ Forecast under threshold in the selected horizon.")
