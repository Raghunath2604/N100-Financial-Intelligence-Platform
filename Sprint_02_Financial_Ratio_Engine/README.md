# N100 Financial Intelligence Platform — Sprint 2: Financial Ratio Engine

Sprint 2 extends the Sprint 1 project and database. The package includes the Sprint 1 source workbooks, ETL pipeline, SQLite database and Sprint 2 analytics.

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run Sprint 2
```bash
python -m src.analytics.run_ratios
pytest tests/kpi tests/etl -v
```

The engine reads P&L, balance sheet, cash-flow and sector tables from `database/nifty100.db`, computes the ratio table, writes `output/financial_ratios_computed.csv` and `output/capital_allocation.csv`, and updates SQLite `financial_ratios`.

## Main outputs
- `database/nifty100.db` — updated `financial_ratios` table with enforced company foreign key
- `output/financial_ratios_computed.csv` — 68-column KPI dataset
- `output/capital_allocation.csv` — CFO/CFI/CFF sign-pattern labels
- `output/ratio_edge_cases.log` — explicit CAGR, debt-free and missing-denominator cases
- `output/ratio_formula_spotchecks.csv` — independent ROE formula checks for five companies
- `output/cagr_5y_manual_spotchecks.csv` — independent 5-year revenue CAGR checks for three companies
- `output/screener_preview_roe15_de1.csv` — required ROE/D-E screener preview (15–50 result check)
- `output/capital_allocation_pattern_summary.csv` — pattern distribution
- `output/source_ratio_comparison.csv` — comparison against company-master display ROE/ROCE fields
- `output/sector_roce_notes.csv` — financial-sector treatment and comparison notes
- `docs/SPRINT_2_VALIDATION_REPORT.md` — detailed run and known data limitations

## Formula handling
- ROE = PAT / (equity capital + reserves) × 100; NULL when equity is non-positive or unavailable.
- ROCE = EBIT / (equity + borrowings) × 100; financial sector records additionally carry sector-relative percentile context.
- D/E = borrowings / equity; high-leverage flag only for non-financial companies above 5×.
- ICR = (operating profit + other income) / interest; numeric value remains NULL for zero interest and `icr_label` is `Debt Free`.
- FCF = CFO + CFI.
- CAGR windows: 3, 5 and 10 years for revenue, PAT and EPS; turnaround, loss and zero-base cases are flagged rather than coerced.
- CFO quality, CapEx intensity, FCF conversion, distress/deleveraging and 8 capital-allocation patterns are included.

## Source-data caveat
Sprint 1 quarantined 438 source rows referencing tickers not present in the 92-company master. Sprint 2 does not invent mappings. KPI output is generated from the available curated P&L/BS/CF data. Some company-year rows have incomplete statement coverage, and their unavailable KPIs remain NULL.
