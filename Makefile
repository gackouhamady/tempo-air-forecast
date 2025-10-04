.PHONY: setup lint test run-api run-app ingest features train predict clean

setup:
	pip install -r requirements.txt

lint:
	ruff src
	black --check src

test:
	pytest -q

run-api:
	uvicorn src.api.main:app --reload --port 8000

run-app:
	streamlit run src/app/Home.py --server.port 8501

ingest:
	python -m src.pipelines.ingest

features:
	python -m src.pipelines.features

train:
	python -m src.pipelines.train

predict:
	python -m src.pipelines.predict

clean:
	rm -rf data/interim/* data/processed/* models/model.pkl models/metrics.json
