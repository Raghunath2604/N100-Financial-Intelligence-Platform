-- 10 Sprint 1 exploratory queries
SELECT COUNT(*) AS companies FROM companies;
SELECT broad_sector, COUNT(*) AS companies FROM sectors GROUP BY broad_sector ORDER BY companies DESC;
SELECT COUNT(*) FROM profitandloss;
SELECT COUNT(*) FROM balancesheet;
SELECT COUNT(*) FROM cashflow;
SELECT company_id, COUNT(DISTINCT year) AS years FROM profitandloss GROUP BY company_id ORDER BY years;
SELECT company_id, COUNT(*) AS rows FROM stock_prices GROUP BY company_id ORDER BY rows DESC LIMIT 10;
SELECT peer_group_name, COUNT(*) AS members FROM peer_groups GROUP BY peer_group_name ORDER BY members DESC;
SELECT COUNT(*) FROM documents WHERE Annual_Report IS NULL OR TRIM(Annual_Report)='';
SELECT year, COUNT(*) AS records FROM market_cap GROUP BY year ORDER BY year;
