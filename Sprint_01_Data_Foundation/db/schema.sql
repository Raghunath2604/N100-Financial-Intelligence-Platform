-- Sprint 1 generated SQLite schema
PRAGMA foreign_keys = ON;

CREATE TABLE "analysis" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "compounded_sales_growth" TEXT, "compounded_profit_growth" TEXT, "stock_price_cagr" TEXT, "roe" TEXT);

CREATE TABLE "analysis_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "compounded_sales_growth" TEXT,
  "compounded_profit_growth" TEXT,
  "stock_price_cagr" TEXT,
  "roe" TEXT
);

CREATE TABLE "balancesheet" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "equity_capital" REAL, "reserves" INTEGER, "borrowings" INTEGER, "other_liabilities" INTEGER, "total_liabilities" INTEGER, "fixed_assets" INTEGER, "cwip" INTEGER, "investments" INTEGER, "other_asset" INTEGER, "total_assets" INTEGER, "source_year" TEXT);

CREATE TABLE "balancesheet_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "year" TEXT,
  "equity_capital" REAL,
  "reserves" INTEGER,
  "borrowings" INTEGER,
  "other_liabilities" INTEGER,
  "total_liabilities" INTEGER,
  "fixed_assets" INTEGER,
  "cwip" INTEGER,
  "investments" INTEGER,
  "other_asset" INTEGER,
  "total_assets" INTEGER,
  "source_year" TEXT
);

CREATE TABLE "cashflow" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "operating_activity" REAL, "investing_activity" REAL, "financing_activity" REAL, "net_cash_flow" REAL, "source_year" TEXT);

CREATE TABLE "cashflow_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "year" TEXT,
  "operating_activity" REAL,
  "investing_activity" REAL,
  "financing_activity" REAL,
  "net_cash_flow" REAL,
  "source_year" TEXT
);

CREATE TABLE "companies" ("id" TEXT PRIMARY KEY, "company_logo" TEXT, "company_name" TEXT, "chart_link" TEXT, "about_company" TEXT, "website" TEXT, "nse_profile" TEXT, "bse_profile" TEXT, "face_value" REAL, "book_value" REAL, "roce_percentage" REAL, "roe_percentage" REAL);

CREATE TABLE "documents" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "annual_report" TEXT, "source_year" TEXT);

CREATE TABLE "documents_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "year" TEXT,
  "annual_report" TEXT,
  "source_year" TEXT
);

CREATE TABLE "financial_ratios" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "net_profit_margin_pct" REAL, "operating_profit_margin_pct" REAL, "return_on_equity_pct" REAL, "debt_to_equity" REAL, "interest_coverage" REAL, "asset_turnover" REAL, "free_cash_flow_cr" REAL, "capex_cr" REAL, "earnings_per_share" REAL, "book_value_per_share" REAL, "dividend_payout_ratio_pct" REAL, "total_debt_cr" INTEGER, "cash_from_operations_cr" REAL, "source_year" TEXT);

CREATE TABLE "financial_ratios_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "year" TEXT,
  "net_profit_margin_pct" REAL,
  "operating_profit_margin_pct" REAL,
  "return_on_equity_pct" REAL,
  "debt_to_equity" REAL,
  "interest_coverage" REAL,
  "asset_turnover" REAL,
  "free_cash_flow_cr" REAL,
  "capex_cr" REAL,
  "earnings_per_share" REAL,
  "book_value_per_share" REAL,
  "dividend_payout_ratio_pct" REAL,
  "total_debt_cr" INTEGER,
  "cash_from_operations_cr" REAL,
  "source_year" TEXT
);

CREATE TABLE "market_cap" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "market_cap_crore" REAL, "enterprise_value_crore" REAL, "pe_ratio" REAL, "pb_ratio" REAL, "ev_ebitda" REAL, "dividend_yield_pct" REAL, "source_year" TEXT);

CREATE TABLE "peer_groups" ("id" INTEGER PRIMARY KEY, "peer_group_name" TEXT, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "is_benchmark" REAL);

CREATE TABLE "profitandloss" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "year" TEXT, "sales" INTEGER, "expenses" INTEGER, "operating_profit" REAL, "opm_percentage" REAL, "other_income" INTEGER, "interest" INTEGER, "depreciation" INTEGER, "profit_before_tax" INTEGER, "tax_percentage" REAL, "net_profit" INTEGER, "eps" REAL, "dividend_payout" REAL, "source_year" TEXT);

CREATE TABLE "profitandloss_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "year" TEXT,
  "sales" INTEGER,
  "expenses" INTEGER,
  "operating_profit" REAL,
  "opm_percentage" REAL,
  "other_income" INTEGER,
  "interest" INTEGER,
  "depreciation" INTEGER,
  "profit_before_tax" INTEGER,
  "tax_percentage" REAL,
  "net_profit" INTEGER,
  "eps" REAL,
  "dividend_payout" REAL,
  "source_year" TEXT
);

CREATE TABLE "prosandcons" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "pros" TEXT, "cons" TEXT);

CREATE TABLE "prosandcons_quarantine" (
"id" INTEGER,
  "company_id" TEXT,
  "pros" TEXT,
  "cons" TEXT
);

CREATE TABLE "sectors" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "broad_sector" TEXT, "sub_sector" TEXT, "index_weight_pct" REAL, "market_cap_category" TEXT);

CREATE TABLE "stock_prices" ("id" INTEGER PRIMARY KEY, "company_id" TEXT REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT, "date" TEXT, "open_price" REAL, "high_price" REAL, "low_price" REAL, "close_price" REAL, "volume" INTEGER, "adjusted_close" REAL);

CREATE INDEX "idx_analysis_company_id" ON "analysis"(company_id);

CREATE INDEX "idx_balancesheet_company_id" ON "balancesheet"(company_id);

CREATE INDEX "idx_balancesheet_year" ON "balancesheet"(year);

CREATE INDEX "idx_cashflow_company_id" ON "cashflow"(company_id);

CREATE INDEX "idx_cashflow_year" ON "cashflow"(year);

CREATE INDEX "idx_documents_company_id" ON "documents"(company_id);

CREATE INDEX "idx_documents_year" ON "documents"(year);

CREATE INDEX "idx_financial_ratios_company_id" ON "financial_ratios"(company_id);

CREATE INDEX "idx_financial_ratios_year" ON "financial_ratios"(year);

CREATE INDEX "idx_market_cap_company_id" ON "market_cap"(company_id);

CREATE INDEX "idx_market_cap_year" ON "market_cap"(year);

CREATE INDEX "idx_peer_groups_company_id" ON "peer_groups"(company_id);

CREATE INDEX "idx_profitandloss_company_id" ON "profitandloss"(company_id);

CREATE INDEX "idx_profitandloss_year" ON "profitandloss"(year);

CREATE INDEX "idx_prosandcons_company_id" ON "prosandcons"(company_id);

CREATE INDEX "idx_sectors_company_id" ON "sectors"(company_id);

CREATE INDEX "idx_stock_prices_company_id" ON "stock_prices"(company_id);
