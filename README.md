# TEMPO Air Forecast — NASA Space Apps 2025

Web app de **prévision locale de qualité de l’air (AQI/NO₂)** en fusionnant mesures au sol (OpenAQ), météo (Open-Meteo/Meteomatics) et (option) **TEMPO**.
MVP : **carte + série temporelle + prévision 24h + alerte**.

## Stack
- Python 3.11, FastAPI (API), Streamlit (UI), Pandas, scikit-learn/RandomForest
- Docker, Makefile, GitHub Actions (CI), déploiement Cloud Run / Firebase (au choix)

## Lancer localement
```bash
python -m venv .venv && source .venv/bin/activate   # (Win: .\.venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env
make ingest features train
make run-api       # http://127.0.0.1:8000/health
make run-app       # http://localhost:8501
```

## Structure
- `src/pipelines`: ingest → features → train → predict
- `src/api`: endpoints `/health`, `/forecast`
- `src/app`: UI Streamlit (carte, graphes, alertes)

## Données (MVP)
- OpenAQ (PM2.5/NO2) — mesures au sol
- Open-Meteo (météo) — gratuit pour MVP
- (Option) TEMPO NASA — à brancher

## Roadmap
- Intégrer TEMPO (produits NO₂ troposphérique)
- Alertes personnalisées (écoles/sportifs)
- PWA + cache offline
