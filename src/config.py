import os
from dotenv import load_dotenv

load_dotenv()

OPENAQ_BASE_URL = os.getenv("OPENAQ_BASE_URL", "https://api.openaq.org/v2")
OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "48.8566"))
DEFAULT_LON = float(os.getenv("DEFAULT_LON", "2.3522"))
ALERT_AQI_THRESHOLD = int(os.getenv("ALERT_AQI_THRESHOLD", "100"))
DATA_WINDOW_DAYS = int(os.getenv("DATA_WINDOW_DAYS", "7"))

DATA_DIR = "data"
RAW_DIR = f"{DATA_DIR}/raw"
INTERIM_DIR = f"{DATA_DIR}/interim"
PROCESSED_DIR = f"{DATA_DIR}/processed"
MODELS_DIR = "models"

for d in (DATA_DIR, RAW_DIR, INTERIM_DIR, PROCESSED_DIR, MODELS_DIR):
    os.makedirs(d, exist_ok=True)
