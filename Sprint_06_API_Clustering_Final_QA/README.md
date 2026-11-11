# N100 Financial Intelligence Platform — Sprint 6

Final sprint: FastAPI read-only service, five-cluster company archetypes, API exports, analyst guide, and acceptance QA.

## Run API
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```
Swagger: `http://127.0.0.1:8000/docs`.

## Run clustering
```bash
python -m src.analytics.run_clustering
```

## Key deliverables
- 16+ live API routes across health, companies, screener, sectors, peers, valuation, portfolio, and documents
- `output/cluster_labels.csv` for all 92 companies
- Elbow plot, correlation heatmap, outlier report, portfolio stats
- OpenAPI and Postman exports; analyst guide PDF; acceptance checklist

## Data note
This is a historical supplied dataset, not a live market-data connection. Missing features are not fabricated; sector-median imputation is applied only for clustering and documented in the output methodology.
