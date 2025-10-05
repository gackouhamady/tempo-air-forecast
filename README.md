# 🌍 TEMPO Air Forecast — NASA Space Apps 2025  

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img alt="CI/CD" src="https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">
  <img alt="Cloud" src="https://img.shields.io/badge/Deploy-Cloud%20Run%20%7C%20Firebase-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white">
</p>

---

## 🛰️ Overview  
**TEMPO Air Forecast** is a web application for **local air quality (AQI/NO₂) forecasting**, combining **ground-based measurements (OpenAQ)**, **weather data (Open-Meteo/Meteomatics)**, and optionally **NASA TEMPO satellite observations**.  

**MVP goal:**  
- Interactive **map**  
- **Time series visualization**  
- **24-hour air quality forecast**  
- **Personalized alerts** (email/notification)  

---

## ⚙️ Tech Stack  
- **Backend:** Python 3.11, FastAPI, scikit-learn (RandomForest)  
- **Frontend:** Streamlit (UI)  
- **Data:** Pandas, OpenAQ, Open-Meteo  
- **DevOps:** Docker, Makefile, GitHub Actions (CI/CD)  
- **Deployment:** Google Cloud Run or Firebase Hosting  

---

## 🚀 Run Locally  

```bash
# Create a virtual environment
python -m venv .venv && source .venv/bin/activate   # (Windows: .\.venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the full pipeline (data → features → model)
make ingest features train

# Start FastAPI backend
make run-api       # http://127.0.0.1:8000/health

# Launch Streamlit frontend
make run-app       # http://localhost:8501

```
## 🧩 Project Structure
``` bash
src/
 ├── pipelines/       # Dataflow: ingest → features → train → predict
 ├── api/             # FastAPI endpoints: /health, /forecast
 └── app/             # Streamlit UI: map, graphs, alerts
```
## 🌤️ Data Sources (MVP)

- OpenAQ → Ground measurements (PM2.5, NO₂)

- Open-Meteo → Weather data (free API)

- (Optional) NASA TEMPO → Tropospheric NO₂ products
  
## 🧭 Roadmap

- 🔗 Integrate NASA TEMPO satellite data (tropospheric NO₂)

- ⚠️ Add personalized alerts for schools, athletes, and vulnerable groups

- 📱 Progressive Web App (PWA) with offline cache and mobile support