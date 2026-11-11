# N100 Financial Intelligence Platform — Master Integrated Engineering Runbook

**Enterprise Grade Financial Intelligence & Quantitative Screening Platform for Nifty 100 Equities**

---

## 1. Executive Overview

The **N100 Financial Intelligence Platform** is an institutional-grade equity analysis, quantitative screening, fundamental ratio computation, machine-learning clustering, and report generation system built on 12 historical financial statement datasets for the Nifty 100 universe.

The platform was built across six structured engineering sprints and is now fully integrated, tested, and certified:
- **Sprint 1 — Data Foundation:** Ingestion of 12 source Excel files into SQLite (`nifty100.db`) with strict primary key/foreign key constraints and quarantine logging.
- **Sprint 2 — Financial Ratio Engine:** Computation of 50+ profitability, liquidity, solvency, growth, and cash-flow ratios, capital allocation classification, and CAGR edge handling.
- **Sprint 3 — Screener & Peer Engine:** 15-filter equity screener, 6 configured presets, winsorized composite quality scores, peer group percentile rankings, and 92 radar spider charts.
- **Sprint 4 — Dashboard & Valuation:** 8-screen interactive Streamlit dashboard and valuation multiple analysis (P/E, P/B, EV/EBITDA, FCF yield).
- **Sprint 5 — Intelligence, NLP & Reports:** NLP parsing of commentary notes, 12 deterministic pros/cons rules, cash flow intelligence workbook, 92 company tearsheets, 11 sector reports, and portfolio summary PDF.
- **Sprint 6 — API, Clustering & Final QA:** 16-endpoint FastAPI REST service, 5-cluster K-Means archetypal grouping, analyst guide, and automated testing suite.

---

## 2. Quickstart & Build Automation

The platform supports GNU Make, Windows Command Prompt (`make.bat`), and PowerShell (`.\run.ps1`).

### 2.1 Using Make (Linux / macOS / Windows with Make)
```bash
make install     # Install pinned dependencies
make load        # Run ETL ingestion and build SQLite database
make ratios      # Compute financial ratios & capital allocation
make screener    # Run equity screener presets and radar charts
make clustering  # Execute K-Means clustering pipeline
make report      # Generate PDF tearsheets, sector reports, portfolio PDF
make test        # Run 201-test pytest suite and generate reports/pytest_report.html
make dashboard   # Start Streamlit dashboard on localhost:8501
make api         # Start FastAPI server on localhost:8000
make clean       # Remove Python cache files safely (never deletes database)
```

### 2.2 Using PowerShell (Windows)
```powershell
.\run.ps1 load
.\run.ps1 ratios
.\run.ps1 screener
.\run.ps1 clustering
.\run.ps1 report
.\run.ps1 test
.\run.ps1 dashboard
.\run.ps1 api
.\run.ps1 clean
```

### 2.3 Using Windows Command Prompt (CMD)
```cmd
make.bat load
make.bat ratios
make.bat screener
make.bat clustering
make.bat report
make.bat test
make.bat dashboard
make.bat api
make.bat clean
```

---

## 3. Project Deliverables Matrix (23 Core Deliverables)

| ID | Deliverable | Expected & Canonical Location | Size | Verification Status |
|---|---|---|---|---|
| **D-01** | `nifty100.db` | `data/nifty100.db` | 2.03 MB | **DONE AND VERIFIED** |
| **D-02** | `load_audit.csv` | `output/load_audit.csv` | 624 B | **DONE AND VERIFIED** |
| **D-03** | `validation_failures.csv` | `output/validation_failures.csv` | 184 KB | **DONE AND VERIFIED** |
| **D-04** | `exploratory_queries.sql` | `notebooks/exploratory_queries.sql` | 765 B | **DONE AND VERIFIED** |
| **D-05** | `financial_ratios table` | `data/nifty100.db` | 2.03 MB | **DONE AND VERIFIED** |
| **D-06** | `capital_allocation.csv` | `output/capital_allocation.csv` | 82 KB | **DONE AND VERIFIED** |
| **D-07** | `screener_output.xlsx` | `output/screener_output.xlsx` | 128 KB | **DONE AND VERIFIED** |
| **D-08** | `screener_config.yaml` | `config/screener_config.yaml` | 516 B | **DONE AND VERIFIED** |
| **D-09** | `peer_comparison.xlsx` | `output/peer_comparison.xlsx` | 36 KB | **DONE AND VERIFIED** |
| **D-10** | 92 Radar Charts | `reports/radar_charts/` | 92 PNGs | **DONE AND VERIFIED** |
| **D-11** | Streamlit Dashboard | `src/dashboard/app.py` | 8 screens | **DONE AND VERIFIED** |
| **D-12** | `valuation_summary.xlsx` | `output/valuation_summary.xlsx` | 19 KB | **DONE AND VERIFIED** |
| **D-13** | `cashflow_intelligence.xlsx` | `output/cashflow_intelligence.xlsx` | 136 KB | **DONE AND VERIFIED** |
| **D-14** | `pros_cons_generated.csv` | `output/pros_cons_generated.csv` | 128 KB | **DONE AND VERIFIED** |
| **D-15** | `analysis_parsed.csv` | `output/analysis_parsed.csv` | 3.3 KB | **DONE AND VERIFIED** |
| **D-16** | 92 Company Tearsheets | `reports/tearsheets/` | 92 PDFs | **DONE AND VERIFIED** |
| **D-17** | 11 Sector Reports | `reports/sector/` | 11 PDFs | **DONE AND VERIFIED** |
| **D-18** | Portfolio Summary PDF | `reports/portfolio/` | 1 PDF | **DONE AND VERIFIED** |
| **D-19** | `cluster_labels.csv` | `output/cluster_labels.csv` | 4.6 KB | **DONE AND VERIFIED** |
| **D-20** | FastAPI Server (16 Endpoints) | `src/api/main.py` | 16 routes | **DONE AND VERIFIED** |
| **D-21** | `pytest_report.html` | `reports/pytest_report.html` | 177 KB | **DONE AND VERIFIED** |
| **D-22** | `analyst_guide.pdf` | `docs/analyst_guide.pdf` | 3.0 KB | **DONE AND VERIFIED** |
| **D-23** | `acceptance_checklist.pdf` | `docs/acceptance_checklist.pdf` | 4.5 KB | **DONE AND VERIFIED** |

---

## 4. Key Accounting & Financial Data Rules

1. **Workbook Header Layout:** The 7 Bluestock financial workbooks (`analysis.xlsx`, `balancesheet.xlsx`, `cashflow.xlsx`, `companies.xlsx`, `documents.xlsx`, `profitandloss.xlsx`, `prosandcons.xlsx`) contain title banners at row 0 and are ingested with `pd.read_excel(path, header=1)`. The 5 tabular datasets (`financial_ratios.xlsx`, `market_cap.xlsx`, `peer_groups.xlsx`, `sectors.xlsx`, `stock_prices.xlsx`) are ingested with `header=0`.
2. **Identifier Normalization:** All `company_id` and ticker fields are normalized to trimmed uppercase strings prior to any database joins or table writes.
3. **Monetary Unit Consistency:** All monetary figures are standardized in **INR Crore**.
4. **Financial Sector D/E Exclusion:** Banks and financial institutions are exempted from universal Debt-to-Equity caps in screener presets, reflecting regulatory capital accounting.
5. **Turnaround CAGR:** Negative base years return `TURNAROUND` rather than misleading standard exponential CAGRs.
6. **Zero Interest ICR:** Companies with zero interest expense are classified as `Debt Free` rather than throwing division-by-zero errors.
7. **Simulated Data Transparency:** Market prices and market cap snapshots are explicitly labeled as **SIMULATED** across dashboards and tearsheets.

---

## 5. Live Services Verification

### FastAPI REST Service
Start the server:
```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
- Interactive Swagger documentation: `http://127.0.0.1:8000/docs`
- OpenAPI Specification: `http://127.0.0.1:8000/openapi.json`
- 16 core business endpoints covering company fundamentals, financial statements, ratios, screener, sectors, peers, valuation, documents, and portfolio stats.

### Streamlit Intelligence Dashboard
Launch the dashboard:
```bash
streamlit run src/dashboard/app.py --server.port 8501
```
Navigate via the sidebar across 8 screens:
- **01 Home:** Market intelligence overview, sector distribution, top quality ranking.
- **02 Company Profile:** Interactive fundamental history, financial KPI cards, and annual report filings.
- **03 Screener:** Dynamic parameter filtering across 15 criteria with preset selection.
- **04 Peer Comparison:** Sector percentile distribution and 5-axis radar chart visualizer.
- **05 Financial Trends:** Time-series analysis of revenues, PAT, and margin trajectories.
- **06 Sector Intelligence:** Sector composition, aggregate market cap, and median ROCE rankings.
- **07 Capital Allocation:** CFO/CFI/CFF waterfall and 8-pattern allocation archetype categorization.
- **08 Annual Reports:** Document repository with direct links to regulatory filings.

---

## 6. Automated Testing Suite

Run the full pytest suite with HTML report generation:
```bash
python -m pytest --html=reports/pytest_report.html --self-contained-html -v
```
- **Test Count:** 201 tests across 8 test modules.
- **Pass Rate:** 100% (201 passed, 0 failed).
- **Report Location:** `reports/pytest_report.html`.

---

## 7. Documentation Index

- `docs/FINAL_ACCEPTANCE_REPORT.md`: Comprehensive engineering sign-off report.
- `docs/FINAL_PROJECT_AUDIT.md`: Complete Phase 1 discovery audit and defect resolution history.
- `docs/DELIVERABLES_VERIFICATION.md`: Evidence and verification standard for all 23 deliverables.
- `docs/KNOWN_LIMITATIONS.md`: Dataset boundaries, fiscal calendar nuances, and simulation details.
- `docs/analyst_guide.pdf`: Quantitative user guide for financial analysts.
- `docs/acceptance_checklist.pdf`: Executive acceptance matrix sign-off document.
