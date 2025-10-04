# src/config.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Charge .env si présent
load_dotenv()

# ---------- Helpers ----------
def _get_env_str(name: str, default: str) -> str:
    val = os.getenv(name, "").strip()
    return val if val else default

def _get_env_int(name: str, default: int) -> int:
    try:
        return int(_get_env_str(name, str(default)))
    except ValueError:
        return default

def _get_env_float(name: str, default: float) -> float:
    try:
        return float(_get_env_str(name, str(default)))
    except ValueError:
        return default

def _get_env_bool(name: str, default: bool) -> bool:
    raw = _get_env_str(name, "true" if default else "false").lower()
    return raw in {"1", "true", "yes", "y", "on"}

# ---------- API endpoints ----------
OPENAQ_BASE_URL = _get_env_str("OPENAQ_BASE_URL", "https://api.openaq.org/v2")
# Météo (température, vent, humidité, etc.)
OPEN_METEO_BASE_URL = _get_env_str("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
# Qualité de l'air (fallback : pm2_5, no2, etc.)
OPEN_METEO_AIR_BASE_URL = _get_env_str(
    "OPEN_METEO_AIR_BASE_URL", "https://air-quality-api.open-meteo.com/v1/air-quality"
)

# ---------- App defaults ----------
DEFAULT_LAT = _get_env_float("DEFAULT_LAT", 48.8566)
DEFAULT_LON = _get_env_float("DEFAULT_LON", 2.3522)
ALERT_AQI_THRESHOLD = _get_env_int("ALERT_AQI_THRESHOLD", 100)
DATA_WINDOW_DAYS = _get_env_int("DATA_WINDOW_DAYS", 7)

# L’URL de l’API à laquelle la webapp (Streamlit) parle ; local par défaut
API_BASE_URL = _get_env_str("API_BASE_URL", "http://localhost:8000")

# (Optionnel) Clé Google Maps si tu l’utilises côté front
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()

# Timeouts réseau (en secondes) pour requests
HTTP_TIMEOUT_SEC = _get_env_int("HTTP_TIMEOUT_SEC", 45)

# ---------- Dossiers projet ----------
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = Path("models")
NOTEBOOKS_DIR = Path("notebooks")

# Création des dossiers si non existants
for d in (DATA_DIR, RAW_DIR, INTERIM_DIR, PROCESSED_DIR, MODELS_DIR, NOTEBOOKS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------- Patterns utiles ----------
AIR_QUALITY_RAW_PATTERN = str(RAW_DIR / "air_quality_*.parquet")
OPENMETEO_RAW_PATTERN = str(RAW_DIR / "openmeteo_*.parquet")
FEATURES_PATH = str(PROCESSED_DIR / "features.parquet")
MODEL_PATH = str(MODELS_DIR / "model.pkl")
METRICS_PATH = str(MODELS_DIR / "metrics.json")
