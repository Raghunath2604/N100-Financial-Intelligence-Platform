# Sprint 6 Validation Report

- API routes (including root): 21
- Clustering rows: 92
- Unique clusters: 5
- Labelled companies: 92
- Cluster feature columns: return_on_equity_pct, debt_to_equity, revenue_cagr_5yr, fcf_cagr_5yr, operating_profit_margin_pct
- Missing-data strategy: sector median, then global median/zero only where sector has no observed values.
- Model: KMeans(n_clusters=5, random_state=42, n_init=20), StandardScaler.
- Acceptance gates documented: 20.

## Known limitations
- The underlying market snapshot is historical, not live prices.
- FCF CAGR is calculated from available positive endpoints over a sufficient observed time span; unavailable cases are imputed by sector median for clustering.
- Cluster archetype names are descriptive labels, not investment recommendations.


## Final QA evidence
- Full test suite: 201 passed, 0 failed.
- Acceptance gates: 20/20 passed.
- Python compile errors: 0.
- SQLite integrity_check: ok.
- Foreign-key violations: 0.
- Application API endpoints: 17 (excluding FastAPI's automatic documentation/schema routes).
