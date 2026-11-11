# N100 Financial Intelligence Platform — Sprint 5

Sprint 5 adds explainable NLP parsing, company pros/cons, cash-flow intelligence, distress and pattern-change flags, and generated PDF reporting.

## Run NLP and cash-flow pipelines
```bash
python src/nlp/parser.py
python src/nlp/pros_cons_generator.py
python -c "from src.analytics.cashflow_kpis import build_cashflow_intelligence; build_cashflow_intelligence()"
```

## Generate reports
```bash
python -c "from src.reports.tearsheet import generate_tearsheets, generate_sector_reports, generate_portfolio_summary; generate_tearsheets(); generate_sector_reports(); generate_portfolio_summary()"
```

## Test
```bash
pytest tests/etl tests/kpi tests/screener tests/dashboard tests/nlp tests/reports -q
```

## Outputs
- `output/analysis_parsed.csv`, `parse_failures.csv`, `cagr_divergence.csv`
- `output/pros_cons_generated.csv`
- `output/cashflow_intelligence.xlsx`, `distress_alerts.csv`, `pattern_changes.csv`
- `reports/tearsheets/` — 92 two-page company PDFs
- `reports/sector/` — 11 sector and cross-sector PDFs
- `reports/portfolio/portfolio_summary.pdf`

See `docs/SPRINT_5_VALIDATION_REPORT.md` for actual source-data coverage and acceptance results.
