# N100 Financial Intelligence Platform — Known Boundaries & Limitations

**Document Version:** 1.0.0  
**Date:** November 2026  
**Auditor:** Quantitative Systems & Lead Financial Engineer  

---

## 1. Overview & Analytical Boundaries

The N100 Financial Intelligence Platform operates on a curated snapshot of 92 master companies from the Nifty 100 universe supplied by Bluestock Fintech. In strict accordance with financial engineering best practices and project governance rules:
- **No data fabrication:** Missing historical financial years are never filled with synthetic numbers.
- **Lineage preservation:** Non-conforming or unassigned records are preserved in explicit quarantine tables and exclusion manifests.
- **Simulation transparency:** Market prices and capitalization metrics are historical snapshots, not real-time streaming tickers.

This document details the observed characteristics, boundaries, and domain-specific caveats of the dataset.

---

## 2. Dataset & Historical Scope Boundaries

### 2.1 Universe Size (92 vs 100 Companies)
- The supplied project dataset contains 92 primary company records in `companies.xlsx` (not 100).
- All downstream systems (ETL loader, ratio engine, screener, valuation summary, clustering, tearsheets) are consistently anchored to these 92 verified master companies.
- Source records referencing tickers outside these 92 companies (e.g., in `profitandloss.xlsx` or `cashflow.xlsx`) were quarantined to maintain relational database integrity.

### 2.2 Preserved Source Quarantine Records (1,480 Data Quality Findings)
- Ingestion validator identified 1,480 data-quality anomalies logged in `output/validation_failures.csv`.
- These include records with company tickers absent from the 92-company master (e.g., historical delistings or acquisitions).
- These rows are safely quarantined in dedicated SQLite tables (`profitandloss_quarantine`, `balancesheet_quarantine`, `cashflow_quarantine`, etc.) rather than being silently dropped or altered.

### 2.3 Non-Standard Fiscal Year-Ends (SIEMENS Fallback)
- The majority of Indian corporate filers report annual statements ending in March (`YYYY-03`).
- However, certain multinational subsidiaries operate on alternate fiscal calendars (e.g., `SIEMENS` reporting on a September fiscal year-end `YYYY-09`).
- **Engine Handling:** The screener and valuation engines prioritize annual March periods (`month == '03'`). For tickers with no March statement, the engine activates a documented fallback to the latest available annual statement (`annual_period_fallback = True`), preventing ticker exclusion while maintaining reporting integrity.

### 2.4 History Depth Variations
- Established conglomerates (e.g., `HDFCBANK`, `RELIANCE`, `TCS`, `INFY`) have up to 12 years of historical statements (2012–2024), allowing complete 3-year, 5-year, and 10-year CAGR calculations.
- Newly demerged or recently listed entities (e.g., `JIOFIN` with 2 years of history, `ZOMATO` with limited profitable history) have insufficient data for 5-year or 10-year CAGRs.
- These return explicit categorical flags (`INSUFFICIENT_DATA`, `TURNAROUND`, `ZERO_BASE`) rather than speculative values.

---

## 3. Financial Ratio & Accounting Nuances

### 3.1 Financials & Banking Sector Accounting
- Conventional non-financial metrics do not apply cleanly to Banks and NBFCs:
  - **Debt-to-Equity (D/E):** For banks, deposits and borrowings represent operational inventory rather than traditional leverage. As mandated by project rules, the screener engine explicitly excludes Financials from the universal D/E screen (`de_max`).
  - **ROCE:** Operating profit (EBIT) is not reported for banks; ROCE is substituted with sector-relative percentile ranking.
  - **CFO / PAT:** Operating cash flow for banks includes changes in deposits and loans, leading to volatile or negative CFO figures that do not indicate operational distress.

### 3.2 Negative Base Year CAGR (Turnaround Rule)
- When computing compounded annual growth rate (CAGR), standard exponential formulas fail when the base year is negative (e.g., moving from a loss of -50 Cr to a profit of 100 Cr).
- As mandated by project rules, the engine detects negative base periods and returns:
  `Value: None, Flag: TURNAROUND`
- This ensures users are not misled by meaningless mathematical artifacts.

### 3.3 Zero Interest ICR ("Debt Free" Rule)
- For companies operating with zero debt or zero interest expense, conventional Interest Coverage Ratio `EBIT / Interest` would result in a division-by-zero error.
- The platform evaluates interest expense and populates `icr_label = "Debt Free"` when interest equals zero.

---

## 4. Analytical Presets & Cluster Findings

### 4.1 Strict Screener Presets (Value Pick Count)
- The *Value Pick* preset (`P/E <= 20`, `P/B <= 3`, `D/E <= 2`, `Dividend Yield >= 1%`) returns 2 companies in the current dataset (`COALINDIA`, `ONGC`).
- In contemporary Indian large-cap markets, consumer and technology compounders trade at elevated multiples (P/E 40x–80x). The engine preserves the strict configured thresholds without artificially weakening the filters, reporting the true market reality.

### 4.2 Peer Group Assignment Coverage
- The benchmark taxonomy in `peer_groups.xlsx` defines 11 specialized peer groups covering 56 companies.
- 36 companies in diversified or emerging segments (e.g., conglomerates, specialized logistics) do not belong to one of the 11 defined peer groups.
- These 36 companies are explicitly reported in `output/companies_without_peer_group.csv` with status `"No peer group assigned"` rather than being arbitrarily forced into mismatched groups.

### 4.3 Simulated Market Multiples
- Daily stock prices (`stock_prices.xlsx`) and valuation snapshots (`market_cap.xlsx`) represent simulated historical extracts.
- Both the Streamlit dashboard and PDF tear sheets clearly caption these figures as **SIMULATED / HISTORICAL DATA**, avoiding confusion with real-time exchange feeds.

---

## 5. Summary & Governance

All known boundaries are explicitly documented, handled with graceful fallbacks, and supported by automated regression tests. The platform maintains total fidelity to the underlying data without artificial extrapolation.
