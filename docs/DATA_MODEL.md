# Sprint 1 Data Model

The uploaded project specification has a count inconsistency: it describes a 10-table SQLite database, while its own table inventory names 12 datasets (companies, profitandloss, balancesheet, cashflow, analysis, documents, prosandcons, sectors, market_cap, stock_prices, financial_ratios, peer_groups). The supplied Sprint 1 task also lists 11 tables while saying 10. This implementation loads all 12 supplied datasets as tables so no source data is discarded. Downstream sprint integration can refine the physical schema if the team lead confirms a different mapping.

Core workbooks use Excel header row index 1; supplementary workbooks use index 0, following the specification. Year labels are normalised to YYYY-MM. Source data is preserved in data/raw and normalized CSV snapshots are written to data/processed.
