import pandas as pd
import streamlit as st
from glob import glob

st.title("🧪 Compare Sources (Raw)")

def latest(pattern):
    files = sorted(glob(pattern))
    return files[-1] if files else None

aq = latest("data/raw/openaq_*.parquet")
meteo = latest("data/raw/openmeteo_*.parquet")

col1, col2 = st.columns(2)
with col1:
    st.subheader("OpenAQ (raw)")
    if aq:
        st.dataframe(pd.read_parquet(aq).head(30))
    else:
        st.info("No OpenAQ file yet.")

with col2:
    st.subheader("Open-Meteo (raw)")
    if meteo:
        st.dataframe(pd.read_parquet(meteo).head(30))
    else:
        st.info("No Open-Meteo file yet.")
