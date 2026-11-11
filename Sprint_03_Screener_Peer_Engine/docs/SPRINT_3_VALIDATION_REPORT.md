# Sprint 3 — Final Implementation & Validation Report

## Completion summary
Sprint 3 engineering deliverables are implemented. The pipeline now selects annual March financial statements rather than accidentally preferring later interim September observations. A source company with no March record (SIEMENS) is retained using its latest available period and explicitly flagged as an interim-period fallback. Missing component inputs receive a neutral 50 component score, so the composite score is available for the full universe without pretending missing source metrics are measured values.

## Delivered
- 15 standard screening filters and six config-driven presets.
- Financial-sector exemption from the D/E threshold.
- Debt-free companies pass ICR thresholds by virtue of the ICR field convention from Sprint 2.
- Composite score 0–100, weighted 35% profitability, 30% cash quality, 20% growth, 15% leverage; P10/P90 winsorisation and 0–100 scaling.
- Sector-relative score.
- 11 peer groups and 10 peer metrics; D/E percentile is inverse-ranked.
- `peer_percentiles` persisted in SQLite.
- Six-sheet `screener_output.xlsx`, sorted by composite score.
- Eleven-sheet `peer_comparison.xlsx` with 20 KPI metrics and percentile columns; percentile cell fills green >=75, yellow 25–75, red <=25; benchmark rows amber.
- 92 radar charts with eight higher-is-better axes; peer average is dashed, and companies without a peer group are compared with the Nifty 100 average.
- Companies with no peer group are explicitly listed.
- 14 Sprint 3 DQ checks.
- Reproducible CLI pipeline: `python src/screener/run_screener.py`.
- Cumulative automated test suite: 136 passed, 0 failed.

## Actual strategy results on supplied source data
- **Quality Compounder:** 22 companies
- **Value Pick:** 2 companies
- **Growth Accelerator:** 19 companies
- **Dividend Champion:** 29 companies
- **Debt-Free Blue Chip:** 18 companies
- **Turnaround Watch:** 31 companies

The requested threshold definitions were applied without weakening them or adding synthetic companies. Value Pick returns only two companies in the supplied data; that is a genuine result, not an implementation failure. Preset result-size guidance (5–50) is therefore not met by every preset. The output workbook preserves the true result rather than filling it with non-qualifying names.

## Data handling notes
- 91 companies have annual March 2024 observations.
- SIEMENS has no March record in the supplied ratio extract; its latest available 2024-09 record is retained and flagged `annual_period_fallback=True`.
- Companies with no peer group are marked `No peer group assigned`; they are not assigned invented peer labels.
- Missing metric inputs remain missing for filters and peer percentiles. The composite score uses neutral component values only for unavailable score components and keeps source metrics untouched.

## Test evidence
Command: `pytest tests/etl tests/kpi tests/screener -q`

Result: **136 passed, 0 failed**.

Fourteen DQ rules are recorded in `output/sprint3_data_quality_checks.csv`.
