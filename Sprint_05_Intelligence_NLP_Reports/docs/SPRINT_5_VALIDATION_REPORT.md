# Sprint 5 — Intelligence, NLP & Reports Validation Report

## Scope
Sprint 5 adds source-grounded analysis parsing, rule-based explainable company pros/cons, cash-flow quality and risk intelligence, and PDF reporting for the supplied N100 dataset.

## NLP parser
- Parser: `src/nlp/parser.py`
- Uses the specified `N Years: X%` expression to extract year horizon and percentage.
- Parsed rows: **51**.
- Parse failures logged rather than silently discarded: **13**.
- Five-year CAGR comparisons available: **8**.
- Divergence flags greater than 5 percentage points: **0**.
- Some parsed company metrics have no matching calculated CAGR in the source ratio history; those comparisons remain missing and are not treated as zero.

Outputs: `output/analysis_parsed.csv`, `output/parse_failures.csv`, `output/cagr_divergence.csv`.

## Pros/cons generator
- Exactly 12 pro rules and 12 con rules are defined.
- Generated **802** evidence statements: 576 pro and 226 con.
- All **92 companies** have at least one pro and one con record.
- Confidence scores are all strictly greater than 60% (minimum **65%**).
- When source metrics cannot support a positive or negative conclusion, the generator emits an explicit limited-data coverage statement rather than inventing a financial claim.

Output: `output/pros_cons_generated.csv`.

## Cash-flow intelligence
- Company summary: **92 companies**.
- Distress alert records: **92**.
- Pattern-change records: **168**.
- Workbook sheets: Company Summary, Historical Quality, Cash Flow History, Distress Alerts, Pattern Changes.
- Alert rules cover leverage, interest coverage, repeated negative FCF, cash conversion and negative ROCE.
- Pattern changes compare consecutive annual observations where available.

Outputs: `output/cashflow_intelligence.xlsx`, `output/distress_alerts.csv`, `output/pattern_changes.csv`.

## PDF reporting acceptance
- Company tearsheets: **92**.
- Page count distribution: `{2: 92}` (all reports have exactly two pages).
- Minimum company PDF size: **39.9 KB** (acceptance threshold: 30 KB).
- Blank pages: **0** based on extracted text checks.
- Sector/cross-sector reports: **11**.
- Portfolio summary: `reports/portfolio/portfolio_summary.pdf`.
- Five representative company first pages were rendered and visually spot-checked; evidence image: `reports/tearsheet_visual_spotcheck.png`.

**Sector-data caveat:** the supplied sector master contains **10 distinct broad-sector labels**, not 11. The package therefore contains 10 actual sector PDFs plus one Nifty 100 cross-sector benchmark PDF to meet the requested total of 11 without inventing an additional sector.

## Reproducibility
Run all Sprint 5 outputs:
```bash
python src/reports/run_sprint5.py
```
Run cumulative tests:
```bash
pytest tests/etl tests/kpi tests/screener tests/dashboard tests/nlp tests/reports -q
```

Sprint 5 is a descriptive financial research and education feature set, not investment advice.
