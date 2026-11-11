# Sprint 1 — Final Execution Report

## Delivered and verified
- All 12 supplied Excel workbooks are included under `data/raw/`.
- All source rows are ingested or explicitly quarantined; none are silently dropped.
- SQLite database: `database/nifty100.db`.
- 12 curated source tables have `id` primary keys.
- Tables containing `company_id` enforce a foreign key to `companies(id)`.
- Unmatched source rows are preserved in corresponding `*_quarantine` tables and listed in `output/quarantine_manifest.csv`.
- All 16 DQ checks (DQ-01 through DQ-16) are implemented.
- 44 automated tests pass.
- `PRAGMA foreign_key_check` returns 0 violations.
- 10 exploratory SQL queries are included.
- Original workbooks and the project PDF are retained.

## Verified counts

| Table | Source rows | Curated rows | Quarantined |
|---|---:|---:|---:|
| companies | 92 | 92 | 0 |
| profitandloss | 1276 | 1177 | 99 |
| balancesheet | 1312 | 1227 | 85 |
| cashflow | 1187 | 1091 | 96 |
| analysis | 20 | 16 | 4 |
| documents | 1585 | 1457 | 128 |
| prosandcons | 16 | 14 | 2 |
| sectors | 92 | 92 | 0 |
| stock_prices | 5520 | 5520 | 0 |
| market_cap | 552 | 552 | 0 |
| financial_ratios | 1184 | 1160 | 24 |
| peer_groups | 56 | 56 | 0 |

- Company master: 92
- Curated rows loaded: 12454
- Rows preserved in quarantine: 438
- Foreign-key violations: 0
- Automated tests: 44 passed, 0 failed

## Source-data issues requiring data-owner decision
1. The 92-company master does not contain 8 ticker values found in other source datasets. Their 438 affected rows are preserved in quarantine, not discarded. Company metadata or ticker mappings must not be invented.
2. Some P&L periods are TTM/non-standard or unsupported. Original labels are retained in `source_year`; annual labels are normalised when possible.
3. OPM, tax percentage, dividend payout, and EPS checks produce source-data warnings. They are reported, not silently rewritten.
4. 52 annual-report URL fields are missing. Live URL checks are outside this offline run.
5. The project specification conflicts on whether the target database has 10, 11, or 12 tables. All 12 supplied datasets are loaded to preserve the provided information.

## Sign-off
The Sprint 1 implementation is runnable and automated tests pass. Curated database referential integrity is enforced. Remaining source-data warnings are visible and quarantined where required; a data owner must approve or correct them before downstream analytics treats those records as complete.
