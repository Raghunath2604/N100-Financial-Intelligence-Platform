# N100 Financial Intelligence Platform — Sprint 1: Data Foundation

## Included
- All 12 supplied Excel datasets in `data/raw/`
- Excel loader with core (`header=1`) and supplementary (`header=0`) conventions
- Ticker and year normalisers
- DQ-01 to DQ-16 validator
- SQLite database build, load audit, validation failures and FK check
- 35+ ETL normalisation unit tests
- 10 exploratory SQL queries

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python -m src.etl.run
pytest tests/etl -v
```
Or use `make load` and `make test` where Make is available.

## Outputs
- `database/nifty100.db`
- `output/load_audit.csv`
- `output/validation_failures.csv`
- `output/foreign_key_check.csv`
- `data/processed/*.csv`

## Data integrity behaviour\nRows referencing tickers absent from the 92-company master are preserved in `<table>_quarantine` SQLite tables and listed in `output/quarantine_manifest.csv`. Curated tables enforce `FOREIGN KEY(company_id) REFERENCES companies(id)`. Duplicate source IDs stop the load; repeated company/year observations are retained because the source primary key is the row identity.\n\n## Important specification note
The PDF says “10 tables” but lists 12 source tables in its module inventory. The Sprint 1 task pasted into the workspace says 10 tables but lists 11. This sprint imports all 12 supplied datasets into 12 SQLite tables to retain all provided data; see `docs/DATA_MODEL.md`.

DQ-13 checks missing URLs offline; live HTTP URL status validation is not run by default. DQ-15 is informational and is not a rejection criterion.
