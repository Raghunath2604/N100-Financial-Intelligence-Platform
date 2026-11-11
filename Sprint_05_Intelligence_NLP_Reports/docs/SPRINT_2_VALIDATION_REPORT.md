# Sprint 2 — Financial Ratio Engine: Final Validation

## Sprint 2 acceptance evidence
- Computed financial ratio records: **1155** (minimum required: 1,100).
- Companies represented: **92** (universe: 92).
- Computed KPI fields: **64** (minimum required: 50).
- Automated test suite: **103 passed, 0 failed**.
- SQLite foreign-key check: **0 violations**.
- `financial_ratios` has an enforced `company_id -> companies(id)` foreign key.
- Three independent five-year revenue CAGR spot checks: maximum absolute difference **0.000000 percentage points**.
- Five independent ROE spot checks: maximum absolute difference **0.000000 percentage points**.
- Screener preview `ROE > 15% AND D/E < 1` returns **35 companies**, within the required 15–50 range after excluding financial-sector companies from the universal D/E screen.

## Implemented calculations
Profitability: NPM, OPM, ROE and ROCE.
Leverage and coverage: D/E, ICR, net debt, total debt, total equity, debt-free label and high-leverage flag.
Efficiency: asset turnover, EBIT, EBITDA and book value per share.
Cash flow: FCF = CFO + CFI, CFO/PAT, five-year CFO quality, CapEx intensity, FCF conversion, negative-FCF flags, distress and deleveraging flags.
Growth: revenue, PAT and EPS YoY growth and 3Y/5Y/10Y CAGR values with explicit edge-case flags.
Capital allocation: all eight non-zero CFO/CFI/CFF sign patterns plus neutral/mixed and incomplete-data labels.
Sector handling: financial-sector D/E leverage flag suppression and sector-relative ROCE percentile context.
OPM cross-check: source OPM compared to computed OPM; differences greater than one percentage point are flagged.

## Formula edge cases
- Zero denominators return NULL rather than infinity.
- Zero-interest records are labelled `Debt Free`; numeric ICR is NULL.
- ROE is NULL when equity is non-positive or missing.
- CAGR sign changes, zero base, declines to loss, and insufficient history are flagged.
- Financial companies are excluded from the universal high D/E risk flag.
- Missing statement inputs remain NULL and are not fabricated.

## Key outputs
- `output/financial_ratios_computed.csv`
- `output/capital_allocation.csv`
- `output/capital_allocation_pattern_summary.csv`
- `output/ratio_edge_cases.log`
- `output/ratio_formula_spotchecks.csv`
- `output/cagr_5y_manual_spotchecks.csv`
- `output/source_ratio_comparison.csv`
- `output/screener_preview_roe15_de1.csv`
- `output/sprint2_metrics_summary.json`

## Source-data caveat carried forward
Sprint 1 unmatched ticker rows and incomplete statement periods remain documented. This sprint computes only from the curated, mapped statement records. The precomputed source ratio workbook has 1,184 rows; the computed output has 1155 rows because the KPI engine uses valid annual statement periods and available statement coverage. This difference is not concealed or padded with invented records.
