# N100 Financial Intelligence Platform — Sprint 4

Sprint 4 adds the Streamlit dashboard and relative-valuation engine on top of Sprint 3.

## Run the dashboard
From this folder:

```bash
pip install -r requirements.txt
streamlit run src/dashboard/app.py
```

The app contains eight screens: Home, Company Profile, Screener, Peer Comparison, Financial Trends, Sector Intelligence, Capital Allocation, and Annual Reports.

## Generate valuation exports

```bash
python src/analytics/run_valuation.py
```

Outputs:
- `output/valuation_summary.xlsx` — 92-company valuation summary
- `output/valuation_flags.csv` — caution, potential-discount and insufficient-data flags

## Tests

```bash
pytest tests/etl tests/kpi tests/screener tests/dashboard -q
```

## Important data notes
- Market multiples are from the latest dated market snapshot in the supplied dataset (2024-03), not live quotes.
- FCF yield remains N/A when the source free-cash-flow metric is missing.
- P/E flags compare a company's P/E with its sector median; they are screening indicators, not buy/sell recommendations.
- Annual report URLs are displayed as supplied and are not independently verified.

See `docs/SPRINT_4_VALIDATION_REPORT.md` for the full implementation and QA summary.
