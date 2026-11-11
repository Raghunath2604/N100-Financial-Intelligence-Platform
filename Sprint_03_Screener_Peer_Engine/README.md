# N100 Financial Intelligence Platform — Sprint 3

Sprint 3 adds a config-driven financial screener, composite quality scoring, peer percentiles, Excel outputs and radar charts on top of the Sprint 2 SQLite database.

## Run the pipeline
From the project root:
```bash
pip install -r requirements.txt
python src/screener/run_screener.py
```

## Test
```bash
pytest tests/etl tests/kpi tests/screener -q
```

## Outputs
- `output/screener_output.xlsx` — six strategy sheets
- `output/peer_comparison.xlsx` — 11 peer-group sheets, 20 KPI metrics plus percentile columns
- `output/companies_without_peer_group.csv`
- `output/sprint3_data_quality_checks.csv` — 14 DQ checks
- `output/sprint3_manifest.json`
- `reports/radar_charts/` — 92 company radar charts
- SQLite `peer_percentiles` table

Read `docs/SPRINT_3_VALIDATION_REPORT.md` for methodology, actual preset counts and source-data caveats.
