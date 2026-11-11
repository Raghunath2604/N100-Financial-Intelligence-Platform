# Sprint 4 — Dashboard & Valuation Validation Report

## Scope delivered
Sprint 4 adds the eight-screen Streamlit dashboard and a relative-valuation module on top of the Sprint 3 database.

### Dashboard screens
1. **Home** — six KPI tiles, sector market-cap donut, top-five quality table, year selector and quality-score distribution.
2. **Company Profile** — searchable company selector, six financial/market KPIs, up-to-10-year revenue and net-profit chart, dual-axis ROE/ROCE trend, pros and cons.
3. **Screener** — six Sprint 3 presets, ten custom financial sliders, live result table and CSV export.
4. **Peer Comparison** — peer-group selector, percentile table and metric percentile chart.
5. **Financial Trends** — company selector, up to three chosen metrics, trend lines and revenue YoY table.
6. **Sector Intelligence** — market-cap/ROE bubble chart, sector median P/E chart and sector table.
7. **Capital Allocation** — allocation-pattern treemap and pattern-filtered company table.
8. **Annual Reports** — company report links with explicit unavailable/invalid-link handling.

### Valuation engine
- Market capitalisation and enterprise value from the latest supplied dated market snapshot.
- FCF yield = free cash flow / market capitalisation × 100.
- Sector median P/E and P/E-to-sector-median multiple.
- Caution flag when P/E is greater than 1.5× the sector median.
- Potential-discount flag when P/E is below 0.7× the sector median.
- Explicit insufficient-data status where a reliable comparison cannot be made.
- Outputs: `output/valuation_summary.xlsx` and `output/valuation_flags.csv`.

## Validation results
- Universe retained: **92 companies**.
- Valuation summary: **92 rows**.
- Market snapshot represented: **2024-03** for all 92 companies.
- One company has an interim financial-ratio period fallback; this is flagged in the valuation summary.
- **152 cumulative Sprint 1–4 tests passed, 0 failed.**
- Ten sample company profile history queries were measured at approximately 0.03 seconds total in the build environment. Python compilation passed for all source modules. The build runtime did not have Streamlit installed, so a real browser/UI test was not possible here. However, all eight page render functions passed an application-level smoke test using a Streamlit API stub, and the app entrypoint imported successfully. Streamlit and Plotly are declared in `requirements.txt`.
- Foreign-key check is expected to remain clean; see final QA log.

## Actual valuation flags
- **In line / insufficient benchmark:** 45
- **Potential discount: PE < 0.7x sector median:** 29
- **Caution: PE > 1.5x sector median:** 14
- **Insufficient valuation data:** 4

## Source-data limitations
- FCF yield is unavailable for companies where the latest annual source ratio row has no free-cash-flow value. Missing values are kept as N/A; no synthetic FCF is inserted.
- Market valuation multiples are the latest dated observations in the supplied workbook (2024-03 in this dataset), not live market prices.
- Annual report URLs are displayed as supplied; external link availability has not been independently verified.
- One company is retained with its latest available interim financial-ratio record because no March annual record exists in the supplied extract.

## Run locally
Install dependencies from `requirements.txt`, then from the Sprint 4 root:
```bash
streamlit run src/dashboard/app.py
```
Generate valuation exports:
```bash
python src/analytics/run_valuation.py
```
Run tests:
```bash
pytest tests/etl tests/kpi tests/screener tests/dashboard -q
```

This dashboard is a financial research and education tool, not investment advice.
