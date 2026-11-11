<div align="center">

# N100 Financial Intelligence Platform
### Enterprise Fundamental Analysis, Quantitative Equity Screening & Analytics Engine for Nifty 100

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Tests-201%20Passed%20(100%25)-brightgreen?logo=pytest&logoColor=white)](reports/pytest_report.html)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57?logo=sqlite&logoColor=white)](data/nifty100.db)
[![ReportLab](https://img.shields.io/badge/Reports-ReportLab%20PDF-D32F2F)](reports/tearsheets/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An institutional-grade quantitative equity research platform engineered to process, normalize, analyze, screen, and visualize 12 historical financial statement datasets for the Nifty 100 universe.

[Key Features](#key-features) • [Architecture](#system-architecture) • [Quickstart](#quickstart) • [API Reference](#fastapi-rest-service) • [Dashboard](#streamlit-intelligence-dashboard) • [Testing](#test-suite--qa)

</div>

---

## System Architecture

```
                        ┌────────────────────────────────────────┐
                        │      12 Raw Excel Datasets (Bluestock) │
                        │  (P&L, BS, CF, Ratios, MCap, Sectors)  │
                        └───────────────────┬────────────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │    ETL & Data Foundation    │
                             │  - Strict Primary & FKs     │
                             │  - Ticker & Date Normalizer │
                             │  - Explicit Data Quarantine │
                             └──────────────┬──────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │ SQLite Database (nifty100)  │
                             │   21 Tables | 92 Companies  │
                             └──────────────┬──────────────┘
                                            │
                       ┌────────────────────┼────────────────────┐
                       ▼                    ▼                    ▼
        ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
        │ Ratio Engine (Sprint 2)│ │ Screener Engine (Sprint 3)│ │ Clustering ML (Sprint 6)│
        │ - 50+ Financial KPIs │ │ - 15 Dynamic Filters │ │ - K-Means (5 Groups) │
        │ - Turnaround CAGR    │ │ - 6 Curated Presets  │ │ - Centroid Distance  │
        │ - Capital Allocation │ │ - 92 Radar Charts    │ │ - Elbow & Heatmaps   │
        └──────────────┬───────┘ └──────────┬───────────┘ └──────────┬───────────┘
                       │                    │                        │
                       └────────────────────┼────────────────────────┘
                                            │
               ┌────────────────────────────┴───────────────────────────┐
               ▼                                                        ▼
┌──────────────────────────────┐                         ┌──────────────────────────────┐
│  Streamlit Visual Dashboard  │                         │   FastAPI REST API Service   │
│  - 8 Interactive Screens     │                         │  - 16 Core Business Routes   │
│  - Dynamic Filter Sliders    │                         │  - Sub-20ms Query Latency    │
│  - Plotly Time-Series & Pies │                         │  - Live Swagger/OpenAPI Spec │
└──────────────────────────────┘                         └──────────────────────────────┘
               │                                                        │
               └────────────────────────────┬───────────────────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │ Institutional Report Engine │
                             │ - 92 Two-Page Tearsheets    │
                             │ - 11 Sector PDF Summaries   │
                             │ - Master Portfolio Summary  │
                             └─────────────────────────────┘
```

---

## Key Features

### 1. Robust Data Foundation & Ingestion
- **12 Comprehensive Datasets:** Direct ingestion from raw Excel extracts (`profitandloss`, `balancesheet`, `cashflow`, `financial_ratios`, `market_cap`, `peer_groups`, `sectors`, `stock_prices`, etc.).
- **Dual Header Layout Engine:** Automatically differentiates between tabular files (`header=0`) and Bluestock banner workbooks (`header=1`).
- **Relational Integrity:** SQLite schema enforcing primary keys and foreign key constraints against a 92-company master table. Non-matching source rows are isolated in quarantine tables rather than dropped.

### 2. Quantitative Financial Ratio Engine
- **50+ Derived Ratios:** Net profit margin, operating margin, return on equity (ROE), return on capital employed (ROCE), debt-to-equity (D/E), interest coverage (ICR), asset turnover, and FCF conversion.
- **CAGR Turnaround Logic:** Strictly detects negative base years and returns `TURNAROUND` instead of distorted exponential percentages.
- **Zero-Interest Protection:** Filers with zero interest expense are categorized as `Debt Free` without division-by-zero errors.
- **Capital Allocation Taxonomy:** Automatically maps CFO, CFI, and CFF sign permutations into 8 corporate allocation patterns (e.g., *Self-Funded Reinvestment*, *Debt/Dividend Harvesting*, *Severe Burn*).

### 3. Config-Driven Equity Screener
- **15 Filter Metrics:** Configured via YAML (`config/screener_config.yaml`) across profitability, growth, leverage, valuation, and cash generation.
- **6 Institutional Presets:**
  - *Quality Compounder:* ROE $\ge$ 15%, D/E $\le$ 1.0, FCF > 0, 5Y Revenue CAGR $\ge$ 10%.
  - *Value Pick:* P/E $\le$ 20, P/B $\le$ 3.0, D/E $\le$ 2.0, Dividend Yield $\ge$ 1.0%.
  - *Growth Accelerator:* 5Y PAT CAGR $\ge$ 20%, 5Y Sales CAGR $\ge$ 15%, D/E $\le$ 2.0.
  - *Dividend Champion:* Dividend Yield $\ge$ 2.0%, Payout $\le$ 80%, FCF > 0.
  - *Debt-Free Blue Chip:* D/E = 0, ROE $\ge$ 12%, Revenue $\ge$ ₹5,000 Cr.
  - *Turnaround Watch:* 3Y Sales CAGR $\ge$ 10%, FCF > 0, Declining D/E leverage.
- **Banking Sector Rule:** Financials are exempted from standard Debt-to-Equity caps to preserve regulatory capital accounting.
- **92 Spider Radar Charts:** 5-axis normalized charts generated for every universe company comparing it to sector medians.

### 4. Interactive Streamlit Dashboard (8 Screens)
1. **01 Home:** Broad market overview, sector capitalization weights, top-quality rankings, and score distribution.
2. **02 Company Profile:** Interactive financial statement history, KPI cards, and annual report links.
3. **03 Screener:** Live multi-slider parameter filtering across 15 criteria with preset selection.
4. **04 Peer Comparison:** Constituent benchmarking, percentile ranks, and radar chart visualizer.
5. **05 Financial Trends:** Plotly time-series charts for revenue, PAT, and margin trajectories.
6. **06 Sector Intelligence:** Sector breakdown, aggregate market cap, and median ROCE rankings.
7. **07 Capital Allocation:** CFO/CFI/CFF waterfall and 8-pattern allocation archetype categorization.
8. **08 Annual Reports:** Corporate filing catalog with direct regulatory document links.

### 5. Production REST API (FastAPI)
- **High-Performance Endpoints:** 16 business routes with sub-20ms latency serving company profiles, balance sheets, cash flows, ratio tables, peer rankings, sector metrics, and portfolio stats.
- **Auto-Generated Documentation:** Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) with OpenAPI 3.1.0 specifications.

### 6. Automated PDF Reporting Engine
- **92 Company Tearsheets:** Standardized 2-page institutional tear sheets generated via ReportLab with zero blank pages. Page 1 presents profile data, valuation multiples, and 5-year financials; Page 2 embeds the radar chart, capital allocation breakdown, and rule-derived pros/cons.
- **11 Sector Research Reports:** 1-page sector summaries detailing constituent rankings, median profitability, and market weights.
- **Portfolio Summary PDF:** Executive overview of total universe fundamentals, market cap concentration, and risk metrics.

### 7. Machine Learning Archetypal Clustering
- **K-Means Model:** Segregates 92 companies into 5 distinct quantitative archetypes using normalized financial features.
- **Artifacts:** Generates `cluster_labels.csv`, `elbow_plot.png`, `correlation_heatmap.png`, and `outlier_report.csv`.

---

## Repository Structure

```
N100-Financial-Intelligence-Platform/
├── config/
│   └── screener_config.yaml             # 15 filter bounds & 6 preset definitions
├── data/
│   ├── raw/                             # 12 original source Excel files (Bluestock)
│   ├── processed/                       # 12 normalized CSV data extracts
│   └── nifty100.db                      # Canonical SQLite database (2.03 MB)
├── db/
│   └── schema.sql                       # Full relational database DDL schema
├── docs/
│   ├── acceptance_checklist.pdf         # Verified 23-deliverable acceptance sign-off
│   ├── analyst_guide.pdf                # Quantitative user guide for research analysts
│   ├── DELIVERABLES_VERIFICATION.md     # Granular verification matrix for all 23 items
│   ├── FINAL_ACCEPTANCE_REPORT.md       # Final engineering sign-off report
│   ├── FINAL_PROJECT_AUDIT.md           # Discovery audit & defect resolution record
│   ├── KNOWN_LIMITATIONS.md             # Dataset boundaries & methodological disclosures
│   └── openapi.json                     # OpenAPI 3.1.0 specification export
├── notebooks/
│   └── exploratory_queries.sql          # 10 exploratory SQL queries
├── output/                              # Generated workbooks & analytical CSVs
│   ├── capital_allocation.csv           # 1,155-row capital allocation patterns
│   ├── cashflow_intelligence.xlsx       # 5-sheet cash-flow intelligence workbook
│   ├── cluster_labels.csv               # 92-company K-Means cluster assignments
│   ├── load_audit.csv                   # 12-table ETL load audit manifest
│   ├── peer_comparison.xlsx             # 11-sheet peer group rankings (20 metrics)
│   ├── pros_cons_generated.csv          # 802 rule-derived pros and cons
│   ├── screener_output.xlsx             # 6-sheet preset screener results
│   ├── validation_failures.csv          # 1,480 logged data quality findings
│   └── valuation_summary.xlsx           # 92-company valuation multiples & flags
├── reports/
│   ├── portfolio/
│   │   └── portfolio_summary.pdf        # Nifty 100 portfolio executive summary
│   ├── radar_charts/                    # 92 company radar charts (.png)
│   ├── sector/                          # 11 sector PDF tear sheets
│   ├── tearsheets/                      # 92 two-page company PDF tear sheets
│   └── pytest_report.html               # Self-contained pytest execution report
├── src/
│   ├── analytics/                       # CAGR, ratios, valuation, clustering
│   ├── api/                             # FastAPI application & route controllers
│   ├── dashboard/                       # Streamlit 8-screen multipage application
│   ├── etl/                             # Ingestion loader, normalizer, validator
│   ├── nlp/                             # Financial statement parser & pros/cons rules
│   ├── reports/                         # ReportLab PDF tearsheet generators
│   └── screener/                        # Screener engine, peer rankings, radar plots
├── tests/                               # 201 automated unit, integration, & regression tests
│   ├── api/                             # FastAPI endpoint verification
│   ├── clustering/                      # K-Means clustering assertions
│   ├── dashboard/                       # Streamlit UI & valuation tests
│   ├── etl/                             # Data ingestion & normalization tests
│   ├── kpi/                             # Mathematical ratio & edge case tests
│   ├── nlp/                             # NLP parsing & pros/cons rule tests
│   ├── reports/                         # PDF page count & visual spotcheck tests
│   └── screener/                        # Screener filters & preset result tests
├── Makefile                             # GNU Make build runner
├── make.bat                             # Windows CMD build runner
├── pytest.ini                           # Test configuration & module path settings
├── README.md                            # Project documentation
├── requirements.txt                     # Pinned project dependencies
└── run.ps1                              # Windows PowerShell build runner
```

---

## Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.12.10)
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Raghunath2604/N100-Financial-Intelligence-Platform.git
cd N100-Financial-Intelligence-Platform

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# or: .venv\Scripts\activate     # Windows PowerShell
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Build & Run
You can run any pipeline stage using **Make**, **PowerShell**, or **CMD**:

| Command | Action |
|---|---|
| `make load` (or `.\run.ps1 load`) | Ingest raw Excel workbooks into SQLite database |
| `make ratios` (or `.\run.ps1 ratios`) | Compute 50+ financial ratios & capital allocation |
| `make screener` (or `.\run.ps1 screener`) | Execute screener presets & generate 92 radar charts |
| `make clustering` (or `.\run.ps1 clustering`) | Execute K-Means clustering & generate QA plots |
| `make report` (or `.\run.ps1 report`) | Generate 92 PDF tearsheets, 11 sector reports, portfolio PDF |
| `make test` (or `.\run.ps1 test`) | Run full 201-test suite with HTML report generation |
| `make dashboard` (or `.\run.ps1 dashboard`) | Launch Streamlit visual dashboard on `localhost:8501` |
| `make api` (or `.\run.ps1 api`) | Launch FastAPI REST service on `localhost:8000` |
| `make clean` (or `.\run.ps1 clean`) | Remove cache files safely (preserves database and reports) |

---

## FastAPI REST Service

Start the API:
```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Open **`http://127.0.0.1:8000/docs`** in your browser for interactive Swagger API documentation.

### Core Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Service health status check |
| `GET` | `/companies` | Paginated list of master companies (`limit`, `offset`) |
| `GET` | `/companies/{company_id}` | Detailed company profile and about data |
| `GET` | `/companies/{company_id}/profit-loss` | Historical Profit & Loss statement |
| `GET` | `/companies/{company_id}/balance-sheet` | Historical Balance Sheet statement |
| `GET` | `/companies/{company_id}/cash-flow` | Historical Cash Flow statement |
| `GET` | `/companies/{company_id}/ratios` | Historical calculated financial ratios |
| `GET` | `/companies/{company_id}/tearsheet` | Stream/download company 2-page PDF tearsheet |
| `GET` | `/screener` | Query equity screener with dynamic parameter filters |
| `GET` | `/sectors` | Aggregate list of broad sectors and constituent counts |
| `GET` | `/sectors/{sector_name}/companies` | Companies belonging to a specific sector |
| `GET` | `/peers/{company_id}` | Peer group members for a company |
| `GET` | `/peers/{company_id}/comparison` | Fundamental metrics comparison against peers |
| `GET` | `/valuation/market-cap-history/{company_id}` | Historical market cap and valuation multiples |
| `GET` | `/portfolio/stats` | Aggregate portfolio statistics across the universe |
| `GET` | `/documents/{company_id}` | Annual report filing repository links |

---

## Streamlit Intelligence Dashboard

Launch the dashboard:
```bash
streamlit run src/dashboard/app.py --server.port 8501
```
Open **`http://localhost:8501`** to interact with the platform across all 8 screens:
- Filter companies interactively with slider thresholds.
- Toggle between historical fiscal years (2019–2024).
- Inspect high-resolution Plotly trend charts, peer percentiles, and capital allocation waterfall distributions.

---

## Test Suite & QA

The repository includes a comprehensive 201-test automated suite ensuring total mathematical and functional consistency.

```bash
python -m pytest --html=reports/pytest_report.html --self-contained-html -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 201 items

tests/api/test_api.py ....................                               [  9%]
tests/clustering/test_clustering.py ..........                           [ 14%]
tests/dashboard/test_sprint4.py ................                         [ 22%]
tests/etl/test_integration.py ...                                        [ 23%]
tests/etl/test_normalise_ticker.py ...............                       [ 31%]
tests/etl/test_normalise_year.py ......................                  [ 42%]
tests/kpi/test_engine_integration.py ...                                 [ 43%]
tests/kpi/test_financial_formula_rules.py ................               [ 51%]
tests/kpi/test_formula_engine.py .................                       [ 60%]
tests/nlp/test_sprint5_nlp.py ........                                   [ 64%]
tests/reports/test_sprint5_reports.py ...........                        [ 69%]
tests/screener/test_screener_peer.py .........................           [ 82%]
tests/screener/test_sprint3_acceptance.py ........                       [100%]

====================== 201 passed, 2 warnings in 40.07s =======================
```

- **Test Pass Rate:** **100% (201 passed, 0 failed)**
- **Report Location:** [`reports/pytest_report.html`](reports/pytest_report.html)

---

## Methodological Disclosures & Data Rules

1. **Source Lineage:** Based on historical extracts for 92 master companies supplied by Bluestock Fintech. Delisted tickers and non-matching entries are strictly quarantined in dedicated database tables.
2. **No Data Fabrication:** Missing historical statement years are never populated with arbitrary or synthetic figures.
3. **Turnaround Accounting:** Companies transitioning from negative base years to positive profits receive an explicit `TURNAROUND` label rather than distorted standard CAGRs.
4. **Financials Leverage Accounting:** Banking and financial institutions are exempted from universal D/E screener caps in adherence to financial accounting conventions.
5. **Simulated Multiples:** Market capitalization and price metrics are historical snapshots and labeled as **SIMULATED** across reports.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
