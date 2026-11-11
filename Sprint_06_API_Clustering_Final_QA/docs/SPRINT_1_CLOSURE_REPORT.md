# Sprint 1 — Data Foundation: Closure Report

## Acceptance evidence
- 12/12 supplied Excel workbooks present and ingested.
- Company master count: 92 (expected 92).
- SQLite database generated at `database/nifty100.db`.
- 12 source datasets represented as curated tables; all source rows are either loaded or preserved in quarantine.
- Source records: 12892; curated rows: 12454; quarantined rows: 438.
- SQLite `PRAGMA foreign_key_check`: 0 violations.
- Critical DQ findings: 0.
- Automated ETL tests: 44 passed, 0 failed.
- Manual review: TCS, HDFCBANK, RELIANCE, INFY, SUNPHARMA; see `output/manual_review_5_companies.csv`.
- ETL audit: `output/load_audit.csv`.
- DQ report: `output/validation_failures.csv`.
- Quarantine report: `output/quarantine_manifest.csv`.
- 10 exploratory SQL queries: `notebooks/exploratory_queries.sql`.

## DQ outcome
The current ETL run reports 0 critical, 1044 warning and 436 informational findings. The unmatched company references are warnings because their source rows are retained in quarantine tables; no invalid company reference is inserted into curated tables. No records are silently deleted.

## Deferred to Sprint 2 (as requested)
1. Reconcile the 8 source ticker values absent from the 92-company master with the data owner; 438 affected records are preserved in quarantine.
2. Review and classify source OPM/tax/dividend/EPS anomalies; do not overwrite source values.
3. Complete annual-report URL reachability checks (52 URLs are missing; non-empty URLs were not checked online).
4. Review non-standard financial reporting periods and confirm whether all should be included in annual KPI calculations.
5. Confirm the physical table-count wording with the project lead. The source specification defines 7 core + 5 supplementary datasets (12 files), while the portal text says 10 tables and its displayed table inventory is inconsistent. All 12 supplied datasets are preserved in the database.

## Sprint 1 status
**Implementation and automated acceptance evidence complete.** Source-data remediation items above are explicitly carried forward to Sprint 2, rather than being silently hidden or fabricated.
